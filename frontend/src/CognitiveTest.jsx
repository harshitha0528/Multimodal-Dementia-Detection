import React, { useState, useEffect } from "react";
import testImage from "./assets/cognitive_test.jpg";

function CognitiveTest({ onScoreCalculated }) {
  const [showImage, setShowImage] = useState(true);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(20);
  <h1 style={{color: "red"}}>THIS IS NEW VERSION</h1>
  const questions = [
  {
    id: "q1",
    question: "How many elderly people were sitting on the bench?",
    options: ["1", "2", "3", "4"],
    correct: "2",
  },
  {
    id: "q2",
    question: "What was the girl riding?",
    options: ["Scooter", "Bicycle", "Car", "Skateboard"],
    correct: "Bicycle",
  },
  {
    id: "q3",
    question: "What was located in the center of the park?",
    options: ["Statue", "Fountain", "Playground", "Tree"],
    correct: "Fountain",
  },
  {
    id: "q4",
    question: "What animals were in the pond?",
    options: ["Dogs", "Cats", "Ducks", "Fish"],
    correct: "Ducks",
  },
  {
    id: "q5",
    question: "What was the boy riding?",
    options: ["Bicycle", "Scooter", "Horse", "Car"],
    correct: "Scooter",
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