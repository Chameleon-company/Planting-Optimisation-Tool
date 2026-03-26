import { Link } from "react-router-dom";

// Create interface to set types for FeatureCardProps
interface FeatureCardProps {
  icon: string;
  title: string;
  text: string;
  href: string;
}

// Set entire card as link, while displaying prop content
export default function FeatureCard({
  icon,
  title,
  text,
  href,
}: FeatureCardProps) {
  return (
    <Link to={href} className="featureCard">
      <div className="defaultContent">
        <div className="iconWrapper">
          <span className="featureIcon">{icon}</span>
        </div>
        <h3 className="featureTitle">{title}</h3>
        <p className="featureText">{text}</p>
      </div>
      <div className="hoverContent">
        <div className="hoverOverlay"></div>
        <span className="centerButton">Explore Now</span>
      </div>
    </Link>
  );
}
