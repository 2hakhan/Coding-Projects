import base64 
import os
import openai
import spotipy
import requests
import re
import random
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def get_spotify_client():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = "http://127.0.0.1:8080/callback"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-read-private user-read-email user-library-read playlist-read-private",  # enables audio_features
        cache_path=".cache"  # stores token between runs
    ))
    return sp

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded

client = OpenAI(api_key=api_key)

def get_image_mood(base64_image):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "What is the emotional mood or vibe of this image? "
                            "Choose up to two words from this list that best describe it, and return them as a single string: "
                            "happy, sad, nostalgic, romantic, calm, energetic, lonely, dreamy."
                            "For example: 'happy nostalgic', 'sad lonely', or just 'calm'. "
                            "Only return the mood phrase — no explanation."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
                
            }
        ],
        max_tokens=50,
    )
    
    return response.choices[0].message.content.strip()

MOOD_FEATURES = {
 
    "calm": {
        "valence": 0.5,
        "energy": 0.3,
        "acousticness": 0.8
    },
    "dreamy": {
        "valence": 0.6,
        "energy": 0.3,
        "acousticness": 0.8
    },
    "energetic": {
        "valence": 0.8,
        "energy": 0.9,
        "acousticness": 0.2
    },
    "happy": {
        "valence": 0.9,
        "energy": 0.7,
        "acousticness": 0.3
    },
    "lonely": {
        "valence": 0.2,
        "energy": 0.3,
        "acousticness": 0.7
    },
    "nostalgic": {
        "valence": 0.5,
        "energy": 0.4,
        "acousticness": 0.6
    },
    "romantic": {
        "valence": 0.7,
        "energy": 0.5,
        "acousticness": 0.6
    },
    "sad": {
        "valence": 0.2,
        "energy": 0.4,
        "acousticness": 0.7
    },

    # Two-word sorted moods
    "calm dreamy": {
        "valence": 0.5,
        "energy": 0.3,
        "acousticness": 0.8
    },
    "calm romantic": {
        "valence": 0.6,
        "energy": 0.4,
        "acousticness": 0.7
    },
    "dreamy happy": {
        "valence": 0.8,
        "energy": 0.5,
        "acousticness": 0.6
    },
    "dreamy sad": {
        "valence": 0.3,
        "energy": 0.3,
        "acousticness": 0.8
    },
    "energetic happy": {
        "valence": 0.9,
        "energy": 0.85,
        "acousticness": 0.3
    },
    "energetic romantic": {
        "valence": 0.8,
        "energy": 0.8,
        "acousticness": 0.3
    },
    "happy nostalgic": {
        "valence": 0.7,
        "energy": 0.5,
        "acousticness": 0.4
    },
    "happy romantic": {
        "valence": 0.8,
        "energy": 0.5,
        "acousticness": 0.5
    },
    "lonely nostalgic": {
        "valence": 0.2,
        "energy": 0.3,
        "acousticness": 0.7
    },
    "lonely sad": {
        "valence": 0.2,
        "energy": 0.3,
        "acousticness": 0.75
    },
    "nostalgic sad": {
        "valence": 0.2,
        "energy": 0.3,
        "acousticness": 0.6
    },
    "romantic sad": {
        "valence": 0.3,
        "energy": 0.4,
        "acousticness": 0.7
    }
}

