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