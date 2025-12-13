import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Chat from './components/Chat';
import DemoFlow from './pages/DemoFlow';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/demo" element={<DemoFlow />} />
            </Routes>
        </Router>
    );
}

export default App;
