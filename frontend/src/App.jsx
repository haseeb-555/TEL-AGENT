// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import TestPage from './pages/test/test.jsx';
import './App.css';
import Home from './pages/Home/Home';
import Privacy from './pages/Privacy/Privacy.jsx';
import Terms from './pages/Terms/Terms.jsx';
import Footer from './components/Footer/Footer.jsx';

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const App = () => (
  <GoogleOAuthProvider clientId={clientId}>
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/test" element={<TestPage />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
      </Routes>
      <Footer />
    </Router>
  </GoogleOAuthProvider>
);

export default App;
