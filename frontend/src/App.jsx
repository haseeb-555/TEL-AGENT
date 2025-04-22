// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import TestPage from './pages/test/test.jsx';
import './App.css';
import Home from './pages/Home/Home';
const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const App = () => (
  <GoogleOAuthProvider clientId={clientId}>
    <Router>
      <Routes>
       <Route path="/" element={<Home />} />
        <Route path="/test" element={<TestPage />} />
      </Routes>
    </Router>
  </GoogleOAuthProvider>
);

export default App;
