from flask import Flask, jsonify, request
import json
import time
from main import full_song_dict  # Import your existing song dictionary here

app = Flask(__name__)


# Route to get the song dictionary
@app.route("/songs", methods=["GET"])
def get_songs():
    return jsonify(full_song_dict)


# Route to search for songs by name or artist
@app.route("/search", methods=["GET"])
def search_songs():
    query = request.args.get("query", "").lower()  # The query input by user
    include = request.args.get("include", "").lower()
    exclude = request.args.get("exclude", "").lower()

    result = []

    for url, songs in full_song_dict.items():
        for song in songs[1:]:  # Skip the title
            title, artist = song
            if (include in title.lower() or include in artist.lower()) and (
                exclude not in title.lower() and exclude not in artist.lower()
            ):
                result.append({"url": url, "title": title, "artist": artist})

    return jsonify(result)


# # Route to trigger the script to update song dictionary
# @app.route('/update', methods=['POST'])
# def update_songs():
#     # Your logic to update the song_dict, e.g., rerun the script
#     # For example:
#     # song_dict = update_song_dict()
#
#     return jsonify({'message': 'Song dictionary updated!'})

if __name__ == "__main__":
    app.run(debug=True)
