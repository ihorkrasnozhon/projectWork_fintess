import React, { useState } from 'react';

const SquatVideoPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoName, setVideoName] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    setVideoName(null);
    setUploadStatus('');
    setUploadProgress(0);
  };

  const handleUpload = () => {
    if (!selectedFile) {
      setUploadStatus('Выберите файл перед отправкой.');
      return;
    }

    setIsProcessing(true);
    setUploadStatus('Загрузка видео...');
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('video', selectedFile);

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
      <div style={{ padding: '20px' }}>
        <h1>Анализ приседаний по видео</h1>

        <div style={{ marginBottom: '20px' }}>
          <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              disabled={isProcessing}
          />
          <br />
          <button
              onClick={handleUpload}
              style={{ marginTop: '10px' }}
              disabled={isProcessing || !selectedFile}
          >
            {isProcessing ? 'Обработка...' : 'Загрузить и анализировать'}
          </button>
        </div>

        <p>{uploadStatus}</p>

        {isProcessing && (
            <div
                style={{
                  marginTop: '10px',
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
            <div style={{ marginTop: '10px', textAlign: 'center' }}>
              <h2>Результат анализа:</h2>
              <img
                  src={`http://localhost:5000/video_feed_video?video_path=${encodeURIComponent(
                      videoName
                  )}&exercise=squat_counter`}
                  alt="Squat analysis feed"
                  style={{
                    borderRadius: '10px',
                    border: '2px solid #ccc',
                    marginTop: '10px',
                    height: '80vh'
                  }}
              />
            </div>
        )}
      </div>
  );
};

export default SquatVideoPage;
