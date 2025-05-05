// terms.jsx
import React from "react";
import "./Terms.css"; // Reuse the same CSS

const Terms = () => {
  return (
    <div className="legal-container">
      <h1>Terms of Service</h1>
      <p><strong>Effective Date:</strong> [May 5th,2025]</p>

      <h2>1. Use of the App</h2>
      <p>Use the app only for lawful purposes. Misuse is not allowed.</p>

      <h2>2. User Data</h2>
      <p>We do not permanently store or share your data. Access is temporary.</p>

      <h2>3. Termination</h2>
      <p>We may terminate access for violations or abuse.</p>

      <h2>4. Limitation of Liability</h2>
      <p>The app is provided “as is” without warranty. Use at your own risk.</p>

      <h2>5. Changes to the Terms</h2>
      <p>Continued use implies acceptance of updated terms.</p>

      <h2>6. Contact Us</h2>
      <p>Email: manvith.reddem@gmail.com</p>
    </div>
  );
};

export default Terms;
