import React from "react";
import "@/pages/recommendations.css";

// Returns the progress bar color based on the MCDA score
export const getBarColor = (score: number) => {
  if (score >= 0.8) return "#28a745"; // green
  if (score >= 0.4) return "#fd7e14"; // orange
  return "#dc3545"; // red
};

// Returns styling for the empty state cards
export const getEmptyStateStyle = (
  type: "top" | "caut" | "exc"
): React.CSSProperties => {
  const baseStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    padding: "20px",
    margin: "20px 0 10px 0",
    borderRadius: "6px",
    borderWidth: "1px",
    borderStyle: "solid",
    fontSize: "0.95rem",
  };

  switch (type) {
    case "top":
      return {
        ...baseStyle,
        color: "#155724",
        backgroundColor: "#d4edda",
        borderColor: "#c3e6cb",
      };
    case "caut":
      return {
        ...baseStyle,
        color: "#856404",
        backgroundColor: "#fff3cd",
        borderColor: "#ffeeba",
      };
    case "exc":
      return {
        ...baseStyle,
        color: "#155724",
        backgroundColor: "#d4edda",
        borderColor: "#c3e6cb",
      };
    default:
      return baseStyle;
  }
};

// Returns the small icon for the empty state message
export const getEmptyStateIcon = (type: "top" | "caut" | "exc") => {
  switch (type) {
    case "top":
      return "ⓘ";
    case "caut":
      return "⚠";
    case "exc":
      return "✓";
    default:
      return "ⓘ";
  }
};

// Formats the text and assigns colors/icons inside the expanded details row
export const renderReason = (reason: string) => {
  const text = reason.toLowerCase();
  const parts = reason.split(":");
  const factor = parts[0] ? parts[0].trim() : "";
  const result = parts[1] ? parts[1].trim() : "";

  const isPositive =
    text.includes("inside") ||
    text.includes("exact match") ||
    text.includes("plateau");
  const isNegative =
    text.includes("below minimum") ||
    text.includes("above maximum") ||
    text.includes("no_match") ||
    text.includes("not supported") ||
    text.includes("excluded");

  const color = isPositive ? "#28a745" : isNegative ? "#dc3545" : "#fd7e14";
  const icon = isPositive ? "✓" : isNegative ? "✗" : "⚠";

  const formatFactor = (str: string) => {
    if (!str) return "";
    if (str.toLowerCase() === "ph") return "pH";
    return str.charAt(0).toUpperCase() + str.slice(1);
  };

  return (
    <div className="rec-reason-row">
      <span
        style={{
          color,
          textAlign: "left",
          fontWeight: isPositive || isNegative ? "600" : "400",
        }}
      >
        <span>{formatFactor(factor)}</span>
        {result && (
          <span style={{ color: "#888", fontWeight: "400" }}>
            {" "}
            &nbsp;&nbsp;—&nbsp;&nbsp; {result}
          </span>
        )}
      </span>
      <span style={{ color, fontSize: "1.2rem", marginLeft: "20px" }}>
        {icon}
      </span>
    </div>
  );
};
