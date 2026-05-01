export default function GlobalWeightsHeader() {
  return (
    <div>
      <h2 className="ahp-view-title">Global Weights</h2>
      <p className="ahp-view-description">
        Upload, delete and view global weights for the MCDA engine. If no global
        weights shown, applied equal global importance to each feature. The
        scoring will solely be based on expert opinion.
      </p>
    </div>
  );
}
