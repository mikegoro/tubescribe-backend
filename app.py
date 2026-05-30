import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)
CORS(app)

# -----------------------------
# Extract YouTube Video ID
# -----------------------------
def extract_video_id(url):
    match = re.search(
        r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        url
    )
    return match.group(1) if match else None


# -----------------------------
# Health Check Route
# -----------------------------
@app.route('/')
def home():
    return jsonify({
        "status": "TubeScribe API is running"
    })


# -----------------------------
# Main API Route
# -----------------------------
@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    url = request.args.get('url')

    if not url:
        return jsonify({
            "success": False,
            "error": "URL is required"
        }), 400

    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({
            "success": False,
            "error": "Invalid YouTube URL"
        }), 400

    try:
        # ✅ FIX: correct method for youtube-transcript-api v1.2.4
        transcript = YouTubeTranscriptApi.fetch(video_id)

        # Plain text
        plain_text = " ".join([item.text for item in transcript])

        # Timestamped text
        formatted_list = []
        for item in transcript:
            start = getattr(item, "start", 0)
            mins, secs = divmod(int(start), 60)
            formatted_list.append(f"[{mins:02d}:{secs:02d}] {item.text}")

        formatted_text = "\n".join(formatted_list)

        return jsonify({
            "success": True,
            "plain_text": plain_text,
            "formatted_text": formatted_text,
            "video_id": video_id
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"YouTube Error: {str(e)}"
        }), 400


# -----------------------------
# Render Entry Point
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)