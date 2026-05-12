import { useNavigate } from "react-router-dom";
import HeroCarousel from "./HeroCarousel";
import HeroTreeline from "./HeroTreeline";

// Create interface to type the handed props
interface LandingProps {
  tagline: string;
  subtitle: string;
  exploreButton: string;
}

export default function Landing({
  tagline,
  subtitle,
  exploreButton,
}: LandingProps) {
  const navigate = useNavigate();

  return (
    <section className="heroSection">
      <div className="heroTriangle" />
      <div className="heroTagline">
        <h1>{tagline}</h1>
      </div>
      <div className="heroCarouselWrapper">
        <HeroCarousel
          images={[
            "/assets/images/carousel/62cceb7eb84c2660c2035957_DSC_1408(small).webp",
            "/assets/images/carousel/62d5f7515f7e3f98385095e3_DSC_1025 (small) 4.webp",
            "/assets/images/carousel/1.webp",
            "/assets/images/carousel/2.webp",
            "/assets/images/carousel/3.webp",
            "/assets/images/carousel/4.webp",
            "/assets/images/carousel/5.webp",
            "/assets/images/carousel/6.webp",
            "/assets/images/carousel/7.webp",
            "/assets/images/carousel/8.webp",
            "/assets/images/carousel/9.webp",
            "/assets/images/carousel/10.webp",
            "/assets/images/carousel/11.webp",
            "/assets/images/carousel/12.webp",
            "/assets/images/carousel/13.webp",
          ]}
        />
      </div>
      <HeroTreeline />
      <div className="heroCTA">
        <p className="heroSubtitle">{subtitle}</p>
        <button
          className="exploreButton"
          onClick={() => navigate("/recommendation")}
        >
          {exploreButton}
        </button>
      </div>
    </section>
  );
}
