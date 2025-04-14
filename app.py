from flask import Flask, render_template, Response
import subprocess
from src.Backend.armBending import gen_frames


app = Flask(__name__)

# Запуск упражнения (в отдельном процессе)
@app.route('/start_exercise/armbend')
def start_exercise():
    try:
        # Запуск скрипта armBending.py в отдельном процессе
        subprocess.Popen(["python", "src/backend/armBending.py"])
        return "Arm Bend exercise started", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

# Отображение страницы с видеопотоком
@app.route('/')
def index():
    return render_template('index.html')  # Страница, которая будет показывать видеопоток

# Видеопоток
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
