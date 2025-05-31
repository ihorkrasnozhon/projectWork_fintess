import React, { useState, useRef } from 'react';

const PushUpsVideoPage = () => {
    const [videoFile, setVideoFile] = useState(null);
    const [videoName, setVideoName] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const videoRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        setVideoFile(file);
        setVideoName(null);
        setUploadStatus('');
        setUploadProgress(0);
    };

    const handleUpload = () => {
        if (!videoFile) {
            setUploadStatus('Выберите файл перед отправкой.');
            return;
        }

        setIsProcessing(true);
        setUploadStatus('Загрузка видео...');
        setUploadProgress(0);

        const formData = new FormData();
        formData.append('video', videoFile);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', 'http://localhost:5000/upload_video');

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const percent = Math.round((event.loaded / event.total) * 100);
                setUploadProgress(percent);
                setUploadStatus(`Загрузка: ${percent}%`);
            } else {
                setUploadStatus('Размер файла неизвестен.');
            }
        };

        xhr.onload = () => {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                if (data.video_path) {
                    setVideoName(data.video_path);
                    setUploadStatus('Видео загружено, начинается анализ...');
                } else {
                    setUploadStatus('Ошибка: сервер не вернул путь к видео');
                    setVideoName(null);
                }
            } else {
                setUploadStatus(`Ошибка при загрузке: ${xhr.statusText}`);
                setVideoName(null);
            }
            setIsProcessing(false);
            setUploadProgress(0);
        };

        xhr.onerror = () => {
            setUploadStatus('Ошибка при отправке.');
            setIsProcessing(false);
            setVideoName(null);
            setUploadProgress(0);
        };

        xhr.send(formData);
    };

    return (
        <div style={{ padding: 20 }}>
            <h2>Push-Ups Video Analysis</h2>

            <input
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                disabled={isProcessing}
            />
            <br /><br />

            <button
                onClick={handleUpload}
                disabled={isProcessing || !videoFile}
            >
                {isProcessing ? 'Обработка...' : 'Загрузить и анализировать'}
            </button>

            <p>{uploadStatus}</p>

            {isProcessing && (
                <div
                    style={{
                        marginTop: 10,
                        width: '80%',
                        background: '#eee',
                        borderRadius: '10px',
                    }}
                >
                    <div
                        style={{
                            width: `${uploadProgress}%`,
                            background: '#4caf50',
                            height: '10px',
                            borderRadius: '10px',
                            transition: 'width 0.3s ease',
                        }}
                    ></div>
                    <p>{uploadProgress}%</p>
                </div>
            )}

            {videoName && !isProcessing && (
                <div style={{ marginTop: 20 }}>
                    <img
                        ref={videoRef}
                        src={`http://localhost:5000/video_feed_video?video_path=${encodeURIComponent(
                            videoName
                        )}&exercise=pushups`}
                        alt="Push-ups video stream"
                        style={{ maxWidth: '100%', border: '1px solid #ccc' }}
                    />
                </div>
            )}
        </div>
    );
};

export default PushUpsVideoPage;
