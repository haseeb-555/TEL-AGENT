import React, { useEffect, useState } from 'react';

const facts = [
  "📖 Pomodoro Technique: Study 25 mins, break 5 mins – boosts focus.",
  "🧠 Spaced repetition helps you retain information for the long-term.",
  "🌅 Early morning study boosts performance for 70% of students.",
  "✍️ Writing notes by hand improves understanding more than typing.",
  "🎧 Lo-fi or nature sounds can help increase your concentration.",
  "😴 Sleep consolidates learning – study before bed, then sleep 8 hrs!",
  "🚶 A short walk after studying boosts memory and creativity.",
  "🗣️ You remember 90% of what you teach – explain concepts aloud!"
];

const StudyFacts = ({ active }) => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!active) return;

    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % facts.length);
    }, 5000); // change every 5 seconds

    return () => clearInterval(interval);
  }, [active]);

  if (!active) return null;

  return (
    <div style={styles.container}>
      <p style={styles.text}>{facts[index]}</p>
    </div>
  );
};

const styles = {
  container: {
    background: "#f0f4ff",
    border: "1px solid #c7d2fe",
    padding: "1rem",
    borderRadius: "12px",
    maxWidth: "500px",
    margin: "1rem auto",
    fontSize: "1rem",
    fontWeight: "500",
    color: "#374151",
    textAlign: "center",
    boxShadow: "0 4px 10px rgba(0,0,0,0.1)"
  },
  text: {
    margin: 0
  }
};

export default StudyFacts;
