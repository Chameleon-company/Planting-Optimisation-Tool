# Exclusion Rules Output Schema

This section defines the output of the exclusion rules module.
The purpose of this module is to filter out species that fail hard constraints
before MCDA scoring is applied.

The exclusion rules module is called by the scoring pipeline and does not produce
the final recommender output.

---

## Exclusion Module Output

The exclusion function returns a dictionary with two fields:

* `candidate_ids` *(list[int], required)*  
  List of species IDs that passed all exclusion rules and should be scored
  by the MCDA engine.

* `excluded_species` *(list[object], required)*  
  List of species that were excluded, along with the reasons for exclusion.

---

## excluded_species Schema

Each item in `excluded_species` contains:

* `species_id` *(int, required)*  
  ID from the species table.

* `species_name` *(string, required)*  
  Scientific name.

* `species_common_name` *(string, optional)*  
  Common name or label, if available.

* `reasons` *(list[string], required)*  
  Human-readable explanations for why the species was excluded.
  Each reason should clearly state the limiting factor and use plain language.

### Reason wording guidelines

Reasons should:
- begin with `excluded:`
- explicitly name the limiting factor
- be short and suitable for UI display

Examples:
- `excluded: rainfall below minimum`
- `excluded: rainfall above maximum`
- `excluded: soil type not supported`
- `excluded: no suitable host plant`

---

## JSON Example (Exclusion Module Output Only)

```json
{
  "candidate_ids": [1, 5, 10],

  "excluded_species": [
    {
      "species_id": 14,
      "species_name": "Casuarina equisetifolia",
      "species_common_name": "Coastal she-oak",
      "reasons": ["excluded: rainfall below minimum"]
    },
    {
      "species_id": 20,
      "species_name": "Vanilla planifolia",
      "species_common_name": "Vanilla",
      "reasons": ["excluded: no suitable host plant"]
    }
  ]
}
```