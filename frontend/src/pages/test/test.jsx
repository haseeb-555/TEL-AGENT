// src/pages/TestPage.jsx
import React, { useEffect, useState } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import EventForm from '../../components/EventForm';
import './test.css'

const TestPage = () => {
  const [user, setUser] = useState(null);
  const [emailCount, setEmailCount] = useState('');
  const [emails, setEmails] = useState([]);
  const [createLoading, setCreateLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(false);


  useEffect(() => {
    const name = localStorage.getItem("user_name");
    const email = localStorage.getItem("user_email");
    const token = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");
    if (name && email && token) {
      setUser({ name, email, token,refreshToken  });
      
    }
  }, []);

  useEffect(() => {
    if (!user) return;
  
    const interval = setInterval(() => {
      console.log("⏳ Triggering /createEvents every 5 minutes...");
      fetch("http://localhost:8000/createEvents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          refresh_token: localStorage.getItem("refresh_token"),
        }),
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            console.log("✅ Events created automatically!");
          } else {
            console.error("❌ Event creation failed in interval:", data);
          }
        })
        .catch(err => console.error("⚠️ Error in interval fetch:", err));
    }, 5 * 60 * 1000); 
  
    return () => clearInterval(interval); 
  }, [user]);
  

  const login = useGoogleLogin({
    flow: 'auth-code',
    scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar',
    access_type: 'offline',
    prompt: 'consent',

    onSuccess: async (codeResponse) => {
      try {
        const res = await fetch("http://localhost:8000/userinfo", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: codeResponse.code }),
        });

        const data = await res.json();
        console.log("Data extracted when 1st time login\n")
        //console.log(data)
        if (data && data.access_token) {
          localStorage.setItem("user_name", data.name);
          localStorage.setItem("user_email", data.email);
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          setUser({ name: data.name, email: data.email, token: data.access_token ,refreshToken: data.refresh_token});
        }
      } catch (err) {
        console.error("Login failed:", err);
      }
    },
    onError: (err) => {
      console.error("Login error:", err);
    }
  });

  const fetchEmails = async () => {
    if (!emailCount || emailCount <= 0) return alert("Reyy donkey 😤 enter valid number!");
    setFetchLoading(true);
    try {
      const res = await fetch("http://localhost:8000/getemails", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          refresh_token: localStorage.getItem("refresh_token"),
          count: emailCount
        }),
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
      const res = await fetch("http://localhost:8000/createEvents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          refresh_token: localStorage.getItem("refresh_token"),
          }),
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
    }finally{
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
            {/* <button onClick={fetchEmails} style={{ backgroundColor: "#27ae60", color: "white", padding: "10px", borderRadius: "5px" }}>
              Fetch now 🚀
            </button> */}
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
        <button onClick={login} style={{ padding: "12px", fontSize: "16px", backgroundColor: "#3498db", color: "white", borderRadius: "8px" }}>
          Sign in with Google 😎
        </button>
      )}
    </div>
  );
};

export default TestPage;
