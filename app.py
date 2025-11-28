# app.py → FINAL VERSION (NO LAG + PERFECT gTTS AUDIO)
from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from backend.chat_handler import ChatEngine
from backend.response_logic import build_system_prompt
from backend.tts import generate_tts_url
import os

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

# ==================== MediaPipe Setup (Optimized) ====================
model_path = 'brain.task'
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
recognizer = GestureRecognizer.create_from_options(options)

# ==================== Webcam Setup ====================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
time.sleep(1)

start_time = time.time()
current_gesture = "None"
last_process_time = 0
PROCESS_INTERVAL = 0.05  # 20 FPS processing


def gen_frames():
    global current_gesture, last_process_time
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)
        now = time.time()

        if now - last_process_time >= PROCESS_INTERVAL:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int((now - start_time) * 1000)
            result = recognizer.recognize_for_video(mp_image, timestamp_ms)

            current_gesture = result.gestures[0][0].category_name if result.gestures else "None"
            last_process_time = now

        cv2.putText(frame, current_gesture, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 180, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/gesture')
def gesture():
    return jsonify({'gesture': current_gesture})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    tts_enabled = data.get('tts', False)

    system_prompt = build_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg}
    ]

    chat_engine = ChatEngine()
    bot_reply = chat_engine.query(messages)

    audio_url = None
    if tts_enabled:
        audio_url = generate_tts_url(bot_reply)

    return jsonify({
        'response': bot_reply,
        'audio_url': audio_url
    })


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=False, threaded=True, use_reloader=False)