import { useNavigate } from "react-router-dom";

function NotFoundContent() {
  const navigate = useNavigate();

  // NotFoundContent for not found page, display text and create button that navigates back to home
  return (
    <div className="not-found-content">
      <h1 className="not-found-code">404</h1>
      <h2 className="not-found-title">Page not found</h2>
      <p className="not-found-description">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <button
        className="btn-primary not-found-btn"
        onClick={() => navigate("/")}
      >
        Back to Home
      </button>
    </div>
  );
}

export default NotFoundContent;
