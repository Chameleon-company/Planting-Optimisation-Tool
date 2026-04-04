import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { useRecommendations } from "../hooks/useRecommendations";
import { styles } from "../utils/recommend_styles";

import RecommendationHeader from "@/components/recommendations/recommendationHeader";
import RecommendationSearch from "@/components/recommendations/recommendationSearch";
import RecommendationTable from "@/components/recommendations/recommendationTable";
import ExcludedTable from "@/components/recommendations/excludedTable";

export default function RecommendationPage() {
  const [farmId, setFarmId] = useState("");
  const { recs, excludes, isLoading, hasSearched } = useRecommendations(farmId);

  const topFits = recs.filter(r => r.score_mcda >= 0.8);
  const cautionaryFits = recs.filter(r => r.score_mcda < 0.8);

  return (
    <div style={styles.viewContainer}>
      <Helmet>
        <title>Agroforestry Recommendation | Planting Optimisation Tool</title>
      </Helmet>

      <RecommendationHeader />

      <RecommendationSearch onSearch={setFarmId} isLoading={isLoading} />

      {hasSearched && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', width: '100%' }}>
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
          <ExcludedTable
            data={excludes}
          />
        </div>
      )}
    </div>
  );
}