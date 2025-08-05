from flask import Flask, request, jsonify
import shutil
import os

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    video_name = request.json.get("video")
    video_path = f"/data/{video_name}"
    output_path = "/app/output"

    if not os.path.exists(video_path):
        return jsonify({"status": "error", "message": "Video not found"}), 404

    process_video(video_path, output_path)

    # Move video to processed folder
    processed_dir = "/data/processed_videos"
    os.makedirs(processed_dir, exist_ok=True)
    shutil.move(video_path, os.path.join(processed_dir, video_name))

    return jsonify({"status": "success", "message": f"Processed {video_name}"}), 200
