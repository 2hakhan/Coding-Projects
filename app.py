from flask import Flask, render_template, request
from project import get_playlist_tracks, get_spotify_client, get_image_mood, encode_image
import os
import uuid
import re
from pathlib import Path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

sp = get_spotify_client()

@app.route("/", methods=["GET", "POST"])
def home():
    mood = None
    songs = []
    image_url = None
    
    if request.method == "POST":
        file = request.files["image"] # picture is stored in "image", this line grabs it from html form under "image"
        if file: 
            filename = f"{uuid.uuid4().hex}.jpg"

            upload_folder = Path(app.config["UPLOAD_FOLDER"])
            upload_folder.mkdir(parents=True, exist_ok=True)
            path = upload_folder / filename

            file.save(path)  

            image_url = f"/{path.as_posix()}" 

            base64_img = encode_image(path)
            mood = get_image_mood(base64_img)
            mood = re.sub(r"[^\w\s]", "", mood).strip().lower()
            mood = " ".join(sorted(mood.split()))

            songs = get_playlist_tracks(sp, mood)
            
    return render_template("index.html", mood=mood, name="Tuaha", songs=songs, image_url=image_url)

@app.route("/about")
def about():
    return render_template("about.html", name="Tuaha")

if __name__ == "__main__":
    app.run(debug=True)