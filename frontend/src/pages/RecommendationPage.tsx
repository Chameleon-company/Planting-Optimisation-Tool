import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { useRecommendations } from "@/hooks/useRecommendations";
import "./recommendations.css";
import RecommendationHeader from "@/components/recommendations/recommendationHeader";
import RecommendationSearch from "@/components/recommendations/recommendationSearch";
import RecommendationTable from "@/components/recommendations/recommendationTable";
import ExcludedTable from "@/components/recommendations/excludedTable";

export default function RecommendationPage() {
  const [farmId, setFarmId] = useState("");
  const { recs, excludes, isLoading, hasSearched, error, downloadPdf } =
    useRecommendations(farmId);

  const topFits = recs.filter(r => r.score_mcda >= 0.8);
  const cautionaryFits = recs.filter(r => r.score_mcda < 0.8);

  return (
    <div className="rec-view-container">
      <Helmet>
        <title>Agroforestry Recommendation | Planting Optimisation Tool</title>
      </Helmet>

      <RecommendationHeader />

      {/* Main Control Container */}
      <div className="rec-controls-wrapper">
        <RecommendationSearch onSearch={setFarmId} isLoading={isLoading} />

        {/* The button only exists in the DOM once hasSearched is true.*/}
        {hasSearched && recs.length > 0 && (
          <div className="rec-download-container">
            <button onClick={downloadPdf} className="rec-download-report-btn">
              Download PDF Report
            </button>
          </div>
        )}
      </div>

      {/* Localized Error Message */}
      {error && (
        <div className="rec-error-message">
          <p>
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      {hasSearched && (
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "20px",
            width: "100%",
          }}
        >
          <RecommendationTable
            title="Top Fit Species"
            data={topFits}
            emptyMessage="No highly suitable species found."
            type="top"
          />
          <RecommendationTable
            title="Cautionary Species"
            data={cautionaryFits}
            emptyMessage="No species with moderate suitability found."
            type="caut"
          />
          <ExcludedTable data={excludes} />
        </div>
      )}
    </div>
  );
}
