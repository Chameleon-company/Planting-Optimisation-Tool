import FeatureCard from "./featurecards";

// Set features as constant, icon, title, text and link to be displayed in HomePage
const features = [
  {
    icon: "📍",
    title: "Generate environmental profile",
    text: "Provide your farm's boundaries to automatically load environmental data.",
    href: "/profile",
  },
  {
    icon: "🔢",
    title: "Bulk Sapling Calculator",
    text: "Calculate exactly how many saplings you need for your farm based on land size and optimal spacing.",
    href: "/calculator",
  },
  {
    icon: "🌳",
    title: "Species Information",
    text: "Access detailed information about 20 species approved by Gold Standard to understand their ecological limits.",
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
