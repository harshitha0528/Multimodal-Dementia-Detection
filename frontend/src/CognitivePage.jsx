import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import testImage from "./assets/cognitive_test.jpg";

function CognitivePage() {
  const location = useLocation();
  const navigate = useNavigate();

  const { mri, audio } = location.state || {};

  const [showImage, setShowImage] = useState(true);
  const [timeLeft, setTimeLeft] = useState(20);
  const [answers, setAnswers] = useState({});

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
      question: "Was water overflowing?",
      options: ["Yes", "No"],
      correct: "Yes",
    },
  ];

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

  const cognitiveScore = score / questions.length;

  console.log("Navigating with:", { mri, audio, cognitiveScore });

  navigate("/result", {
    state: { mri, audio, cognitiveScore },
  });
};
  return (
    <div style={{ padding: "30px" }}>
      <h2>Cognitive Visual Test</h2>

      {showImage ? (
        <div>
          <p>Observe carefully. Time left: {timeLeft}s</p>
          <img src={testImage} alt="Test" width="500" />
        </div>
      ) : (
        <div>
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

          <button onClick={handleSubmit}>
            Run Analysis
          </button>
        </div>
      )}
    </div>
  );
}

export default CognitivePage;