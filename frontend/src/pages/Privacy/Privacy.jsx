// privacy.jsx
import React from "react";
import "./Privacy.css";

const Privacy = () => {
  return (
    <div className="legal-container">
      <h1>Privacy Policy</h1>
      <p><strong>Effective Date:</strong> [5th May,2025]</p>

      <h2>1. Information We Access</h2>
      <p>We may access your Google account data based on permissions you grant, including basic profile info, Gmail data, or Calendar events.</p>

      <h2>2. How We Use Your Data</h2>
      <p>Your data is used only to provide app functionality like detecting deadlines and creating reminders. We do not store or share your data.</p>

      <h2>3. Data Storage and Security</h2>
      <p>Data is processed in-memory and not stored. We use secure HTTPS connections.</p>

      <h2>4. Your Consent and Control</h2>
      <p>You can revoke access anytime from your Google account settings.</p>

      <h2>5. Changes to This Policy</h2>
      <p>We may update this policy. Updates will be posted here.</p>

      <h2>6. Contact Us</h2>
      <p>Email: manvith.reddem@gmail.com</p>
    </div>
  );
};

export default Privacy;
