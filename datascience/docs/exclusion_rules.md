# Exclusion Rules Module

This section documents the core exclusion logic used to filter unsuitable species for a given farm before suitability scoring (MCDA).

The goal is to provide a flexible, data-driven exclusion engine that:
- Uses the project datasets (farms, species, dependencies)
- Produces clear exclusion reasons
- Can be extended when new rules or data are added

## Function Name

`run_exclusion_rules()`

The function takes farm-level data, the evaluated species list, and two lookup
tables for rule checks and biological dependencies as input. It returns the list of surviving candidate species and the list of excluded
species with reasons.


## Inputs

| Name | Type | Description |
|------|------|-------------|
| `farm_data` | dict | Data for one farm, including rainfall, temperature, soil, habitat flags, and other conditions. |
| `all_species` | list[Any] | Species records to evaluate against the exclusion rules. |
| `rules_lookup` | dict[int, list[Any]] | Species-specific exclusion rules keyed by species ID. |
| `dep_lookup` | dict[int, list[int]] | Species dependency mapping keyed by species ID. |


## Outputs

The function returns a dictionary with two keys:

| Key | Type | Description |
|------|------|-------------|
| `candidate_ids` | list[int] | Species IDs that passed all rules. Used for scoring or other modules. |
| `excluded_species` | list[dict] | Species that failed one or more rules, with reasons listed. Rule-based exclusions include species metadata; dependency exclusions include only `id` and `reasons`. |

Example:

```json
{
  "candidate_ids": [1, 2, 3],
  "excluded_species": [
    {
      "id": 14,
      "species_name": "Casuarina equisetifolia",
      "species_common_name": "Coastal she-oak",
      "reasons": ["excluded: rainfall below minimum, farm value = 420"]
    },
    {
      "id": 18,
      "species_name": "Casuarina equisetifolia",
      "species_common_name": "Coastal she-oak",
      "reasons": ["excluded: no suitable host/partner plant available"]
    }
  ]
}
```

This output is designed to plug directly into the MCDA scoring module.


## Core exclusion rules

Rules are evaluated per species using the supplied `rules_lookup`.
Each rule compares a farm attribute against a rule feature and value.

Examples:
- Farm rainfall must satisfy the rule operator against the rule value
- Farm soil texture must be supported by the species rule
- Farm pH must fall within the species pH range

Rules are evaluated dynamically so new rules can be added without rewriting the main logic.

## Handling missing data

The current implementation handles incomplete data as follows:
- if the farm value is missing, the species is excluded for that rule
- if the rule threshold is missing, the species passes that rule
- if the farm value cannot be converted to a numeric value, the species is excluded for numeric comparisons
- if the rule threshold cannot be converted to a numeric value, the species passes numeric comparisons
- if the rule feature is missing, the rule is skipped entirely

This prevents incorrect exclusions caused by incomplete data.

## Dependency handling

Some species depend on other species (for example host plants).

The current implementation always applies dependency filtering after the main
rule checks. A species remains a candidate only if at least one required partner
species is still present in the surviving candidate set.


## Dummy Pass-Through

Passing empty dictionaries for `rules_lookup` and `dep_lookup` allows the species to pass thorough without exclusion.


# Decision Tree vs Rule-Based Model Comparison

This section compares two possible approaches for implementing the exclusion rules:
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