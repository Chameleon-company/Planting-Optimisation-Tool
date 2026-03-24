import { useNavigate } from "react-router-dom";

// Create interface to type the handed props
interface LandingProps {
  video: string;
  tagline: string;
  subtitle: string;
  exploreButton: string;
}

export default function Landing({
  video,
  tagline,
  subtitle,
  exploreButton,
}: LandingProps) {
  const navigate = useNavigate();

  // Display information handed by props, explore button heads to profile page
  return (
    <section className="heroSection">
      <video className="heroVideo" autoPlay loop muted playsInline>
        <source src={video} type="video/mp4" />
      </video>
      <div className="videoOverlay"></div>
      <div className="heroTagline">
        <h1>{tagline}</h1>
      </div>
      <div className="heroCTA">
        <p className="heroSubtitle">{subtitle}</p>
        <button className="exploreButton" onClick={() => navigate("/profile")}>
          {exploreButton}
        </button>
      </div>
    </section>
  );
}
