// Footer.jsx
import React from "react";
import { Link } from "react-router-dom";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <p className="footer-text">
        By using this app, you agree to our{" "}
        <Link to="/terms" className="footer-link">
          Terms of Service
        </Link>{" "}
        and{" "}
        <Link to="/privacy" className="footer-link">
          Privacy Policy
        </Link>.
      </p>
      <p className="footer-subtext">© {new Date().getFullYear()} AcadHelper. All rights reserved.</p>
    </footer>
  );
};

export default Footer;
