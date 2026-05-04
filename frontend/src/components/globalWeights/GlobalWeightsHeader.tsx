export default function GlobalWeightsHeader() {
  return (
    <div>
      <h2 className="ahp-view-title">Global Weights</h2>
      <p className="ahp-view-description">
        Process EPI data, Upload, Delete and View global weights for the MCDA
        engine. If no Global Weights are shown, equal global importance is
        applied to each feature. The scoring will solely be based on expert
        opinion.
      </p>
    </div>
  );
}
