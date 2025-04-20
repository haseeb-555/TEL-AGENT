// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import TestPage from './pages/test';

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const App = () => (
  <GoogleOAuthProvider clientId={clientId}>
    <Router>
      <Routes>
        <Route path="/test" element={<TestPage />} />
        {/* You can add more routes here like home, dashboard, etc */}
      </Routes>
    </Router>
  </GoogleOAuthProvider>
);

export default App;
