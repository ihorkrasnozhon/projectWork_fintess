import time
import cv2
import mediapipe as mp
import math
from src.Backend import camera_state

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def get_joint_coords(landmark_enum, landmarks, w, h):
    try:
        landmark = landmarks[landmark_enum.value]
        return int(landmark.x * w), int(landmark.y * h), landmark.visibility
    except:
        return None, None, 0

def gen_frames_pushups(source='camera', video_path=None):
    counter = 0
    stage = None

    if source == 'camera':
        camera_state.cap = cv2.VideoCapture(0)
    elif source == 'video' and video_path:
        camera_state.cap = cv2.VideoCapture(video_path)
    else:
        return

    camera_state.is_camera_active = True

    while camera_state.is_camera_active:
        if not camera_state.cap or not camera_state.cap.isOpened():
            break

        success, frame = camera_state.cap.read()
        if not success:
            camera_state.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        h, w, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Получаем координаты и видимость ключевых точек
            right_shoulder, right_elbow, right_wrist = (
                get_joint_coords(mp_pose.PoseLandmark.RIGHT_SHOULDER, landmarks, w, h),
                get_joint_coords(mp_pose.PoseLandmark.RIGHT_ELBOW, landmarks, w, h),
                get_joint_coords(mp_pose.PoseLandmark.RIGHT_WRIST, landmarks, w, h),
            )
            left_shoulder, left_elbow, left_wrist = (
                get_joint_coords(mp_pose.PoseLandmark.LEFT_SHOULDER, landmarks, w, h),
                get_joint_coords(mp_pose.PoseLandmark.LEFT_ELBOW, landmarks, w, h),
                get_joint_coords(mp_pose.PoseLandmark.LEFT_WRIST, landmarks, w, h),
            )

            # Проверяем видимость
            visible_right = all([right_shoulder[2] > 0.6, right_elbow[2] > 0.6, right_wrist[2] > 0.6])
            visible_left = all([left_shoulder[2] > 0.6, left_elbow[2] > 0.6, left_wrist[2] > 0.6])

            # Если видны обе стороны
            if visible_right and visible_left:
                shoulder_line_y = (right_shoulder[1] + left_shoulder[1]) / 2
                elbow_line_y = (right_elbow[1] + left_elbow[1]) / 2

                if abs(shoulder_line_y - elbow_line_y) < 15:  # 15 пикселей - допустимая разница
                    if stage != "down":
                        stage = "down"
                        counter += 1
                        print(f"Push-ups count: {counter}")
                else:
                    stage = "up"

                # Отрисовка линий
                cv2.line(frame, (right_shoulder[0], right_shoulder[1]),
                         (right_elbow[0], right_elbow[1]), (0, 255, 0), 3)
                cv2.line(frame, (left_shoulder[0], left_shoulder[1]),
                         (left_elbow[0], left_elbow[1]), (0, 0, 255), 3)

            # Если видна только правая сторона
            elif visible_right:
                angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                if angle < 45:
                    stage = "down"
                if angle > 160 and stage == "down":
                    stage = "up"
                    counter += 1
                    print(f"Push-ups count: {counter}")

                color = (0, 255, 0)
                cv2.line(frame, (right_shoulder[0], right_shoulder[1]),
                         (right_elbow[0], right_elbow[1]), color, 3)
                cv2.line(frame, (right_elbow[0], right_elbow[1]),
                         (right_wrist[0], right_wrist[1]), color, 3)

            # Если видна только левая сторона
            elif visible_left:
                angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                if angle < 45:
                    stage = "down"
                if angle > 160 and stage == "down":
                    stage = "up"
                    counter += 1
                    print(f"Push-ups count: {counter}")

                color = (0, 0, 255)
                cv2.line(frame, (left_shoulder[0], left_shoulder[1]),
                         (left_elbow[0], left_elbow[1]), color, 3)
                cv2.line(frame, (left_elbow[0], left_elbow[1]),
                         (left_wrist[0], left_wrist[1]), color, 3)

            # Если не видно никого
            else:
                cv2.putText(frame, "No visible arm!", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.putText(frame, f'Count: {counter}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    if camera_state.cap is not None:
        camera_state.cap.release()
        camera_state.cap = None

def calculate_angle(a, b, c):
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle
