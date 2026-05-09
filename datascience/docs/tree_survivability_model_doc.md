# Tree Survival Prediction Model - Documentation

## Overview
This model predicts whether a tree planted in Timor-Leste is likely to **survive** or **die**, based on the environmental conditions at its farm location and basic information about the tree. It was trained on TreeO2 (Dec 5) dataset covering tree-scan records across multiple farms.

This model is intended to support planting decisions by flagging trees or sites where survival is at risk which will help field staff focus their attention before problems occur.

---

## What the Model Predicts
The model outputs:
- **A survival probability** - the estimated chance the tree will survive (in percentage)
- **A prediction label** - `Survived` or `Died`, based on a tuned decision threshold

---

## Inputs Required

| Input | Description | Example |
|---|---|---|
| `species_name` | Normalised tree species name (must match species reference table) | `"Ai-kamelli"` |
| `temp` | Mean annual temperature at the farm location (°C) | `24.5` |
| `rain` | Mean annual rainfall at the farm location (mm) | `1200` |
| `elev` | Mean elevation of the farm (metres above sea level) | `450` |
| `slope` | Mean slope of the farm (degrees) | `12` |
| `ph` | Soil pH at the farm | `6.2` |
| `trunk_circumference` | Trunk circumference at time of scan (cm) | `15.0` |
| `planted_month` | Month the tree was planted (1–12) | `3` |
| `age_months` | Age of the tree in months at time of scan | `24` |

---

## Outputs of the Model

The model returns three things:

1. **Warnings** - if any environmental condition falls outside the species's known optimal range, a note is printed. These do not block the prediction but flag potential risk factors.
2. **Predicted survival probability** - the higher this value, the more likely the tree will survive.
3. **Prediction label** - `Survived` or `Died`, based on the tuned threshold.

### Understanding the Decision Threshold

The threshold was chosen to maximise the **F2 score**, which weights recall (catching dying trees) twice as heavily as precision. This means:

- The model is deliberately biased toward flagging trees as "at risk"
- Some trees predicted to die will actually survive (false alarms are expected)
- This trade-off is intentional as **missing a tree that will die is more costly than raising a false alarm**

---

## Model Performance

Evaluated on a held-out test set of approximately 196,700 tree records not used during training.

| Metric | Value | Plain-language meaning |
|---|---|---|
| ROC-AUC | 0.881 | Strong ability to separate survivors from deaths |
| Recall (Died) | 65% | Correctly flags approximately 2 in 3 trees that will die |
| Precision (Died) | 30% | 1 in 3 flagged trees are actually at risk |
| F2 Score (Died) | 0.528 | Best recall-weighted performance across all models tested |

**In practice:** if the model flags 100 trees as likely to die, approximately 30 will genuinely be at risk. Of all trees that actually die, the model catches roughly 65% of them.

---

## Limitations

**1. Class Imbalance**
Only ~5.6% of tree records are labelled as dead. Even with class weighting, the model has limited examples of dying trees to learn from. This is the primary reason precision for the "Died" class is low.

**2. How "Death" is Defined**
A tree is labelled "dead" when its FOB tag was later reused for a different tree which is used as a proxy for death, not a direct observation.

**3. Environmental Data Is Farm-Level**
Temperature, rainfall, elevation, slope, and soil pH are averaged at the farm level. Two trees on the same farm receive identical environmental inputs regardless of where they sit on the land and if there are any micro variation in any variables between them.

---

## Key Findings from Model Development

**Feature engineering was the critical breakthrough.**
Models trained on only the six raw environmental features resulted in ROC-AUC being approximately 0.754 regardless of algorithm. Adding trunk circumference, planting month, tree age, and four species-specific "outside optimal range" distances lifted performance to ROC-AUC 0.881. The optimal range features contributed most to this improvement.

**Synthetic oversampling (SMOTE-ENN) did not improve results.**
SMOTE-ENN has been tested but underperformed class-weighted LightGBM with threshold tuning, ROC-AUC 0.796 vs 0.881, F2 0.496 vs 0.528.

**Threshold tuning is essential for this use case.**
The default 50% threshold results in very few "Died" predictions. Moving it using F2 score roughly doubled recall for the "Died" class.

---

## Summary of Models Compared

| Model | ROC-AUC | Recall (Died) | Precision (Died) | F2 (Died) |
|---|---|---|---|---|
| Baseline (majority class) | - | 0% | - | 0.000 |
| Random Forest (no weighting) | 0.754 | 3% | 21% | 0.038 |
| Random Forest (balanced) | 0.754 | 56% | 12% | 0.359 |
| Random Forest (balanced + threshold) | 0.754 | 71% | 19% | 0.494 |
| LightGBM (balanced + threshold) | 0.881 | 61% | 24% | 0.461 |
| Random Forest (threshold) + SMOTE-ENN | 0.796 | 59% | 28% | 0.496 |
| **LightGBM (tuned + threshold) - selected** | **0.881** | **65%** | **30%** | **0.528** |

---

## Data Sources

- **Tree scan data:** TreeO2 (Dec 5)
- **Farm environmental data:** farm_master.csv (temperature, rainfall, elevation, slope, pH per farm)
- **Species optimal ranges:** species_20251222.csv (rainfall, temperature, elevation, pH min/max per species)
