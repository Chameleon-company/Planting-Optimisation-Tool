import { Species } from "../../utils/contentfulClient";

interface SpeciesCardProps {
  item: Species;
  onClick: () => void;
}

export default function SpeciesCard({ item, onClick }: SpeciesCardProps) {
  const { name, image } = item.fields;

  const imageUrl = image?.fields?.file?.url
    ? `https:${image.fields.file.url}?w=700&fm=webp&q=80`
    : "https://placehold.co/600x400?text=No+Image";

  return (
    <article className="article-card">
      <div className="article-media">
        <img src={imageUrl} alt={name} />
      </div>
      <div className="article-body">
        <h3 className="article-title">{name}</h3>
        <div className="article-actions">
          <button className="btn-outline" onClick={onClick}>
            View Details
          </button>
        </div>
      </div>
    </article>
  );
}
