import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import testImage from "./assets/cognitive_test.jpg";

function CognitivePage() {
  const location = useLocation();
  const navigate = useNavigate();

  const { mri, audio, patientName, age, gender, mobileNumber, city } = location.state || {};

  const [showImage, setShowImage] = useState(true);
  const [timeLeft, setTimeLeft] = useState(20);
  const [answers, setAnswers] = useState({});

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

    navigate("/result", {
      state: { mri, audio, cognitiveScore, patientName, age, gender, mobileNumber, city },
    });
  };

  const allAnswered = questions.every((q) => Boolean(answers[q.id]));

  return (
    <div className="cognitiveShell">
      <div className="cognitiveTop">
        <h2>NeuroFusion AI</h2>
      </div>

      <div className="cognitiveBody">
        {showImage ? (
          <div className="cognitivePreview">
            <div className="timerBadge">Time left: {timeLeft}s</div>
            <img src={testImage} alt="Memory Test" className="cognitiveMainImage" />
          </div>
        ) : (
          <div className="mcqWrap">
            <h3>Visual Memory Questions</h3>
            {questions.map((q, index) => (
              <article key={q.id} className="mcqCard">
                <p className="mcqTitle">
                  <span>{`Q${index + 1}`}</span> {q.question}
                </p>
                <div className="mcqOptions">
                  {q.options.map((opt) => {
                    const isSelected = answers[q.id] === opt;
                    return (
                      <label key={opt} className={`mcqPill ${isSelected ? "selected" : ""}`}>
                        <input
                          type="radio"
                          name={q.id}
                          value={opt}
                          checked={isSelected}
                          onChange={() => handleChange(q.id, opt)}
                        />
                        <span>{opt}</span>
                      </label>
                    );
                  })}
                </div>
              </article>
            ))}

            <button onClick={handleSubmit} className="mcqSubmit" disabled={!allAnswered}>
              Run Analysis {"->"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default CognitivePage;
