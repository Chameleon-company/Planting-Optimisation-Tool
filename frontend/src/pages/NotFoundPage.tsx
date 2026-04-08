import { Helmet } from "react-helmet-async";

import NotFoundContent from "@/components/notfound/notfoundcontent";

// Not Found Page, for when a user searches for a page which does not exist
function NotFoundPage() {
  return (
    <div>
      <Helmet>
        <title>Not Found | Planting Optimisation Tool</title>
      </Helmet>

      {/* NotFoundContent, if empty page is searchde for, display this */}
      <NotFoundContent />
    </div>
  );
}

export default NotFoundPage;