def get_playlist_tracks(sp, mood):

    mood_playlists = {
        "happy": ["6sdu762jS8figBTAXXmJ6s"],
        "sad": ["3YUfKnn0V71fj8FNY1e2nk", "0Aiv1pOU9oXeom4PsPjV4h"],
        "happy romantic": ["2iyUq00DBCnYVjpYzwwf1N", "16n4NT7tVA5JAhzHhwEJ9O"],
        "sad romantic": ["2laqVXC6LVoYfu1edRp94Z", "3uCtO9BKor0vLqXQ2i6QwV"],
        "energetic": ["7bu7BZEusLNJSaAuUUZBKn", "7bnEC1e3dYrS5vxi8Xqu8G"],
        "energetic happy": ["7bu7BZEusLNJSaAuUUZBKn", "7bnEC1e3dYrS5vxi8Xqu8G"],
        "lonely": ["6PNwxLmnru6eGQBK4Y266M"],
        "lonely sad": ["6PNwxLmnru6eGQBK4Y266M", "5VRZx2foYKeCd0sWcbBk16"],
        "dreamy sad": ["6PNwxLmnru6eGQBK4Y266M", "5VRZx2foYKeCd0sWcbBk16"],
        "calm": ["66GHeZReUuM85dXWYtUDUD"],
        "calm dreamy": ["66GHeZReUuM85dXWYtUDUD"],
        "calm romantic": ["6D3FARsYIOlrVxfgoMdb0P"],
        "dreamy happy": ["2MjN2IuSoypJzjd0OerRt9"],
        "calm happy": ["6aK87NdugXYssQGHjKu1j9"],
        "energetic romantic": ["7haaEUXo4v2yvOmrb1unkY"]
        
    }
    
    if mood not in mood_playlists:
        print(f"No playlist mapped for mood: {mood}")
        return []
    
    all_tracks = []
    for pid in mood_playlists[mood]:
        print(f"getting up to 100 tracks from playlist {pid}")
        results = sp.playlist_tracks(pid, limit=100)
        all_tracks.extend(results["items"])
    
    if not all_tracks:
        print(" No tracks found.")
        return []
    
    chosen = random.sample(all_tracks, min(3, len(all_tracks)))
    recommended_songs = []
    for i, item in enumerate(chosen):
        track_info = item["track"]
        name = track_info["name"]
        artist = track_info["artists"][0]["name"]
        url = track_info["external_urls"]["spotify"]
        recommended_songs.append({
            "title": name,
            "artist": artist,
            "url": url
        })
    
    return recommended_songs

def filter_tracks(sp, tracks, mood):
    if mood not in MOOD_FEATURES:
        print(f"No mood features defined for: {mood}")
        return []
    print(f"[🔍] Filtering {len(tracks)} tracks for mood: '{mood}'")

    track_ids = [track["id"] for track in tracks if track.get("id")]
    print(f"[🧠] Found {len(track_ids)} track IDs with valid metadata")
    
    if not track_ids:
        return []
    
    features = []
    for i, track_id in enumerate(track_ids):
        url = f"https://api.reccobeats.com/audio-features?id={track_id}"
        print(f"[📦] Fetching audio features for track {i+1}/{len(track_ids)}")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("audio_features"):
                    features.append((track_id, data["audio_features"]))
                else:
                    print(f"[⚠️] No features found for {track_id}")
            else:
                print(f"Failed to fetch for {track_id}: {response.status_code}")
        except Exception as e:
            print(f"Exception while fetching for {track_id}: {e}")

    target = MOOD_FEATURES[mood]
    scored = []
    for track in tracks:
        tid = track.get("id")
        feat_entry = next((f for f in features if f[0] == tid), None)
        if not feat_entry:
            continue
        feat = feat_entry[1]
        score = (
            abs(feat["valence"] - target["valence"]) +
            abs(feat["energy"] - target["energy"]) +
            abs(feat["acousticness"] - target["acousticness"])
        )
        scored.append((score, track))

    scored.sort(key=lambda x: x[0])
    top_tracks = [track for _, track in scored[:3]]

    return [
        f"{t['name']} by {t['artists'][0]['name']}: {t['external_urls']['spotify']}"
        for t in top_tracks
    ]

def get_reccobeats_recommendations(valence, energy, acousticness, limit=3):
    url = f"https://api.reccobeats.com/audio-features/similar"
    params = {
        "valence": valence,
        "energy": energy,
        "acousticness": acousticness,
        "limit": limit
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["data"]

if __name__ == "__main__":
    sp = get_spotify_client()
    image_path = "test.jpg"
    encoded_image = encode_image(image_path)
    mood = get_image_mood(encoded_image)
    mood = re.sub(r"[^\w\s]", "", mood).strip().lower()
    mood = " ".join(sorted(mood.split()))

    print("Mood of image:\n", mood)