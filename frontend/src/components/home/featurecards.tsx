import { type ReactNode } from "react";
import { Link } from "react-router-dom";

interface FeatureCardProps {
  icon: ReactNode;
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
          <div className="featureIcon">{icon}</div>
        </div>
        <h3 className="featureTitle">{title}</h3>
        <p className="featureText">{text}</p>
      </div>
      <div className="hoverContent">
        <div className="iconWrapper iconWrapper--large">
          <div className="featureIcon">{icon}</div>
        </div>
        <h3 className="featureTitleLarge">{title}</h3>
      </div>
    </Link>
  );
}
