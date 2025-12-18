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
