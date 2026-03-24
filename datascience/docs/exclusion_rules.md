# Task 4 – Function Signature for Exclusion Rules Module

This task defines the function signature for the exclusion rules module.  
The function will take farm-level data, species-level data, and rule settings as input.  
It will return the list of candidate species and the list of excluded species with reasons.

## Function Name

`run_exclusion_rules()`

## Inputs

| Name | Type | Description |
|------|------|-------------|
| `farm_data` | dict | Data for one farm, including rainfall, temperature, soil, habitat flags, and other conditions. |
| `species_data` | list[dict] | Species records. Each record holds the environmental limits, traits, and optional dependency info. |
| `config` | dict | Rule thresholds and any extra settings for exclusion. |

## Outputs

The function returns a dictionary with two keys:

| Key | Type | Description |
|------|------|-------------|
| `candidate_species` | list[int] | Species IDs that passed all rules. Used for scoring or other modules. |
| `excluded_species` | list[dict] | Species that failed one or more rules, with reasons listed. |

## Return Structure

```json
{
  "candidate_species": [1, 3, 8, 11],
  "excluded_species": [
    {
      "species_id": 14,
      "species_name": "Casuarina equisetifolia",
      "reasons": ["rainfall_below_min", "soil_texture_not_supported"]
    }
  ]
}
```
# Task 5 – Dummy Pass-Through Function

This task implements a simple dummy version of the exclusion rules module.
The purpose is to set up the basic structure and interface so that the
scoring module and tests can call the function.

At this stage, no real exclusion logic is applied.

---

## Behaviour

The dummy implementation of `run_exclusion_rules` will:

- accept `farm_data`, `species_data`, and `config`
- ignore all rule logic for now
- treat all species as valid candidates
- return:
  - a list of candidate species IDs
  - an empty list of excluded species

This allows the pipeline to run end-to-end while the real exclusion rules
are developed in later tasks.

---

## Output Format

The function returns a dictionary with two keys:

- `candidate_ids`: list of species IDs
- `excluded_species`: empty list

Example:

```json
{
  "candidate_ids": [1, 2, 3],
  "excluded_species": []
}
```
# Task 6 – Decision Tree vs Rule-Based Model Comparison

This notebook compares two possible approaches for implementing the exclusion rules:
a rule-based model and a decision tree model.

The goal is to evaluate flexibility, maintainability, and suitability for future rule changes,
rather than to build a production-ready system.


## Background

The exclusion rules are used to filter out unsuitable species before scoring.
In this project, the rules may change over time and new rules may be added as more data becomes available.

Because of this, flexibility and ease of updates are important design considerations.


## Example Exclusion Rules (Small Sample)

For this comparison, a small set of example exclusion rules is used:

- Rainfall must be within a minimum and maximum range
- Soil type must be supported by the species
- A habitat flag (e.g. coastal) must be satisfied
- Species dependencies may exist (assumed for now)



```python
# Rule-based prototype (conceptual example)

def rule_based_exclusion(farm, species):
    reasons = []

    if farm["rainfall"] < species["rainfall_min"]:
        reasons.append("rainfall below minimum")

    if farm["soil_type"] not in species["allowed_soil_types"]:
        reasons.append("soil type not supported")

    if species.get("requires_coastal") and not farm.get("is_coastal"):
        reasons.append("habitat requirement not met")

    if reasons:
        return False, reasons

    return True, []

```

### Rule-Based Approach – Observations

- Each rule is independent
- New rules can be added without changing existing ones
- Missing data can be handled by skipping rules
- Failure reasons are easy to record



```python
# Decision tree prototype (conceptual example)

def decision_tree_exclusion(farm, species):
    if farm["rainfall"] < species["rainfall_min"]:
        return False, "rainfall below minimum"

    if farm["soil_type"] not in species["allowed_soil_types"]:
        return False, "soil type not supported"

    if species.get("requires_coastal") and not farm.get("is_coastal"):
        return False, "habitat requirement not met"

    return True, "passed all checks"

```

### Decision Tree Approach – Observations

- Rules are evaluated in a fixed order
- The structure becomes harder to manage as rules increase
- Updating logic often requires changing the tree structure
- Less flexible when rules are frequently added or removed


## Comparison of Rule-Based and Decision Tree Approaches

Both approaches can be used to implement exclusion logic, but they differ in structure and behaviour.

### Maintainability
In a rule-based approach, each rule is implemented as a separate check.
This makes the code easier to read and maintain, especially when the number of rules grows.
In contrast, a decision tree requires changes to the tree structure when new rules are added,
which can make maintenance more difficult over time.

