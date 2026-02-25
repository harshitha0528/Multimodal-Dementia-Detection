import React, { useState, useEffect } from "react";
import testImage from "./assets/cognitive_test.jpg";

function CognitiveTest({ onScoreCalculated }) {
  const [showImage, setShowImage] = useState(true);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(20);

  const questions = [
    {
      id: "q1",
      question: "How many people were in the image?",
      options: ["1", "2", "3", "4"],
      correct: "2",
    },
    {
      id: "q2",
      question: "What was the boy doing?",
      options: [
        "Washing dishes",
        "Taking cookies",
        "Cleaning floor",
        "Eating at table",
      ],
      correct: "Taking cookies",
    },
    {
      id: "q3",
      question: "Was water overflowing from the sink?",
      options: ["Yes", "No"],
      correct: "Yes",
    },
  ];

  // Timer logic
  useEffect(() => {
    if (showImage && timeLeft > 0) {
      const timer = setTimeout(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }

    if (timeLeft === 0) {
      setShowImage(false);
    }
  }, [timeLeft, showImage]);

  const handleChange = (qid, value) => {
    setAnswers({ ...answers, [qid]: value });
  };

  const handleSubmit = () => {
    let score = 0;

    questions.forEach((q) => {
      if (answers[q.id] === q.correct) {
        score++;
      }
    });

    const normalizedScore = score / questions.length;

    onScoreCalculated(normalizedScore);
    alert(`Cognitive Score: ${normalizedScore.toFixed(2)}`);
  };

  return (
    <div>
      <h2>🧠 Visual Cognitive Test</h2>

      {showImage ? (
        <div>
          <p>Observe the image carefully. Time left: {timeLeft} seconds</p>
          <img src={testImage} alt="Test" style={{ width: "300px" }} />
        </div>
      ) : (
        <div>
          <p>Now answer the following questions:</p>

          {questions.map((q) => (
            <div key={q.id}>
              <p>{q.question}</p>
              {q.options.map((opt) => (
                <label key={opt} style={{ marginRight: "10px" }}>
                  <input
                    type="radio"
                    name={q.id}
                    value={opt}
                    onChange={() => handleChange(q.id, opt)}
                  />
                  {opt}
                </label>
              ))}
            </div>
          ))}

          <button type="button" onClick={handleSubmit}>
            Submit Cognitive Test
          </button>
        </div>
      )}
    </div>
  );
}

export default CognitiveTest;