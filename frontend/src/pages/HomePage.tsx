import { Helmet } from "react-helmet-async";

import FeaturesSection from "@/components/home/features";
import AboutSection from "@/components/home/aboutsection";
import Landing from "@/components/home/landing";

function HomePage() {
  return (
    <div>
      <Helmet>
        <title>Home | Planting Optimisation Tool</title>
      </Helmet>

      {/* Landing component, hand values to component and display */}
      <Landing
        video="assets/videos/herobg.mp4"
        tagline="Planting Optimisation Tool"
        subtitle="Generate your environmental profile!"
        exploreButton="Generate"
      />

      {/* AboutSection component, hand values to component and display */}
      <AboutSection
        logoSrc="/assets/images/logo2.svg"
        logoAlt="xpandFoundation Logo"
        tagline="A tool developed under xpandFoundation"
        title="About Us"
        description="We help farmers in Timor-Leste generate their environmental profile to discover the best tree species for their land."
      />

      {/* Features component, values stored in component */}
      <FeaturesSection />
    </div>
  );
}

export default HomePage;
