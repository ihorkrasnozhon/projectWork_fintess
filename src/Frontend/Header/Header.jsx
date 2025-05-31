// src/components/Header.js
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const Header = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Не показывать кнопку, если уже на главной
    const showButton = location.pathname !== '/';



    return (
        <header style={{ padding: '10px 20px', borderBottom: '1px solid #ccc' }}>
            {showButton && (
                <button onClick={() => navigate('/')} style={{ padding: '5px 10px' }}>
                    На главную
                </button>
            )}
        </header>
    );
};

export default Header;
