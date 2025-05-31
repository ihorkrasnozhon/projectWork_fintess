import cv2
import mediapipe as mp
import math

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

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

def process_arm(side, landmarks, w, h, frame, counter_stage):
    counter, stage = counter_stage

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

    return counter, stage

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

def process_arm(side, landmarks, w, h, frame, counter_stage):
    counter, stage = counter_stage

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

    return counter, stage

def gen_frames(source='camera', video_path=None):
    print(f"Starting gen_frames with source={source}, video_path={video_path}")
    if source == 'camera':
        cap = cv2.VideoCapture(0)
    elif source == 'video' and video_path:
        cap = cv2.VideoCapture(video_path)
    else:
        print("Invalid source or missing video_path")
        return

    if not cap.isOpened():
        print(f"Failed to open video source: {source} with path: {video_path}")
        return

    counter = 0
    stage = None

    while True:
        success, frame = cap.read()
        if not success:
            print("Frame read failed or video ended.")
            break

        h, w, _ = frame.shape
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        frame = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            counter, stage = process_arm("LEFT", landmarks, w, h, frame, (counter, stage))
            counter, stage = process_arm("RIGHT", landmarks, w, h, frame, (counter, stage))

            cv2.putText(frame, f'Count: {counter}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
    print("Video capture released")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Использование: python script.py путь_к_видео путь_для_выходного_файла")
        sys.exit(1)

    video_path = sys.argv[1]
    output_path = sys.argv[2]
    gen_frames(video_path, output_path)
