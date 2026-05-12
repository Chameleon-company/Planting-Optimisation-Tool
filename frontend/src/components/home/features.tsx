import { Trees, Calculator, SatelliteDish, BookOpenCheck } from "lucide-react";
import FeatureCard from "./featurecards";

const features = [
  {
    icon: <Trees size={32} color="#fff" />,
    title: "Agroforestry Recommendations",
    text: "Determine which species are best suited for your farms conditions and needs.",
    href: "/recommendation",
  },
  {
    icon: <Calculator size={32} color="#fff" />,
    title: "Sapling Estimation Calculator",
    text: "Maximise the potential of your land by optimising how many saplings can be planted.",
    href: "/calculator",
  },
  {
    icon: <SatelliteDish size={32} color="#fff" />,
    title: "Generate Environmental Profile",
    text: "Generate a comprehensive environmental profile report of your farms conditions.",
    href: "/profile",
  },
  {
    icon: <BookOpenCheck size={32} color="#fff" />,
    title: "Species Information",
    text: "Access detailed information on 20 approved species by Gold Standard to understand their ecological limits.",
    href: "/species",
  },
];

// Set features as grid using .map with each feature being mapped to the FeatureCard
// With key set as link/href, icon as icon, href as href, etc
export default function FeaturesSection() {
  return (
    <section className="featuresSection">
      <div className="featuresContainer">
        {features.map(feature => (
          <FeatureCard
            key={feature.href}
            icon={feature.icon}
            title={feature.title}
            text={feature.text}
            href={feature.href}
          />
        ))}
      </div>
    </section>
  );
}
