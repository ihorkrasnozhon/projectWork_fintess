from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import math

app = Flask(__name__)

# Инициализация Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Глобальные переменные
counter = 0  # Счётчик
stage = None  # Стадия (вверх или вниз)

# Функция для вычисления угла
def calculate_angle(a, b, c):
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Генерация кадров с камеры
def gen_frames_squat(source='camera', video_path=None):
    global counter, stage
    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        h, w, _ = image.shape

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Получаем координаты суставов
            def get_joint_coords(landmark_enum):
                lm = landmarks[landmark_enum.value]
                return [lm.x, lm.y] if lm.visibility > 0.5 else None

            # Обрабатываем позу для приседания
            def process_squat():
                global counter, stage

                hip = get_joint_coords(mp_pose.PoseLandmark.LEFT_HIP)
                knee = get_joint_coords(mp_pose.PoseLandmark.LEFT_KNEE)
                ankle = get_joint_coords(mp_pose.PoseLandmark.LEFT_ANKLE)

                if hip and knee and ankle:
                    angle = calculate_angle(hip, knee, ankle)

                    if angle is not None:
                        # Логика подсчета приседаний
                        if angle > 160:
                            stage = "up"
                        if angle < 90 and stage == "up":
                            stage = "down"
                            counter += 1

                        # Рисуем точки и линии
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
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Основная страница
@app.route('/')
def index():
    return render_template('index.html')

# Видео поток
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames_squat(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
