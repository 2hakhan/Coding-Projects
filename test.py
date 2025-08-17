import requests

def get_recommendations():
    url = "https://api.reccobeats.com/v1/track/recommendation"
    params = {
        
        "seeds": ["22mek4IiqubGD9ctzxc69s", "29I9dv9Nq704w0Oc5yFGsR", "787Y2idwCU2Rk60Prv4wpr", "46N3FCKFABRjNoNBVq4osr", ""],  # Gods plan by drake
        "size": 1,

        # Feature filters (EDM profile)
        "valence": 0.7,         # Moderately upbeat, not too happy
        "energy": 0.7,          # High energy
        "danceability": 0.85,   # Very danceable
        "acousticness": 0.1,    # Mostly synthetic
        "instrumentalness": 0.1,  # Some instrumental parts but not fully instrumental
        "tempo": 122,           # Typical house tempo (118–125 BPM)
        "speechiness": 0.2,    # Not rap or speech-heavy
        "liveness": 0,        # Studio tracks

        # Optional
        "popularity": 80,       # Prioritize moderately popular
        "featureWeight": 4      # Strong match to these features
    }

    response = requests.get(url, params=params)
    
    if response.ok:
        data = response.json()
        print("🎵 Recommended Songs:")
        for track in data.get("content", []):
            name = track["trackTitle"]
            artist = track["artists"][0]["name"]
            link = track["href"]
            print(f"→ {name} by {artist}: {link}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

# Run it
if __name__ == "__main__":
    get_recommendations()
