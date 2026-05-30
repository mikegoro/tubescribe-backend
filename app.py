import os
import re
from flask import Flask, request, jsonify, send_from_directory
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

# -----------------------------
# Extract YouTube ID
# -----------------------------
def extract_video_id(url):
    match = re.search(
        r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        url
    )
    return match.group(1) if match else None


# -----------------------------
# Optional: serve frontend (can remove if using Vercel)
# -----------------------------
@app.route('/')
def home():
    return jsonify({"status": "TubeScribe API running"})


# -----------------------------
# API
# -----------------------------
@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    url = request.args.get('url')

    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400

    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({"success": False, "error": "Invalid YouTube URL"}), 400

    try:
        # ✅ YOUR WORKING LOGIC (DO NOT CHANGE)
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)

        plain_text = " ".join([item.text for item in transcript])

        formatted_text = "\n".join([
            f"[{int(item.start//60):02d}:{int(item.start%60):02d}] {item.text}"
            for item in transcript
        ])

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
# Render entry point
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)