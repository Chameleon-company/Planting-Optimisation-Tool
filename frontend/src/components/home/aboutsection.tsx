// Create interface to set types for AboutSectionProps
interface AboutSectionProps {
  logoSrc: string;
  logoAlt: string;
  tagline: string;
  title: string;
  description: string;
}

// Display AboutSection as headings and paragraphs dependent on props handed to component
export default function AboutSection({
  logoSrc,
  logoAlt,
  tagline,
  title,
  description,
}: AboutSectionProps) {
  return (
    <section className="aboutSection">
      <div className="aboutLeft">
        <div className="aboutLogoContainer">
          <img src={logoSrc} alt={logoAlt} className="aboutLogo" />
          <span className="aboutLogoText">{tagline}</span>
        </div>
      </div>
      <div className="aboutRight">
        <h2 className="aboutTitle">{title}</h2>
        <p className="aboutDescription">{description}</p>
      </div>
    </section>
  );
}
