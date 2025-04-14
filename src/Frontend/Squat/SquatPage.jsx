// src/SquatPage.js

import React from 'react';

const SquatPage = () => {
    return (
        <div>
            <h1>Приседания</h1>
            <img
                src="http://localhost:5001/video_feed"
                alt="Video Stream"
                style={{width: '80%', borderRadius: '10px', border: '2px solid #ccc'}}
            />
        </div>
    );
};

export default SquatPage;
