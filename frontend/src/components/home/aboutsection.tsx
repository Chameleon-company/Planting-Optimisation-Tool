interface Partner {
  src: string;
  alt: string;
  href: string;
}

interface AboutSectionProps {
  logoSrc: string;
  logoAlt: string;
  tagline: string;
  title: string;
  description: string;
  partners?: Partner[];
}

export default function AboutSection({
  logoSrc,
  logoAlt,
  tagline,
  title,
  description,
  partners,
}: AboutSectionProps) {
  return (
    <section className="aboutSection">
      <div className="aboutLeft">
        <div className="aboutLogoContainer">
          <img src={logoSrc} alt={logoAlt} className="aboutLogo" />
          <span className="aboutLogoText">{tagline}</span>
        </div>
        {partners && partners.length > 0 && (
          <div className="aboutPartners">
            {partners.map(p => (
              <a key={p.href} href={p.href} target="_blank" rel="noreferrer">
                <img src={p.src} alt={p.alt} className="aboutPartnerLogo" />
              </a>
            ))}
          </div>
        )}
      </div>
      <div className="aboutRight">
        <h2 className="aboutTitle">{title}</h2>
        <p className="aboutDescription">{description}</p>
      </div>
    </section>
  );
}
