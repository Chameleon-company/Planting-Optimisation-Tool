import "./style.css";
import { client, Species, RichTextNode } from "./utils/contentfulClient";

const searchInput = document.getElementById(
  "speciesSearch"
) as HTMLInputElement;
const searchBtn = document.getElementById(
  "speciesSearchBtn"
) as HTMLButtonElement;
const grid = document.getElementById("speciesArticles") as HTMLElement;
const emptyMsg = document.getElementById("speciesEmpty") as HTMLElement;

// --- 1. Fetch Data ---
async function fetchSpecies(query: string = "") {
  try {
    const response = await client.getEntries({
      content_type: "species",
      query: query,
      limit: 100,
    });
    return response.items as unknown as Species[];
  } catch (error) {
    console.error("Error fetching data:", error);
    return [];
  }
}

// --- 2. Render Grid (Cards) ---
function renderGrid(items: Species[]) {
  grid.innerHTML = "";

  if (items.length === 0) {
    emptyMsg.hidden = false;
    emptyMsg.textContent = "No species found matching your criteria.";
    return;
  }

  emptyMsg.hidden = true;

  items.forEach(item => {
    const { name, image } = item.fields;

    const imageUrl = image?.fields?.file?.url
      ? `https:${image.fields.file.url}`
      : "https://placehold.co/600x400?text=No+Image";

    const card = document.createElement("article");
    card.className = "article-card";
    card.innerHTML = `
      <div class="article-media">
        <img src="${imageUrl}" alt="${name}" />
      </div>
      <div class="article-body">
        <h3 class="article-title">${name}</h3>
        <div class="article-actions">
          <button class="btn-outline view-details-btn">View Details</button>
        </div>
      </div>
    `;

    // Click to open Modal
    card
      .querySelector(".view-details-btn")
      ?.addEventListener("click", () => openModal(item));
    grid.appendChild(card);
  });
}

// --- 3. Render Modal (Pop-up) ---
function openModal(item: Species) {
  let modal = document.getElementById("speciesModal");
  if (!modal) {
    createModalDOM();
    modal = document.getElementById("speciesModal");
  }

  const { name, scientificName, description, image } = item.fields;
  const imageUrl = image?.fields?.file?.url
    ? `https:${image.fields.file.url}`
    : "";

  const renderRichText = (document?: { content: RichTextNode[] }) => {
    if (!document?.content) return "<p>No details available.</p>";

    return document.content
      .map((node: RichTextNode) => {
        if (node.nodeType === "paragraph" && node.content) {
          const text = node.content
            .map((c: RichTextNode) => c.value || "")
            .join("");
          return `<p>${text}</p>`;
        }
        if (node.nodeType === "heading-3" && node.content) {
          const text = node.content
            .map((c: RichTextNode) => c.value || "")
            .join("");
          return `<h3>${text}</h3>`;
        }
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
        return "";
      })
      .join("");
  };

  const modalContent = modal!.querySelector(
    ".modal-content-body"
  ) as HTMLElement;

  modalContent.innerHTML = `
    <div class="modal-header-img">
        ${imageUrl ? `<img src="${imageUrl}" alt="${name}">` : ""}
    </div>
    <h2>${name}</h2>
    ${scientificName ? `<h4 class="scientific-name">${scientificName}</h4>` : ""}
    <div class="modal-rich-text">
        ${renderRichText(description)}
    </div>
  `;

  modal!.classList.add("active");
}

function createModalDOM() {
  const modal = document.createElement("div");
  modal.id = "speciesModal";
  modal.className = "side-modal";
  modal.innerHTML = `
    <div class="modal-overlay"></div>
    <div class="modal-panel">
      <button class="close-modal-btn">&times;</button>
      <div class="modal-content-body"></div>
    </div>
  `;
  document.body.appendChild(modal);

  const close = () => modal?.classList.remove("active");
  modal.querySelector(".close-modal-btn")?.addEventListener("click", close);
  modal.querySelector(".modal-overlay")?.addEventListener("click", close);
}

async function handleSearch() {
  const query = searchInput.value.trim();
  if (!query) {
    grid.innerHTML = "";
    emptyMsg.hidden = false;
    emptyMsg.textContent = "Enter a keyword to search for species.";
    return;
  }

  searchBtn.textContent = "...";
  const results = await fetchSpecies(query);
  renderGrid(results);
  searchBtn.innerHTML =
    '<span class="search-icon">🔍</span><span>Search</span>';
}

function init() {
  searchBtn.addEventListener("click", handleSearch);
  searchInput.addEventListener("keydown", e => {
    if (e.key === "Enter") handleSearch();
  });

  emptyMsg.hidden = false;
  emptyMsg.textContent =
    "Enter keywords like '2000mm' or 'boundary systems' to find species.";
}

init();
