from flask import Flask, request, jsonify
import requests
import subprocess
import os

app = Flask(__name__)

@app.route('/process-video', methods=['POST'])
def process_video():
    data = request.json
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({"error": "video_url is required"}), 400

    try:
        # Step 1: Download video from URL
        r = requests.get(video_url, stream=True)
        r.raise_for_status()
        
        input_path = "input.mp4"
        with open(input_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Step 2: Crop video using ffmpeg
        # Adjust crop filter as per watermark size
        # Example: crop full width, height - 200 px, offset y = 100 px (crop 100px top & 100px bottom)
        output_path = "output_cropped.mp4"
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_path,
            "-filter:v", "crop=in_w:in_h-200:0:100",
            "-c:a", "copy",
            "-y",  # overwrite output file if exists
            output_path
        ]

        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": "ffmpeg failed", "details": result.stderr}), 500

        # Optional: You can upload output_path to S3 or other storage here and return that URL

        return jsonify({"message": "Video processed successfully", "output_file": output_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run on port 5000 for local testing
    app.run(host='0.0.0.0', port=5000)
