import React, { useState } from 'react';

const ExerciseSelector = () => {
    const [status, setStatus] = useState('');

    const startExercise = (exercise) => {
        fetch(`http://localhost:5000/start_exercise/${exercise}`)
            .then((response) => response.json())
            .then((data) => setStatus(data.status || data.error))
            .catch((error) => setStatus('Error: ' + error.message));
    };

    return (
        <div>
            <h1>Select an Exercise</h1>
            <button onClick={() => startExercise('armbend')}>Start Arm Bend</button>
            <button onClick={() => startExercise('squat')}>Start Squat</button>
            <p>{status}</p>
        </div>
    );
};

export default ExerciseSelector;
