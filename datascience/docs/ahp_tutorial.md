# AHP Tree Species Weighting Tool: A Tutorial

## 1. Introduction

This tool uses the **Analytic Hierarchy Process (AHP)** to help you determine the precise environmental requirements for different tree species. Instead of guessing that "Mahogany needs good soil," this tool allows you to mathematically quantify *how much more important* soil is compared to rainfall or temperature.

The output is a set of **weights** (percentages) that you can directly input into the Planting Optimsation Tool Multi-Criteria Decision Analysis (MCDA) engine for suitability scoring.


## 2. Running the Tool

To start the process, open your terminal and source the uv virtual environment then run:

```bash
python src\ahp_cli.py
```

You will see a menu listing your species:

```text
============================================================
 AHP Species Weighting Tool
============================================================
 1. Casuarina equisetifolia [Ai-kakeu]
 2. Tectona grandis [Ai-teka]
 3. Pterocarpus indicus [Ai-na]
 4. Santalum album [Ai-kamelli]
 5. Sterculia foetida [Ai-nitas]
 6. Eucalyptus alba [Ai-bobur (mutin)]
 7. Eucalyptus urophylla [Ai-ru]
 8. Toona ciliata [Ai-saria]
 9. Sweitenia macrophylla [Ai-Mahony]
 10. Albizia procera [Itili/White Siris]
 11. Azadirachta indica [Ai-nimba/Neem]
 12. Terminalia catappa [Ai-Kalesi/Ketapang/Sea almond]
 13. Aquilaria malaccensis [Gaharu/Agarwood]
 14. Calophyllum inophyllum [Alexandrian Laurel]
 15. Aleurites moluccanus [Candelnut/Ai-kamii/Sae]
 16. Intsia bijuga [Moluccan Ironwood/Ai-besi]
 17. Canarium vulgare [Kenari nut/Kiar/Java Almond]
 18. Peltophorum pterocarpum [Ai-silose/Copperpod]
 19. Parkia speciosa [Petai/Pete]
 20. Falcataria falcata [Ai-samtuco]
 Q. Quit

Select Species:
```

Select a number (e.g., `1`) to begin profiling **Casuarina equisetifolia**.


## 3. Pairwise Comparison

The core of AHP is the **Pairwise Comparison** method. The tool will ask you to compare two factors at a time using the standard Saaty 1–9 scale.

### The Scale

When comparing **Factor A** (Left) vs. **Factor B** (Right):

| Value | Interpretation    | Meaning |
| ---   | ---               | ---     |
| **1** | Equal Importance  | Both factors contribute equally to growth. |
| **3** | Slightly Favors A | Experience slightly favors Factor A over B. |
| **5** | Strongly Favors A | Factor A is strongly more important. |
| **7** | Very Strong       | Factor A is critical compared to Factor B. |
| **9** | Extreme           | Factor A is absolutely essential; Factor B is negligible.|

### Entering Values

* **If Factor A is more important:** Enter a whole number (e.g., `5`).
* *Example:* "Rainfall is Strongly more important than Soil pH"  Enter `5`.


* **If Factor B is more important:** Enter a fraction (e.g., `1/5` or `0.2`).
* *Example:* "Elevation is Strongly more important than Rainfall"  Enter `1/5`.

The tool automatically builds a **Reciprocal Matrix**.

```text
================================================================================
 Profiling: Casuarina equisetifolia [Ai-kakeu]
================================================================================

Comparison 1/10

[?] Compare: rainfall vs temperature
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 9

Comparison 2/10

[?] Compare: rainfall vs elevation
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 1

Comparison 3/10

[?] Compare: rainfall vs ph
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 3

Comparison 4/10

[?] Compare: rainfall vs soil
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 3

Comparison 5/10

[?] Compare: temperature vs elevation
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 1/7

Comparison 6/10

[?] Compare: temperature vs ph
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 1

Comparison 7/10

[?] Compare: temperature vs soil
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 1

Comparison 8/10

[?] Compare: elevation vs ph
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 5

Comparison 9/10

[?] Compare: elevation vs soil
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 5

Comparison 10/10

[?] Compare: ph vs soil
    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)
    Enter preference: 1
```

## 4. Understanding the Results

After you answer all questions (comparisons), the tool calculates the results.

### A. The Weights (Priority Vector)

This is the **Normalised Eigenvector** of your matrix. It represents the relative importance of each factor as a percentage. The sum of all weights will always equal 1 (100%).

*Example Output:*

```text
---------------------------------------------
 Consistency Ratio: 2.9% (OK)
---------------------------------------------
 rainfall       : 0.3621
 temperature    : 0.0648
 elevation      : 0.4031
 ph             : 0.0850
 soil           : 0.0850
```

### B. Consistency Ratio (CR)

Humans are not always consistent. If you say **A > B** and **B > C**, but then say **C > A**, your logic is flawed (intransitive) .

The tool calculates a **Consistency Ratio (CR)**:


* **If CR < 10%:** Your judgments are consistent. The data is saved.


* **If CR > 10%:** Your judgments are inconsistent. You should re-run the comparison and think more carefully.


## 5. Output Data

If your profile is consistent, the tool saves the data to `species_params.csv`.

| species_id | feature              | score_method | weight | trap_left_tol | trap_right_tol |
|        --- |     ---              |          --- |    --- |           --- |            --- |
| 1          | rainfall_mm          | Unchanged    | 0.3621 | Unchanged     | Unchanged      |
| 1          | temperature_celsius  | Unchanged    | 0.0648 | Unchanged     | Unchanged      |
| 1          | elevation_m          | Unchanged    | 0.4031 | Unchanged     | Unchanged      |
| 1          | ph                   | Unchanged    | 0.085  | Unchanged     | Unchanged      |
| 1          | soil_texture         | Unchanged    | 0.085  | Unchanged     | Unchanged      |


### **Frequently Asked Questions**

**Q: Can I change the criteria?**
A: Yes. Edit the `config/recommend.yaml` file. The tool handles any number of features, but it is recommended to keep the number of factors low to avoid fatigue.

**Q: Why use fractions like 1/3?**
A: AHP uses reciprocal matrices. If A is 3 times more important than B, then B must be 1/3 as important as A.

**Q: My CR is negative?**
A: This tool uses exact Eigenvalue calculation (`numpy.linalg.eig`), so you will not see negative errors.
