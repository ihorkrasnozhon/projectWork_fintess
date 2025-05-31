// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ExerciseSelector from '../Functionality/ExerciseSelector';
import ArmBendPage from "../ArmBending/ArmBendPage";
import SquatPage from "../Squat/SquatPage";
import ArmBendVideoPage from "../ArmBending/ArmBendVideoPage"; // добавляем
import SquatVideoPage from "../Squat/SquatVideoPage";           // добавляем
import Header from "../Header/Header";
import PushUpsPage from "../PushUps/PushUpsPsge";

const App = () => {
    return (
        <Router>
            <Header />
            <Routes>
                <Route path="/" element={<ExerciseSelector />} />
                <Route path="/exercise/arm-bend" element={<ArmBendPage />} />
                <Route path="/exercise/squat" element={<SquatPage />} />
                <Route path="/exercise/pushups" element={<PushUpsPage />} />

                <Route path="/exercise/arm-bend-video" element={<ArmBendVideoPage />} /> {/* добавляем */}
                <Route path="/exercise/squat-video" element={<SquatVideoPage />} /> {/* добавляем */}
            </Routes>
        </Router>
    );
};

export default App;
