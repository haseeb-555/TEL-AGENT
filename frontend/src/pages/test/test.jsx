// src/pages/TestPage.jsx
import React, { useEffect, useState } from 'react';
import EventForm from '../../components/EventForm';
import './test.css';
import { useUser } from '../../context/usercontext';
const baseURL = import.meta.env.VITE_BACKEND_URL;

const TestPage = () => {
  const { user, setUser } = useUser();
  const [emailCount, setEmailCount] = useState('');
  const [emails, setEmails] = useState([]);
  const [createLoading, setCreateLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(false);

  useEffect(() => {
    const name = localStorage.getItem("user_name");
    const email = localStorage.getItem("user_email");
    if (name && email) {
      setUser({ name, email });
    }
  }, []);

  const fetchEmails = async () => {
    if (!emailCount || emailCount <= 0) return alert("Reyy donkey 😤 enter valid number!");
    setFetchLoading(true);
    try {
      const res = await fetch(`${baseURL}/getemails`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: user.email, count: emailCount }),
      });

      const data = await res.json();
      setEmails(data.emails || []);
    } catch (err) {
      console.error("Failed to fetch emails:", err);
    } finally {
      setFetchLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    setEmails([]);
    setEmailCount('');
  };

  const handleCreateEvent = async () => {
    setCreateLoading(true);
    try {
      const res = await fetch(`${baseURL}/createEvents`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: user.email }),
      });

      const data = await res.json();
      if (data.success) {
        alert("Event created successfully! ✅");
      } else {
        alert("Failed to create event 😞");
        console.error(data);
      }
    } catch (err) {
      console.error("Error creating event:", err);
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Comic Sans MS", backgroundColor: "#fef9e7", minHeight: "100vh" }}>
      <h1 style={{ color: "#8e44ad" }}>📩 Gmail Viewer</h1>

      {user ? (
        <>
          <div style={{ marginBottom: "20px", backgroundColor: "#d5f5e3", padding: "15px", borderRadius: "10px" }}>
            <h2>Welcome, {user.name}! 👋</h2>
            <p>Email: {user.email}</p>
            <button onClick={handleLogout} style={{ backgroundColor: "#e74c3c", color: "white", padding: "10px", borderRadius: "5px" }}>
              Sign out 😢
            </button>
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label>
              How many emails do you want?{" "}
              <input
                type="number"
                value={emailCount}
                onChange={(e) => setEmailCount(e.target.value)}
                style={{ padding: "5px", marginRight: "10px" }}
              />
            </label>
            <button
              onClick={fetchEmails}
              style={{
                backgroundColor: "#2980b9",
                color: "white",
                padding: "10px",
                borderRadius: "5px",
                cursor: fetchLoading ? "not-allowed" : "pointer",
                opacity: fetchLoading ? 0.6 : 1,
                marginLeft: "10px"
              }}
              disabled={fetchLoading}
            >
              {fetchLoading ? (
                <>
                  <span className="spinner" /> Fetching...
                </>
              ) : (
                "Fetch Now 🚀"
              )}
            </button>
          </div>

          <div>
            <button
              onClick={handleCreateEvent}
              style={{
                backgroundColor: "#27ae60",
                color: "white",
                padding: "10px",
                borderRadius: "5px",
                cursor: createLoading ? "not-allowed" : "pointer",
                opacity: createLoading ? 0.6 : 1,
              }}
              disabled={createLoading}
            >
              {createLoading ? (
                <>
                  <span className="spinner" /> Creating events...
                </>
              ) : (
                "Create Events from emails"
              )}
            </button>
          </div>

          <EventForm onSubmit={handleCreateEvent} />

          {fetchLoading && <p>Hold on donkey 🫏... Fetching your emails 📨</p>}

          {emails.length > 0 && (
            <div style={{ marginTop: "20px" }}>
              <h3>Your Glorious Emails 🧾</h3>
              {emails.map((email, index) => (
                <div
                  key={index}
                  style={{
                    border: "2px dashed #7dcea0",
                    padding: "10px",
                    marginBottom: "10px",
                    borderRadius: "10px",
                    backgroundColor: "#fcf3cf",
                  }}
                >
                  <strong>🆔 ID:</strong> {email.id} <br />
                  <strong>📌 Subject:</strong> {email.subject || "No Subject"} <br />
                  <strong>📨 Body:</strong> {email.body || "No content"} <br />
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <p>Please sign in from the homepage 😎</p>
      )}
    </div>
  );
};

export default TestPage;
