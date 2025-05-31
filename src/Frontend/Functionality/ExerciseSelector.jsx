import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ExerciseSelector = () => {
    const [status, setStatus] = useState('');
    const navigate = useNavigate();

    const startExercise = (exercise) => {
        console.log('Упражнение выбрано:', exercise);

        fetch(`http://localhost:5000/start_exercise/${exercise}`)
            .then((res) => res.json())
            .then((data) => {
                console.log('Ответ сервера:', data);
                setStatus(data.status || data.error);

                if (exercise === 'armbend') {
                    navigate('/exercise/arm-bend');
                } else if (exercise === 'squat') {
                    navigate('/exercise/squat');
                } else if (exercise === 'pushups') {
                    navigate('/exercise/pushups');
                } else if (exercise === 'armbend_video') {
                    navigate('/exercise/arm-bend-video');
                } else if (exercise === 'squat_video') {
                    navigate('/exercise/squat-video');
                }
            })
            .catch((err) => {
                console.error('Ошибка:', err);
                setStatus('Ошибка: ' + err.message);
            });
    };

    return (
        <div>
            <h1>Выбор упражнения</h1>
            <button onClick={() => startExercise('armbend')}>Start Arm Bend (Камера)</button>
            <button onClick={() => startExercise('squat')}>Start Squat (Камера)</button>
            <button onClick={() => startExercise('pushups')}>Start Push Ups (Камера)</button>


            <button onClick={() => startExercise('armbend_video')}>Start Arm Bend (Видео)</button>
            <button onClick={() => startExercise('squat_video')}>Start Squat (Видео)</button>

            <p>{status}</p>
        </div>
    );
};

export default ExerciseSelector;
