import React from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import "./Home.css"; 


const Home = () => {
  const navigate = useNavigate();

  const handleLoginSuccess = (credentialResponse) => {
    console.log('Login Success:', credentialResponse);
    navigate('/test');
  };

  const handleLoginError = () => {
    console.log('Login Failed');
  };

  return (
    <div className="home-container">
      <h1 className="home-title">Welcome to Acadhelper</h1>
      <p className="home-subtitle">AI-powered Gmail Reminders at your fingertips</p>
      <div className="google-login-wrapper">
        <GoogleLogin onSuccess={handleLoginSuccess} onError={handleLoginError} />
      </div>
    </div>
  );
};

export default Home;
