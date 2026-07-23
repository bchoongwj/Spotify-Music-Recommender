# Spotify Music Recommender

A side project I built to explore local LLM applications and the Spotify API.

Spotify Music Recommender is a playlist analysis application built with **Python**, **Streamlit**, **LangChain**, and **Ollama**. It accepts a public Spotify playlist URL and provides a detailed music taste profile along with personalised song recommendations, powered by a **locally hosted Large Language Model (LLM)**. Since inference runs locally through Ollama, no external AI APIs or API keys are required beyond Spotify.

---

## Features

* Analyse any **public Spotify playlist** via URL
* Automatically fetch track data and **artist genres** from the Spotify API
* AI-powered **music taste profiling** — genres, mood, recurring artists, and surprising patterns
* **10 personalised song recommendations** in a clean markdown table
* Runs LLM inference entirely on your own machine with **Ollama**

---

## Tech Stack

* Python
* Streamlit
* LangChain
* Ollama
* Spotipy

---

## Prerequisites

Before running the application, make sure you have installed:

* Python 3.13+
* Ollama
* uv
* A Spotify Developer account with a registered app

Install **uv**:
```bash
pip install uv
```

---

## Spotify Setup

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Under **Redirect URIs**, add: `http://127.0.0.1:9090`
4. Copy your **Client ID** and **Client Secret**
![Uploading image.png…]()


---

## Installation

### Clone the repository
```bash
git clone https://github.com/bchoongwj/Spotify-Music-Recommender.git
cd Spotify-Music-Recommender
```

### Set up environment variables
Create a `.env` file in the project root:
```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:9090
```

### Install dependencies
```bash
uv sync
```

### Download the LLM
```bash
ollama pull qwen3:4b
```

### Start Ollama
If Ollama isn't already running:
```bash
ollama serve
```

### Run the application
```bash
uv run python -m streamlit run main.py
(OR if not using uv: python -m streamlit run main.py)
```

The application will open automatically in your browser.

---

## Screenshots

*Coming soon.*

---

## Future Improvements

* Streaming LLM responses for faster perceived output
* Support for private playlists via Spotify OAuth
* Export analysis and recommendations to PDF
* Compare two playlists side by side
* Recommend Spotify-searchable tracks with direct links
* Support for multiple LLM models
* ATS-style scoring — rate how "mainstream" or "niche" your taste is

---

## License
MIT
This project is intended for learning and portfolio purposes.
