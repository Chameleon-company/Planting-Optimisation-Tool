export interface GlobalWeightItem {
  feature: string;
  mean_weight: number;
  ci_lower: number;
  ci_upper: number;
  ci_width: number;
  touches_zero: boolean;
}

export interface GlobalWeightsRunSummary {
  run_id: string;
  created_at: string;
  bootstraps: number;
  bootstrap_early_stopped: boolean;
  source: string | null;
}

export interface InterpretedWeights {
  overview: string;
  commentary: Record<string, string>;
}

export function formatFactor(str: string) {
  if (!str) return "";
  if (str.toLowerCase() === "ph") return "pH";
  if (str.toLowerCase() === "soil_texture") return "Soil Texture";
  const parts = str.split("_");
  const factor = parts[0] ? parts[0].trim() : "";
  return factor.charAt(0).toUpperCase() + factor.slice(1);
}

export function interpretGlobalWeights(
  rows: GlobalWeightItem[]
): InterpretedWeights {
  const sorted = [...rows].sort((a, b) => b.mean_weight - a.mean_weight);
  const maxMean = Math.max(...rows.map(r => r.mean_weight));

  const commentary: Record<string, string> = {};
  const overviewBits: string[] = [];

  sorted.forEach(row => {
    const { feature, mean_weight, ci_lower, ci_width, touches_zero } = row;

    const dominant = mean_weight >= 0.4 && ci_lower > 0.15;
    const moderate = mean_weight >= 0.15 && mean_weight < 0.4 && ci_lower > 0;
    const minor = mean_weight < 0.15 && !touches_zero;
    const wideCI = ci_width > 0.3;

    let text: string;

    if (dominant) {
      text =
        "This criterion is the dominant system-level driver. It consistently provides strong discriminatory power across farms and remains influential even under conservative assumptions.";
    } else if (moderate) {
      text =
        "This criterion has moderate but robust global importance. It contributes meaningfully to discrimination in many contexts, though it is not universally dominant.";
    } else if (minor) {
      text =
        "This criterion plays a secondary role at the system level. Its influence is consistent but comparatively limited, often acting as a contextual or supporting factor.";
    } else {
      text =
        "This criterion shows weak or uncertain global importance. Its contribution is not consistently distinguishable from zero once other criteria are considered.";
    }

    if (wideCI) {
      text +=
        " The wide confidence interval indicates that its importance varies substantially across farms or environmental contexts.";
    }

    if (mean_weight === maxMean) {
      overviewBits.push(
        `${formatFactor(feature)} emerges as the primary global discriminator.`
      );
    }

    commentary[feature] = text;
  });

  return {
    overview:
      "Global importance weights indicate how strongly each environmental criterion contributes to distinguishing species performance across farms. " +
      overviewBits.join(" "),
    commentary,
  };
}
