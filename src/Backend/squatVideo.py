import cv2
import mediapipe as mp
import math
from flask import Flask, render_template, Response, request
import os

app = Flask(__name__)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Глобальные переменные счётчика и стадии
counter = 0
stage = None

def calculate_angle(a, b, c):
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def gen_frames_squat_video(video_path):
    global counter, stage

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Не удалось открыть видео: {video_path}")
        return

    last_frame_bytes = None

    while True:
        success, frame = cap.read()
        if not success:
            # Если видео закончилось, отдаем последний кадр бесконечно
            if last_frame_bytes is not None:
                while True:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + last_frame_bytes + b'\r\n')
            break

        h, w, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            def get_joint_coords(landmark_enum):
                lm = landmarks[landmark_enum.value]
                return [lm.x, lm.y] if lm.visibility > 0.5 else None

            def process_squat():
                global counter, stage
                hip = get_joint_coords(mp_pose.PoseLandmark.LEFT_HIP)
                knee = get_joint_coords(mp_pose.PoseLandmark.LEFT_KNEE)
                ankle = get_joint_coords(mp_pose.PoseLandmark.LEFT_ANKLE)

                if hip and knee and ankle:
                    angle = calculate_angle(hip, knee, ankle)

                    if angle is not None:
                        if angle > 160:
                            if stage == "down":
                                stage = "up"
                                counter += 1
                        elif angle < 90:
                            if stage == "up" or stage is None:
                                stage = "down"

                        hip_px = (int(hip[0] * w), int(hip[1] * h))
                        knee_px = (int(knee[0] * w), int(knee[1] * h))
                        ankle_px = (int(ankle[0] * w), int(ankle[1] * h))

                        cv2.circle(image, hip_px, 10, (0, 0, 255), -1)
                        cv2.circle(image, knee_px, 10, (0, 255, 0), -1)
                        cv2.circle(image, ankle_px, 10, (0, 255, 255), -1)
                        cv2.line(image, hip_px, knee_px, (255, 0, 0), 3)
                        cv2.line(image, knee_px, ankle_px, (255, 0, 0), 3)

            process_squat()

            cv2.putText(image, f'Count: {counter}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        ret, buffer = cv2.imencode('.jpg', image)
        frame_bytes = buffer.tobytes()
        last_frame_bytes = frame_bytes

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

# Роут для загрузки видео потока с подсчетом приседаний
@app.route('/video_feed_squat')
def video_feed_squat():
    video_filename = request.args.get('video_path')
    if not video_filename:
        return "No video file specified", 400

    UPLOAD_FOLDER = "path_to_your_videos_folder"  # Укажи путь к папке с видео
    full_path = os.path.join(UPLOAD_FOLDER, video_filename)

    if not os.path.exists(full_path):
        return f"File not found: {full_path}", 404

    return Response(gen_frames_squat_video(full_path),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
