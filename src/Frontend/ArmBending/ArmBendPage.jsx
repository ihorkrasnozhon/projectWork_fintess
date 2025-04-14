import React from 'react';

const ArmBendPage = () => {
    return (
        <div style={{ textAlign: 'center' }}>
            <h1>Сгибание руки</h1>
            <img
                src="http://localhost:5000/video_feed"
                alt="Video Stream"
                style={{ width: '80%', borderRadius: '10px', border: '2px solid #ccc' }}
            />
            <p>Выполняйте упражнение перед камерой</p>
        </div>
    );
};

export default ArmBendPage;
