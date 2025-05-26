import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Signup from './pages/Signup';
import Login from './pages/Login';
import Home from './pages/Home';
import EmotionalDiary from './components/EmotionalDiary'
import './App.css';

function App() {
  const [count, setCount] = useState(0);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/Home" element={<Home />} />
        <Route path="/EmotionalDiary" element={<EmotionalDiary />} />
      </Routes>
    </Router>
  );
}

export default App;