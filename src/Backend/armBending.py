import time

import cv2
import mediapipe as mp
import math
from src.Backend import camera_state

# Инициализация mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Глобальные переменные
counter = 0
stage = None
is_camera_active = False  # или False — по умолчанию
cap = None

def calculate_angle(a, b, c):
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def get_joint_coords(landmark_enum, landmarks, w, h):
    try:
        landmark = landmarks[landmark_enum.value]
        return int(landmark.x * w), int(landmark.y * h)
    except:
        return None

def process_arm(side, landmarks, w, h, frame):
    global counter, stage

    shoulder = get_joint_coords(getattr(mp_pose.PoseLandmark, f"{side}_SHOULDER"), landmarks, w, h)
    elbow = get_joint_coords(getattr(mp_pose.PoseLandmark, f"{side}_ELBOW"), landmarks, w, h)
    wrist = get_joint_coords(getattr(mp_pose.PoseLandmark, f"{side}_WRIST"), landmarks, w, h)

    if shoulder and elbow and wrist:
        angle = calculate_angle(shoulder, elbow, wrist)

        if angle is not None:
            if angle < 45:
                stage = f"{side}_down"
            if angle > 160 and stage == f"{side}_down":
                stage = f"{side}_up"
                counter += 1

            color = (0, 0, 255) if side == "LEFT" else (0, 255, 0)

            # Точки
            cv2.circle(frame, shoulder, 10, color, -1)
            cv2.circle(frame, elbow, 10, color, -1)
            cv2.circle(frame, wrist, 10, color, -1)

            # Линии
            cv2.line(frame, shoulder, elbow, color, 3)
            cv2.line(frame, elbow, wrist, color, 3)

def gen_frames_armbending(source='camera', video_path=None):
    from src.Backend import camera_state
    import cv2
    import mediapipe as mp
    import math

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    counter = 0
    stage = None

    def calculate_angle(a, b, c):
        radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
        angle = abs(radians * 180.0 / math.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def get_joint_coords(landmark_enum, landmarks, w, h):
        try:
            landmark = landmarks[landmark_enum.value]
            return int(landmark.x * w), int(landmark.y * h)
        except:
            return None

    def process_arm(side, landmarks, w, h, frame):
        nonlocal counter, stage

        shoulder = get_joint_coords(getattr(mp_pose.PoseLandmark, f"{side}_SHOULDER"), landmarks, w, h)
        elbow = get_joint_coords(getattr(mp_pose.PoseLandmark, f"{side}_ELBOW"), landmarks, w, h)
        wrist = get_joint_coords(getattr(mp_pose.PoseLandmark, f"{side}_WRIST"), landmarks, w, h)

        if shoulder and elbow and wrist:
            angle = calculate_angle(shoulder, elbow, wrist)

            if angle is not None:
                if angle < 45:
                    stage = f"{side}_down"
                if angle > 160 and stage == f"{side}_down":
                    stage = f"{side}_up"
                    counter += 1

                color = (0, 0, 255) if side == "LEFT" else (0, 255, 0)
                cv2.circle(frame, shoulder, 10, color, -1)
                cv2.circle(frame, elbow, 10, color, -1)
                cv2.circle(frame, wrist, 10, color, -1)
                cv2.line(frame, shoulder, elbow, color, 3)
                cv2.line(frame, elbow, wrist, color, 3)

    # Выбор источника
    if source == 'camera':
        camera_state.cap = cv2.VideoCapture(0)
    elif source == 'video' and video_path:
        camera_state.cap = cv2.VideoCapture(video_path)
    else:
        return  # ничего не делаем, если источник некорректный

    camera_state.is_camera_active = True

    while camera_state.is_camera_active:
        if not camera_state.cap or not camera_state.cap.isOpened():
            break  # Если камера не открыта, выходим из цикла

        success, frame = camera_state.cap.read()
        if not success:
            # если видео закончилось — вернуться в начало
            camera_state.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        h, w, _ = frame.shape

        # Mediapipe обработка
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            process_arm("LEFT", landmarks, w, h, frame)
            process_arm("RIGHT", landmarks, w, h, frame)

            cv2.putText(frame, f'Count: {counter}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    # Очистка
    if camera_state.cap is not None:
        camera_state.cap.release()
        camera_state.cap = None  # Окончательно обнуляем ссылку на камеру

# Запуск захвата видео
if __name__ == "__main__":
    gen_frames_armbending()  # Эта функция будет вызываться сервером Flask для трансляции видеопотока