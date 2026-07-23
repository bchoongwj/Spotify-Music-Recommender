# Run with this: uv run python -m streamlit run main.py

from collections import Counter
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os
import streamlit as st

load_dotenv()


# ── Page setup ────────────────────────────────────────────────────────────────

def setup_page():
    st.set_page_config(
        page_title="Spotify Song Recommender",
        page_icon="♪♫♪♬",
        layout="centered"
    )


def create_ui() -> str:
    st.title("Spotify Song Recommender")
    st.markdown("Upload a Spotify playlist URL to get song recommendations!")
    return st.text_input("Enter playlist URL:")


# ── Spotify helpers ───────────────────────────────────────────────────────────

# def connect_spotify() -> Spotify:
#     return Spotify(
#         auth_manager=SpotifyClientCredentials(
#             client_id=os.getenv("SPOTIPY_CLIENT_ID"),
#             client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
#         )
#     )

def connect_spotify() -> Spotify:
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="http://127.0.0.1:9090",
        scope="playlist-read-private playlist-read-collaborative",
        cache_path=".cache",
        open_browser=True
    )
    return Spotify(auth_manager=auth_manager)

def validate_url(playlist_url: str) -> bool:
    if not playlist_url:
        st.warning("Please enter a Spotify playlist URL.")
        return False
    if "open.spotify.com/playlist/" not in playlist_url:
        st.error("Invalid Spotify playlist URL.")
        return False
    return True


def get_playlist_id(playlist_url: str) -> str:
    return playlist_url.split("/")[-1].split("?")[0]


def load_playlist(sp: Spotify, playlist_id: str) -> dict | None:
    try:
        return sp.playlist(playlist_id)
    except Exception:
        st.error("Unable to load playlist. Please check the URL and permissions.")
        return None


def display_playlist_header(playlist: dict):
    if playlist["images"]:
        st.image(playlist["images"][0]["url"], width=250)
    st.subheader(f"{playlist['name']} - 👤 {playlist['owner']['display_name']}")


def fetch_tracks(sp: Spotify, playlist_id: str) -> list:
    tracks = []
    results = sp.playlist_items(playlist_id, additional_types=["track"])

    while True:
        for item in results["items"]:
            if item is None:
                continue
            track = item.get("item") or item.get("track")
            if track is None or track.get("id") is None:
                continue
            tracks.append(track)

        if results["next"]:
            results = sp.next(results)
        else:
            break

    return tracks


def fetch_artist_genres(sp: Spotify, tracks: list) -> dict:
    artist_genres = {}

    for track in tracks:
        for artist in track["artists"]:
            artist_id = artist["id"]
            if artist_id in artist_genres:
                continue
            artist_info = sp.artist(artist_id)
            artist_genres[artist_id] = {
                "name": artist_info["name"],
                "genres": artist_info.get("genres", [])
            }

    return artist_genres


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_playlist_text(tracks: list, artist_genres: dict) -> str:
    # Count artist appearances
    artist_counter = Counter()
    for track in tracks:
        for artist in track["artists"]:
            artist_counter[artist["name"]] += 1

    # Build concise track list — song name + primary artist + genres only
    lines = []
    for track in tracks:
        primary_artist = track["artists"][0]
        info = artist_genres[primary_artist["id"]]
        genres = ", ".join(info["genres"][:2]) or "Unknown"  # max 2 genres
        lines.append(f"{track['name']} by {info['name']} ({genres})")

    return "\n".join(lines)


def build_prompt(playlist_text: str, total_tracks: int) -> str:
    return f"""
You are an expert music recommendation system.

This playlist has {total_tracks} songs total. Here is the full track listing:

{playlist_text}

Your tasks — be concise, allow minimal filler words.
Use these exact markdown headers for each section:

### 🎵 Music Taste
3 sentences max.

### 🎸 Top Genres
List top 3 only with slight explanations.

### 👤 Recurring Artists
List top 5 with number of tracks by each artist.

### 🌙 Mood
2 sentences.

### 🎧 Best Situation
2 sentences.

### 💡 Surprising Pattern
2 sentences.

### 🎯 Recommended Songs
Recommendation rules:
- Maximum 2 songs per artist across all 10 recommendations.
- Cover at least 5 different artists.
- Include artists from outside my playlist, not just ones I already listen to.
- Prioritise variety over familiarity.
- For this section, only answer accordingly to the format below. No need to answer with extra information.

Format as a markdown table with these exact columns:
| # | Song | Artist | Why |

Do not recommend songs already in the playlist.
Answer as if you're not expecting a reply. Do not ask the user for further input.
There is no need to introduce yourself.
"""

# ── LLM ──────────────────────────────────────────────────────────────────────

def get_recommendations(prompt: str) -> str:
    llm = ChatOllama(model="qwen3:4b", temperature=0.7)
    response = llm.invoke([HumanMessage(prompt)])
    return response.content


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    setup_page()
    playlist_url = create_ui()
    analyze = st.button("Analyze Playlist")

    if not analyze:
        return

    status = st.empty()

    # Connect
    status.info("🔑 Connecting to Spotify...")
    sp = connect_spotify()

    # Validate
    status.info("📋 Loading playlist information...")
    if not validate_url(playlist_url):
        st.stop()

    playlist_id = get_playlist_id(playlist_url)
    playlist = load_playlist(sp, playlist_id)
    if playlist is None:
        st.stop()

    display_playlist_header(playlist)

    # Fetch tracks
    status.info("🎵 Pulling playlist songs...")
    tracks = fetch_tracks(sp, playlist_id)
    st.success(f"Loaded {len(tracks)} songs")

    if not tracks:
        st.warning("No tracks found. Make sure the playlist is public.")
        st.stop()

    # Fetch genres
    status.info("🎸 Fetching artist genres...")
    artist_genres = fetch_artist_genres(sp, tracks)

    # Build prompt
    status.info("🧠 Building music profile...")
    playlist_text = build_playlist_text(tracks, artist_genres)
    prompt = build_prompt(playlist_text, len(tracks))

    # Get recommendations
    status.info("🤖 Asking Ollama for recommendations...")
    with st.spinner("🤖 Analyzing your music taste (takes a couple of minutes)..."):
        result = get_recommendations(prompt)

    status.success("✅ Analysis complete!")
    st.markdown(result)


if __name__ == "__main__":
    main()