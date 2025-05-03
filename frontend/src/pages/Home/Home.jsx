import React, { useState,useEffect } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/usercontext';
import './Home.css';

const baseURL = import.meta.env.VITE_BACKEND_URL;

const Home = () => {
  const navigate = useNavigate();
  const { user, setUser } = useUser(); 
  const [loading, setLoading] = useState(false);

  const login = useGoogleLogin({
    flow: 'auth-code',
    scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar',
    access_type: 'offline',
    prompt: 'consent',

    onSuccess: async (codeResponse) => {
      setLoading(true);
      try {
        const res = await fetch(`${baseURL}/userinfo`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: codeResponse.code }),
        });

        const data = await res.json();
        if (data.email) {
          localStorage.setItem('user_name', data.name);
          localStorage.setItem('user_email', data.email);
          setUser({ name: data.name, email: data.email });
          navigate('/test');
        } else {
          alert('Failed to retrieve user info.');
        }
      } catch (err) {
        console.error('Login error:', err);
        alert('Login failed.');
      }
      setLoading(false);
    },

    onError: () => {
      console.error('Google login error');
      alert('Login failed.');
    }
  });

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
  };

  useEffect(() => {
    const userName = localStorage.getItem('user_name');
    const userEmail = localStorage.getItem('user_email');
    if (userName && userEmail) {
      setUser({ name: userName, email: userEmail });
    }
  }, [setUser]);

  return (
    <div className="home-container">
      <h1 className="home-title">Welcome to Acadhelper</h1>
      <p className="home-subtitle">AI-powered Gmail Reminders at your fingertips</p>
      <div className="google-login-wrapper">
        {user ? (
          <button
            className="auth-button logout"
            onClick={handleLogout}
          >
            Sign out 😢
          </button>
        ) : (
          <button
            onClick={() => login()}
            className={`google-signin-btn ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign in with Google 😎'}
          </button>
        )}
      </div>
    </div>
  );
};

export default Home;
