import os
import subprocess


from flask import Flask, Response, jsonify, request, render_template, send_from_directory
import cv2
from werkzeug.utils import secure_filename

from src.Backend.armBending import gen_frames_armbending
from src.Backend.pushUps import gen_frames_pushups
from src.Backend.squat import gen_frames_squat

from src.Backend.squatVideo import gen_frames_squat_video  # Импортируем новую функцию




app = Flask(__name__)

# Глобальные переменные
is_camera_active = False
cap = None
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')


# ================== РУЧНАЯ НАСТРОЙКА CORS ==================
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # или 'http://localhost:3000' для ограничения
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Обработка preflight-запросов OPTIONS (если надо)
# @app.route('/stop_video', methods=['OPTIONS'])
# def handle_options():
#     response = jsonify({'status': 'ok'})
#     return add_cors_headers(response)
# ===========================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    source = request.args.get('source', 'camera')  # 'camera' или 'video'
    video_path = request.args.get('video_path', None)
    exercise = request.args.get('exercise', 'armbend')  # по умолчанию armbend

    if exercise == 'armbend':
        return Response(gen_frames_armbending(source, video_path),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'pushups':
        return Response(gen_frames_pushups(source, video_path),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'squats':
        return Response(gen_frames_squat(source, video_path),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Exercise not supported", 400

@app.route('/stop_video')
def stop_video():
    from src.Backend import camera_state
    camera_state.is_camera_active = False
    if camera_state.cap:
        camera_state.cap.release()
        camera_state.cap = None
    return 'Video stopped'
#
# @app.route('/video_feed_video')
# def video_feed_video():
#     video_path = request.args.get('video_path')
#
#     if not video_path:
#         return "No video path provided", 400
#
#     # Убираем "/uploads/" из URL и собираем абсолютный путь
#     filename = os.path.basename(video_path)
#     full_path = os.path.join(UPLOAD_FOLDER, filename)
#
#     if not os.path.exists(full_path):
#         return f"Файл не найден: {full_path}", 404
#
#     # Возвращаем поток кадров (предположим, у тебя есть функция gen_frames)
#     return Response(gen_frames(full_path), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_video')
def video_feed_video():
    video_filename = request.args.get('video_path')
    exercise = request.args.get('exercise', 'armbend')

    if not video_filename:
        return "No video file specified", 400

    # Полный путь к видео
    full_path = os.path.join(UPLOAD_FOLDER, video_filename)
    if not os.path.exists(full_path):
        return f"File not found: {full_path}", 404

    if exercise == 'armbend':
        return Response(gen_frames_armbending(source='video', video_path=full_path),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'pushups':
        return Response(gen_frames_pushups(source='video', video_path=full_path),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'squats':
        return Response(gen_frames_squat(source='video', video_path=full_path),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'squat_counter':  # Новый кейс
        return Response(gen_frames_squat_video(full_path),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Exercise not supported", 400


@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video part'}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Создаем папку uploads, если её нет
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    filename = secure_filename(video.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    video.save(save_path)

    # Возвращаем имя файла для потоковой передачи
    return jsonify({
        'video_path': filename,  # Только имя файла, не полный путь
        'message': 'Video uploaded successfully'
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/start_exercise/<exercise_name>', methods=['GET'])
def start_exercise(exercise_name):
    if exercise_name == 'armbend':
        # Здесь можно инициализировать логику сгибания рук, если нужно
        return jsonify({'status': 'started', 'exercise': 'armbend'})
    elif exercise_name == 'squat':
        # Аналогично для "squat", если реализовано
        return jsonify({'status': 'started', 'exercise': 'squat'})
    elif exercise_name == 'pushups':
        # Аналогично для "pushups", если реализовано
        return jsonify({'status': 'started', 'exercise': 'pushups'})
    else:
        return jsonify({'error': 'Unknown exercise'}), 400



if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
