import React, { useEffect } from 'react';

const PushUpsPage = () => {
    useEffect(() => {
        // При размонтировании компонента вызываем остановку видео
        return () => {
            fetch('http://localhost:5000/stop_video')
                .then((response) => {
                    if (!response.ok) {
                        throw new Error('Failed to stop video');
                    }
                })
                .catch((error) => {
                    console.error('Error stopping video:', error);
                });
        };
    }, []);

    return (
        <div style={{ textAlign: 'center' }}>
            <h1>Отжимания</h1>
            <img
                src="http://localhost:5000/video_feed?source=camera&exercise=pushups"
                alt="Video Stream"
                style={{borderRadius: '10px', border: '2px solid #ccc' }}
            />
            <p>Выполняйте отжимания перед камерой</p>
        </div>
    );
};

export default PushUpsPage;
