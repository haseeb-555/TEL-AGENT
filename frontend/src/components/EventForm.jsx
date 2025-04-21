import React, { useState } from 'react';

const EventForm = ({ onSubmit }) => {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [reminder, setReminder] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title || !startTime || !endTime) {
      return alert("Please fill in all required fields (title, start & end time)");
    }

    onSubmit({
      title,
      description: body,
      start: startTime,
      end: endTime,
      reminder1HourBefore: reminder
    });

    setTitle('');
    setBody('');
    setStartTime('');
    setEndTime('');
    setReminder(true);
  };

  return (
    <form onSubmit={handleSubmit} style={{
      backgroundColor: "#d6eaf8",
      padding: "20px",
      borderRadius: "10px",
      marginTop: "30px"
    }}>
      <h3>Create Calendar Event 📅</h3>
      <label>Title*:<br />
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          style={{ padding: "8px", width: "100%", marginBottom: "10px" }}
        />
      </label>
      <label>Body/Description:<br />
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          style={{ padding: "8px", width: "100%", marginBottom: "10px" }}
        />
      </label>
      <label>Start Time*:<br />
        <input
          type="datetime-local"
          value={startTime}
          onChange={(e) => setStartTime(e.target.value)}
          required
          style={{ padding: "8px", width: "100%", marginBottom: "10px" }}
        />
      </label>
      <label>End Time*:<br />
        <input
          type="datetime-local"
          value={endTime}
          onChange={(e) => setEndTime(e.target.value)}
          required
          style={{ padding: "8px", width: "100%", marginBottom: "10px" }}
        />
      </label>
      <label>
        <input
          type="checkbox"
          checked={reminder}
          onChange={() => setReminder(!reminder)}
          style={{ marginRight: "8px" }}
        />
        Set reminder 1 hour before 🔔
      </label>
      <br />
      <button type="submit" style={{ marginTop: "15px", padding: "10px", backgroundColor: "#1abc9c", color: "white", borderRadius: "5px" }}>
        Create Event 🛠️
      </button>
    </form>
  );
};

export default EventForm;
