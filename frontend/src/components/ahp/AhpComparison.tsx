import { useState } from "react";

// Map backend factor strings to the imported SVGs
const factorIconMap: Record<string, string> = {
  Rainfall: "/assets/images/rainfall.svg",
  Temperature: "/assets/images/temperature.svg",
  Elevation: "/assets/images/elevation.svg",
  pH: "/assets/images/ph.svg",
  Soil: "/assets/images/soil_texture.svg",
};

interface ComparisonProps {
  factors: string[];
  speciesName: string;
  onComplete: (matrix: number[][]) => void;
  onCancel: () => void;
}

export default function AhpComparison({
  factors,
  speciesName,
  onComplete,
  onCancel,
}: ComparisonProps) {
  // Initialize empty N x N identity matrix
  const [matrix, setMatrix] = useState<number[][]>(() =>
    Array.from({ length: factors.length }, (_, i) =>
      Array.from({ length: factors.length }, (_, j) => (i === j ? 1 : 0))
    )
  );

  const [queue] = useState(() => {
    const q = [];
    for (let r = 0; r < factors.length; r++) {
      for (let c = r + 1; c < factors.length; c++) {
        q.push({ r, c });
      }
    }
    return q;
  });

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedValue, setSelectedValue] = useState(1);

  const { r, c } = queue[currentIndex];
  const factorA = factors[r];
  const factorB = factors[c];

  const handleNext = () => {
    const newMatrix = matrix.map(row => [...row]);
    newMatrix[r][c] = selectedValue;
    newMatrix[c][r] = 1 / selectedValue;

    setMatrix(newMatrix);

    if (currentIndex < queue.length - 1) {
      setCurrentIndex(prev => prev + 1);
      setSelectedValue(1);
    } else {
      onComplete(newMatrix);
    }
  };

  const scaleOptions = [
    { label: "Extreme (9)", val: 9 },
    { label: "V.Strong (7)", val: 7 },
    { label: "Strong (5)", val: 5 },
    { label: "Slight (3)", val: 3 },
    { label: "Equal (1)", val: 1 },
    { label: "Slight (3)", val: 1 / 3 },
    { label: "Strong (5)", val: 1 / 5 },
    { label: "V.Strong (7)", val: 1 / 7 },
    { label: "Extreme (9)", val: 1 / 9 },
  ];

  return (
    <div className="ahp-results-card">
      <h3>Profiling: {speciesName}</h3>
      <p style={{ color: "#888" }}>
        Comparison {currentIndex + 1} of {queue.length}
      </p>

      <div className="ahp-comparison-box">
        <div className="ahp-factor-left">{factorA}</div>
        <div className="ahp-vs">vs</div>
        <div className="ahp-factor-right">{factorB}</div>
      </div>

      <div>
        <p style={{ marginBottom: "15px" }}>Which factor is more important?</p>

        <div className="ahp-scale-wrapper">
          {/* Left Side Icon (Factor A) */}
          <div className="ahp-icon-side">
            <img
              src={factorIconMap[factorA] || "/assets/images/default.svg"}
              alt={factorA}
              className="ahp-svg-icon"
            />
            <span className="ahp-icon-label">Favours {factorA}</span>
          </div>

          <div className="ahp-scale-container">
            {scaleOptions.map((opt, idx) => {
              const isActive = opt.val === selectedValue;

              return (
                <button
                  key={idx}
                  className={`ahp-scale-btn ${isActive ? "active" : ""}`}
                  onClick={() => setSelectedValue(opt.val)}
                  aria-pressed={isActive}
                  title={opt.label}
                >
                  {opt.val === 1
                    ? "1"
                    : Math.round(opt.val) || Math.round(1 / opt.val)}
                </button>
              );
            })}
          </div>

          {/* Right Side Icon (Factor B) */}
          <div className="ahp-icon-side">
            <img
              src={factorIconMap[factorB] || "/assets/images/default.svg"}
              alt={factorB}
              className="ahp-svg-icon"
            />
            <span className="ahp-icon-label">Favours {factorB}</span>
          </div>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "15px",
          marginTop: "30px",
        }}
      >
        <button className="ahp-secondary-btn" onClick={onCancel}>
          Cancel
        </button>
        <button className="ahp-primary-btn" onClick={handleNext}>
          Next Comparison ➔
        </button>
      </div>
    </div>
  );
}
