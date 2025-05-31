import cv2
import mediapipe as mp
import math
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def get_joint_coords(landmark_enum, landmarks, w, h):
    try:
        landmark = landmarks[landmark_enum.value]
        return int(landmark.x * w), int(landmark.y * h), landmark.visibility
    except:
        return None, None, 0

def calculate_angle(a, b, c):
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def gen_frames_pushups(video_path):
    counter = 0
    stage = None

    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            # Повторное воспроизведение видео
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        h, w, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

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

            visible_right = all([right_shoulder[2] > 0.6, right_elbow[2] > 0.6, right_wrist[2] > 0.6])
            visible_left = all([left_shoulder[2] > 0.6, left_elbow[2] > 0.6, left_wrist[2] > 0.6])

            if visible_right and visible_left:
                shoulder_line_y = (right_shoulder[1] + left_shoulder[1]) / 2
                elbow_line_y = (right_elbow[1] + left_elbow[1]) / 2

                if abs(shoulder_line_y - elbow_line_y) < 15:
                    stage = "down"
                else:
                    if stage == "down":  # Только при переходе с down на up считаем
                        counter += 1
                        print(f"Push-ups count: {counter}")
                    stage = "up"

                cv2.line(frame, (right_shoulder[0], right_shoulder[1]),
                         (right_elbow[0], right_elbow[1]), (0, 255, 0), 3)
                cv2.line(frame, (left_shoulder[0], left_shoulder[1]),
                         (left_elbow[0], left_elbow[1]), (0, 0, 255), 3)

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

            else:
                cv2.putText(frame, "No visible arm!", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.putText(frame, f'Count: {counter}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break
        frame_bytes = buffer.tobytes()

        yield frame_bytes

    cap.release()

def analyze_video_pushups(video_path):
    """
    Анализирует видео с отжиманиями и показывает результат с подсчетом.
    """
    frame_generator = gen_frames_pushups(video_path)

    for frame_bytes in frame_generator:
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        cv2.imshow('Push-up Analysis (Video)', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    video_path = 'path_to_your_video.mp4'  # Замените на путь к вашему видео
    analyze_video_pushups(video_path)
