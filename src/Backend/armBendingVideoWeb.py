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
            cv2.circle(frame, shoulder, 10, color, -1)
            cv2.circle(frame, elbow, 10, color, -1)
            cv2.circle(frame, wrist, 10, color, -1)
            cv2.line(frame, shoulder, elbow, color, 3)
            cv2.line(frame, elbow, wrist, color, 3)

def gen_frames(video_path):
    global counter
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Не удалось открыть видео: {video_path}")
        return

    last_frame_bytes = None  # сюда будем сохранять последний кадр


    while True:
        success, frame = cap.read()
        if not success:
            if last_frame_bytes is not None:
                while True:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + last_frame_bytes + b'\r\n')
            else:
                break

        h, w, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            process_arm("LEFT", landmarks, w, h, frame)
            process_arm("RIGHT", landmarks, w, h, frame)

            # Отображаем счётчик
            cv2.putText(frame, f'Count: {counter}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

        # Кодируем кадр в JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        last_frame_bytes = frame_bytes

        # Возвращаем кадр в формате MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
