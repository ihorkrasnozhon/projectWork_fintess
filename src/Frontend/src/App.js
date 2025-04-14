import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ExerciseSelector from '../Functionality/ExerciseSelector';
import ArmBendPage from "../ArmBending/ArmBendPage";
import SquatPage from "../Squat/SquatPage";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<ExerciseSelector />} />
                <Route path="/exercise/arm-bend" element={<ArmBendPage />} />
                <Route path="/exercise/squat" element={<SquatPage />} />
            </Routes>
        </Router>
    );
};

export default App;
