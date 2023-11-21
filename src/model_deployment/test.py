import base64
import json

# Read the video file as binary data
with open('sample_video.mp4', 'rb') as video_file:
    video_data = video_file.read()

# Encode the binary data to base64
encoded_video_data = base64.b64encode(video_data).decode('utf-8')

# Format the JSON in the way expected by the TorchServe custom handler
payload = {
    "instances": [
        {"data": {"b64": encoded_video_data}}
    ]
}

# Save the JSON payload to a file
with open('input_payload.json', 'w') as json_file:
    json.dump(payload, json_file)
