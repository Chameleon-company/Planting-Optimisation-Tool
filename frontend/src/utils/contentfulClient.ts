import { createClient } from "contentful";

const SPACE_ID = import.meta.env.VITE_SPACE_ID;
const ACCESS_TOKEN = import.meta.env.VITE_ACCESS_TOKEN;

console.log("Contentful Config:", {
  spaceId: SPACE_ID ? "Loaded" : "Missing",
  token: ACCESS_TOKEN ? "Loaded" : "Missing",
});

if (!SPACE_ID || !ACCESS_TOKEN) {
  console.error(
    "CRITICAL ERROR: Contentful API keys are missing. Check your .env file!"
  );
  throw new Error(
    "Contentful configuration missing. Check .env file for VITE_SPACE_ID and VITE_ACCESS_TOKEN."
  );
}

export const client = createClient({
  space: SPACE_ID,
  accessToken: ACCESS_TOKEN,
});

export interface RichTextNode {
  nodeType: string;
  value?: string;
  content?: RichTextNode[];
}

export interface Species {
  sys: { id: string };
  fields: {
    name: string;
    scientificName?: string;
    image?: {
      fields: {
        file: {
          url: string;
        };
      };
    };
    description?: { content: RichTextNode[] };
    keywords?: string[];
  };
}
