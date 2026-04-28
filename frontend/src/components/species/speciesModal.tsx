import { Species, RichTextNode } from "../../utils/contentfulClient";

// Create interface for SpeciesModalProps, item is of type Species from Contenful or null,
// and onClose is a function promising void
interface SpeciesModalProps {
  item: Species | null;
  onClose: () => void;
}

export default function SpeciesModal({ item, onClose }: SpeciesModalProps) {
  // If no item has been clicked, return an empty page
  if (!item) return null;

  // Pull new variables from the fields within handed item
  const { name, scientificName, description, image } = item.fields;

  // Build imageUrl from fields
  const imageUrl = image?.fields?.file?.url
    ? `https:${image.fields.file.url}?w=500&fm=webp&q=85`
    : "";

  return (
    <div className="side-modal active">
      {/* Clicking the overlay outside the panel closes the modal */}
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-panel">
        {/* Close button in the top corner of the panel */}
        <button className="close-modal-btn" onClick={onClose}>
          &times;
        </button>
        <div className="modal-content-body">
          {/* Only render the image block if a valid url was built */}
          {imageUrl && (
            <div className="modal-header-img">
              <img src={imageUrl} alt={name} />
            </div>
          )}
          <h2>{name}</h2>
          {/* Only render scientific name if it exists on the entry */}
          {scientificName && (
            <h4 className="scientific-name">{scientificName}</h4>
          )}
          {/* Render the Contentful rich text as HTML using the helper below */}
          <div
            className="modal-rich-text"
            dangerouslySetInnerHTML={{ __html: renderRichText(description) }}
          />
        </div>
      </div>
    </div>
  );
}

// Converts a Contentful text document into an HTML string
// Handles paragraphs, headings, and lists
// Returns a fallback message if no content is provided
function renderRichText(document?: { content: RichTextNode[] }): string {
  if (!document?.content) return "<p>No details available.</p>";

  return document.content
    .map((node: RichTextNode) => {
      // Join all child text values and wrap in a paragraph tag
      if (node.nodeType === "paragraph" && node.content) {
        const text = node.content
          .map((c: RichTextNode) => c.value || "")
          .join("");
        return `<p>${text}</p>`;
      }
      // Join all child text values and wrap in a heading tag
      if (node.nodeType === "heading-3" && node.content) {
        const text = node.content
          .map((c: RichTextNode) => c.value || "")
          .join("");
        return `<h3>${text}</h3>`;
      }
      // Each list item has nested content, drill down to the text node value
      if (node.nodeType === "unordered-list" && node.content) {
        const items = node.content
          .map((li: RichTextNode) => {
            const firstChild = li.content?.[0];
            const textNode = firstChild?.content?.[0];
            return `<li>${textNode?.value || ""}</li>`;
          })
          .join("");
        return `<ul>${items}</ul>`;
      }
      // Return empty string for any unhandled node types
      return "";
    })
    .join("");
}
