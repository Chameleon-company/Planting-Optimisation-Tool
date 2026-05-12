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
        tagline="Planting Optimisation Tool"
        subtitle="Find the best suited species for your farm!"
        exploreButton="Find"
      />

      {/* AboutSection component, hand values to component and display */}
      <AboutSection
        logoSrc="/assets/images/logo2.svg"
        logoAlt="Planting Optimisation Tool Logo"
        tagline="A tool developed in partnership with xPand Foundation and the Rai Matak project."
        title="About Us"
        description="We help farmers in Timor-Leste generate their environmental profile to discover the best tree species for their land."
        partners={[
          {
            src: "/assets/images/xPand_logo.png",
            alt: "xPand Foundation",
            href: "https://xpand.net.au/",
          },
          {
            src: "/assets/images/rai-matak.svg",
            alt: "Rai Matak",
            href: "https://www.raimatak.org/",
          },
        ]}
      />

      {/* Features component, values stored in component */}
      <FeaturesSection />
    </div>
  );
}

export default HomePage;
