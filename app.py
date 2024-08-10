from IPython.display import display, Image, Audio, DisplayHandle
from flask import Flask, request, jsonify
import cv2  
import base64
from openai import OpenAI
import os
import tempfile
import sys

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", sys.argv[1]))


ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_video(frames):
    PROMPT_MESSAGES = [
    {
        "role": "user",
        "content": [
            "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video.",
            *map(lambda x: {"image": x, "resize": 768}, frames[0::50]),
        ],
    },
    ]
    params = {
    "model": "gpt-4o",
    "messages": PROMPT_MESSAGES,
    "max_tokens": 200,
    }

    result= client.chat.completions.create(**params)
    return result.choices[0].message.content

def voice_description(frames):
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "These are frames of a video. Create a short description of the video. Only include the narration.",
                *map(lambda x: {"image": x, "resize": 768}, frames[0::60]),
            ],
        },
    ]

    params = {
        "model": "gpt-4o",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 500,
    }

    result = client.chat.completions.create(**params)
    return result.choices[0].message.content


@app.route('/convert_video', methods=['POST'])
def convert_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video part in the request'}), 400

    video_file = request.files['video']

    if video_file.filename == '':
        return jsonify({'error': 'No video selected'}), 400

    if not allowed_file(video_file.filename):
        return jsonify({'error': 'Invalid file format'}), 400

    # Save video to temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        video_file.save(temp_file.name)

    # Convert video to frames
    video = cv2.VideoCapture(temp_file.name)
    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()

    video_result=process_video(base64Frames)
    voice_result=voice_description(base64Frames)



    cv2.destroyAllWindows()

    # Return success message or frame data
    return jsonify(
        {           'message': 'Video converted successfully',
                    'video_description':video_result,
                    'voice_result':voice_result
        })


if __name__ == '__main__':
    app.run(debug=True)