### Ease of Updates
Rule-based logic allows new rules to be added or removed with minimal impact on existing rules.
Each rule can be updated independently.
With a decision tree, updates often require restructuring the tree or reordering conditions,
which increases the risk of introducing errors.

### Transparency and Debugging
Rule-based models are generally easier to understand and debug.
It is clear which rule caused a species to be excluded, and multiple failure reasons can be recorded.
Decision trees follow a fixed path, so only the first failing condition is usually captured,
which makes detailed explanations harder.

### Handling Missing Data
Rule-based logic can easily skip rules when required data is missing,
without excluding the species.
In a decision tree, missing data often needs special handling at each node,
which adds complexity to the implementation.

### Future Rule Growth and Dependencies
As more rules and species dependencies are introduced,
a rule-based approach scales more naturally.
Decision trees can become large and rigid as more conditions are added,
making them harder to modify when requirements change.

### Overall Fit for This Project
Because exclusion rules are expected to change over time and may depend on incomplete data,
the rule-based approach provides better flexibility and long-term maintainability for this project.


## Recommendation

Based on this comparison, the rule-based approach is more suitable for the exclusion rules module.

The main reasons are:
- Rules are expected to change and grow over time
- Each rule can be added or updated independently
- Failure reasons are easy to track and explain

For these reasons, a rule-based model provides better flexibility and maintainability for this project.

# Task 7 – Exclusion Rules Core Logic

This notebook documents the core exclusion logic used to filter unsuitable species for a given farm before suitability scoring (MCDA).

The goal is to provide a flexible, data-driven exclusion engine that:
- Uses the project datasets (farms, species, dependencies)
- Produces clear exclusion reasons
- Can be extended when new rules or data are added

## Input datasets

The exclusion module works with three datasets:

### Farms (`farms.xlsx`)
Each farm provides:
- rainfall_mm
- temperature_celsius
- elevation_m
- ph
- soil_texture
- costal (coastal flag)
- riprian (riparian flag)

### Species (`species.xlsx`)
Each species provides:
- rainfall_mm_min, rainfall_mm_max
- temperature_celsius_min, temperature_celsius_max
- elevation_m_min, elevation_m_max
- ph_min, ph_max
- preferred_soil_texture
- costal, riparian
- species_id, species_name, species_common_name

### Species Dependencies (`Species dependencies.xlsx`)
This file lists species that require other species to be present.
The current file contains trailing spaces in column names and may be updated by the PO later.
The core logic handles this in a robust way.

## Core exclusion rules

All exclusion rules are defined in a central rule list.
Each rule compares a farm attribute against a species limit.

Examples:
- Farm rainfall must be >= species rainfall minimum
- Farm soil texture must be allowed by the species
- Farm pH must fall within the species pH range

Rules are evaluated dynamically so new rules can be added without rewriting the main logic.

## Handling missing data

If either the farm or species does not have a value required by a rule:
- The rule is skipped
- The species is NOT excluded
- No reason is recorded

This prevents incorrect exclusions caused by incomplete data.

## Dependency handling

Some species depend on other species (for example host plants).

Because the current dependency data may not be complete or fully reliable,
dependency filtering is controlled by configuration.

By default:
    config["dependency"]["enabled"] = False

This means dependency rules are ignored unless explicitly enabled.
When more reliable dependency data becomes available, this flag can be turned on
without changing the core logic.

## Output format

The exclusion engine returns:

- candidate_ids: species that passed all exclusion rules
- excluded_species: species that failed, with human-readable reasons

Example:

```json
{
  "candidate_ids": [1, 5, 7],
  "excluded_species": [
    {
      "species_id": 14,
      "species_name": "Casuarina equisetifolia",
      "species_common_name": "Coastal she-oak",
      "reasons": ["excluded: rainfall below minimum"]
    }
  ]
}
```

This output is designed to plug directly into the MCDA scoring module.

## Summary

Task 7 delivers a production-ready exclusion core that:
- Uses real project datasets
- Applies environmental, soil and habitat filters
- Supports optional dependency filtering
- Produces clear exclusion explanations
- Integrates cleanly with the suitability scoring pipeline

## Summary

Task 7 delivers a production-ready exclusion core that:
- Uses real project datasets
- Applies environmental, soil and habitat filters
- Supports optional dependency filtering
- Produces clear exclusion explanations
- Integrates cleanly with the suitability scoring pipeline
