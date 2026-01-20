"""
Task 7 - Exclusion Rules Core Logic (API-aligned: id)

Key points
- Uses "id" for both farm and species primary keys (API aligned)
- Rules are config-driven via RULES list (easy to add/remove rules)
- Column mapping is centralised (easy to adapt to renamed columns)
- Missing data does NOT exclude species (skip rule safely)
- Dependency check is optional via config["dependency"]["enabled"] (default False)
- Dependency headers may contain trailing spaces (handled by stripping keys)

Updates included:
- Task 8: Add annotation logic (more specific, readable reasons)
- Task 9: Handle missing data (explicitly enforced; no exclusion on missing values)
- Task 10: Make it configurable (support direct column names in config rules)

# NOTES:
# Exclusion_criteria.xlsx includes some narrative/text rules.
# In this sprint we do not parse text-only rules.
# Exclusions are driven by structured datasets only.
# Missing values are skipped to avoid accidental exclusion when data is incomplete.

# Notes on missing vs valid values handling:
#
# - Blank / NA-like values (e.g. "", "NA", "N/A", "null", None) are treated as MISSING
#   and will cause the rule to be skipped (no exclusion).
#
# - False is considered a VALID value and may trigger exclusion
#   (e.g. habitat flags such as coastal / riparian).
#
# - 0 is considered a VALID numeric value and will be evaluated normally
#   in numeric comparisons (e.g. rainfall, temperature, elevation).
#
# This design avoids accidental exclusion when datasets are incomplete,
# while still respecting explicit negative constraints in the data.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


# ============================================================
# 1) Column mapping (edit here if headers change later)
# ============================================================

FARM_COL = {
    "id": "id",
    "rainfall": "rainfall_mm",
    "temperature": "temperature_celsius",
    "elevation": "elevation_m",
    "ph": "ph",
    "soil": "soil_texture",
    # Optional: if backend adds these later, rules can use them
    "coastal_flag": "costal",
    "riparian_flag": "riparian",
}

SPECIES_COL = {
    "id": "id",
    "species_name": "name",
    "species_common_name": "common_name",
    "rain_min": "rainfall_mm_min",
    "rain_max": "rainfall_mm_max",
    "temp_min": "temperature_celsius_min",
    "temp_max": "temperature_celsius_max",
    "elev_min": "elevation_m_min",
    "elev_max": "elevation_m_max",
    "ph_min": "ph_min",
    "ph_max": "ph_max",
    "soil_pref": "soil_textures",
    # habitat flags
    "coastal_ok": "costal",
    "riparian_ok": "riparian",
}


# ============================================================
# 2) Rules (edit/add rules here later; core flow does NOT change)
# ============================================================

RULES: List[Dict[str, Any]] = [
    {
        "id": "rain_min",
        "farm": "rainfall",
        "op": ">=",
        "species": "rain_min",
        "reason": "excluded: rainfall below minimum",
    },
    {
        "id": "rain_max",
        "farm": "rainfall",
        "op": "<=",
        "species": "rain_max",
        "reason": "excluded: rainfall above maximum",
    },
    {
        "id": "temp_min",
        "farm": "temperature",
        "op": ">=",
        "species": "temp_min",
        "reason": "excluded: temperature below minimum",
    },
    {
        "id": "temp_max",
        "farm": "temperature",
        "op": "<=",
        "species": "temp_max",
        "reason": "excluded: temperature above maximum",
    },
    {
        "id": "elev_min",
        "farm": "elevation",
        "op": ">=",
        "species": "elev_min",
        "reason": "excluded: elevation below minimum",
    },
    {
        "id": "elev_max",
        "farm": "elevation",
        "op": "<=",
        "species": "elev_max",
        "reason": "excluded: elevation above maximum",
    },
    {
        "id": "ph_min",
        "farm": "ph",
        "op": ">=",
        "species": "ph_min",
        "reason": "excluded: pH below minimum",
    },
    {
        "id": "ph_max",
        "farm": "ph",
        "op": "<=",
        "species": "ph_max",
        "reason": "excluded: pH above maximum",
    },
    {
        "id": "soil_texture",
        "farm": "soil",
        "op": "in_set",
        "species": "soil_pref",
        "reason": "excluded: soil texture not supported",
    },
    # Habitat rules: only apply if farm flag == True.
    # If farm flag missing => skip rule safely.
    {
        "id": "coastal_habitat",
        "farm": "coastal_flag",
        "op": "requires_true",
        "species": "coastal_ok",
        "reason": "excluded: not suitable for coastal habitat",
    },
    {
        "id": "riparian_habitat",
        "farm": "riparian_flag",
        "op": "requires_true",
        "species": "riparian_ok",
        "reason": "excluded: not suitable for riparian habitat",
    },
]


# ============================================================
# 3) Dependency model (name-based, flexible parser)
# ============================================================


@dataclass(frozen=True)
class DependencyRule:
    focal_species_name: str
    good_partners: Set[str]
    reason: str = "excluded: no suitable host plant"


def _norm_str(x: Any) -> Optional[str]:
    if _is_missing_value(x):
        return None
    s = str(x).strip()
    return s


# -------------------------------
# Task 9 (clarification): strict missing handling
# -------------------------------
def _is_missing_value(x: Any) -> bool:
    """
    Treat only true missing values as missing.
    - Missing => None / blank string / NA-like strings
    - NOT missing => False / 0 (both are meaningful)
    """
    if x is None:
        return True

    # False is meaningful
    if isinstance(x, bool):
        return False

    # 0 is meaningful
    if isinstance(x, (int, float)):
        return False

    s = str(x).strip()
    if s == "":
        return True

    if s.lower() in {"nan", "none", "na", "n/a", "null"}:
        return True

    return False


def _to_bool(x: Any) -> Optional[bool]:
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        if x == 1:
            return True
        if x == 0:
            return False
        return None

    # New: treat blank/NA-like strings as missing (skip)
    if _is_missing_value(x):
        return None

    s = str(x).strip().lower()
    if s in {"true", "yes", "y", "1"}:
        return True
    if s in {"false", "no", "n", "0"}:
        return False
    return None


def _to_float(x: Any) -> Optional[float]:
    if _is_missing_value(x):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _parse_set(val: Any) -> Optional[Set[str]]:
    """
    Parse soil / partner lists.
    Supports:
      - Iterables: list/tuple/set -> returns set of stripped strings
      - "Loam, Clay" / "Loam;Clay" / "Loam / Clay"
      - single string
    """
    if val is None:
        return None

    # If it's already an iterable of values (but not a string), convert directly
    if isinstance(val, (list, tuple, set)):
        parts = {str(x).strip() for x in val if str(x).strip()}
        return parts

    s = str(val).strip()
    if not s or s.lower() == "nan":
        return None

    for sep in [";", "/", "|"]:
        s = s.replace(sep, ",")

    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return None
    return set(parts)


def _compare(farm_val: Any, op: str, species_val: Any) -> Optional[bool]:
    """
    True  => rule passes
    False => rule fails
    None  => cannot evaluate (missing/invalid) => skip rule

    Task 9: Missing data handling
    - If farm/species value is missing or invalid => return None
    - None => caller will skip the rule (no exclusion)
    """
    if op in {">=", "<=", ">", "<", "=="}:
        fv = _to_float(farm_val)
        sv = _to_float(species_val)
        if fv is None or sv is None:
            return None

        if op == ">=":
            return fv >= sv
        if op == "<=":
            return fv <= sv
        if op == ">":
            return fv > sv
        if op == "<":
            return fv < sv
        if op == "==":
            return fv == sv

    if op == "in_set":
        fv = _norm_str(farm_val)
        allowed = _parse_set(species_val)
        if fv is None or allowed is None:
            return None
        allowed_lower = {a.lower() for a in allowed}
        return fv.lower() in allowed_lower

    if op == "requires_true":
        f = _to_bool(farm_val)
        if f is None:
            return None
        if f is False:
            return True
        s = _to_bool(species_val)
        if s is None:
            return None
        return s is True

    return None


# -------------------------------
# Task 10: Configurable columns
# -------------------------------
def _resolve_farm_col(rule: Dict[str, Any]) -> Optional[str]:
    """
    Task 10:
    Allow config rules to use direct column names without code changes.
    - If rule["farm_col"] is provided, use it directly.
    - Else resolve via FARM_COL map using rule["farm"] key.
    """
    direct = rule.get("farm_col")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    key = rule.get("farm")
    if not isinstance(key, str):
        return None
    return FARM_COL.get(key)


def _resolve_species_col(rule: Dict[str, Any]) -> Optional[str]:
    """
    Task 10:
    Allow config rules to use direct column names without code changes.
    - If rule["species_col"] is provided, use it directly.
    - Else resolve via SPECIES_COL map using rule["species"] key.
    """
    direct = rule.get("species_col")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    key = rule.get("species")
    if not isinstance(key, str):
        return None
    return SPECIES_COL.get(key)


# -------------------------------
# Task 8: Annotation formatting
# -------------------------------
def _format_reason(
    rule: Dict[str, Any],
    farm_val: Any,
    species_val: Any,
    *,
    include_values: bool,
) -> str:
    """
    Task 8:
    Produce readable reasons.
    - Base reason comes from rule["reason"] (or reason_template if supplied).
    - Optionally include numeric/text values for easier debugging/explanations.
    """
    # Optional template support (still config-driven)
    template = rule.get("reason_template")
    if isinstance(template, str) and template.strip():
        base = template.strip()
        # Light formatting support (safe, best-effort)
        base = base.replace("{farm_val}", str(farm_val))
        base = base.replace("{species_val}", str(species_val))
    else:
        base = str(rule.get("reason", "excluded: rule failed"))

    if not include_values:
        return base

    # Add extra context to make it more readable
    op = rule.get("op", "")
    if op in {">=", "<=", ">", "<", "=="}:
        return f"{base} (farm={farm_val}, threshold={species_val})"

    if op == "in_set":
        return f"{base} (farm={farm_val}, allowed={species_val})"

    if op == "requires_true":
        return f"{base} (farm_flag={farm_val}, species_flag={species_val})"

    return base


def parse_dependencies_rows(
    dep_rows: List[Dict[str, Any]],
    *,
    focal_key: str = "Focal_species",
    partners_key: str = "Good_tree_partners",
    default_reason: str = "excluded: no suitable host plant",
) -> List[DependencyRule]:
    """
    Parse dependency rows in a flexible way.

    The Excel file may have headers like:
        "Good_tree_partners  "
        "Role "
        "Group_notes "
    We strip whitespace from keys so it keeps working if spacing changes.
    """
    rules: List[DependencyRule] = []

    for row in dep_rows:
        clean_row = {str(k).strip(): v for k, v in row.items()}

        focal = _norm_str(clean_row.get(focal_key))
        partners = _parse_set(clean_row.get(partners_key)) or set()
        partners = {p for p in partners if _norm_str(p)}

        if focal and partners:
            rules.append(
                DependencyRule(
                    focal_species_name=focal,
                    good_partners=partners,
                    reason=default_reason,
                )
            )

    return rules


# ============================================================
# 4) Core function (records-based)
# ============================================================


def run_exclusion_rules_records(
    farm_data: Dict[str, Any],
    species_rows: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
    dependencies_rows: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Apply exclusion rules for ONE farm.

    Returns
    -------
    {
      "candidate_ids": [...],
      "excluded_species": [
        {"id", "species_name", "species_common_name", "reasons": [...]}
      ]
    }
    """
    cfg = config or {}

    # -------------------------------
    # Task 10: Configurable rules
    # -------------------------------
    rules = cfg.get("rules") or RULES

    # -------------------------------
    # Task 8: Annotation config
    # -------------------------------
    annotation_cfg = (
        cfg.get("annotation", {}) if isinstance(cfg.get("annotation", {}), dict) else {}
    )
    include_values = bool(annotation_cfg.get("include_values", False))

    excluded: List[Dict[str, Any]] = []
    candidates: List[int] = []

    name_to_id: Dict[str, int] = {}
    id_to_species: Dict[int, Dict[str, Any]] = {}

    for sp in species_rows:
        sp_id_raw = sp.get(SPECIES_COL["id"])
        sp_name = _norm_str(sp.get(SPECIES_COL["species_name"]))

        if sp_id_raw is None:
            continue
        try:
            sp_id = int(sp_id_raw)
        except (TypeError, ValueError):
            continue

        id_to_species[sp_id] = sp
        if sp_name:
            name_to_id[sp_name.lower()] = sp_id

    # 1) Rule evaluation
    for sp_id, sp in id_to_species.items():
        reasons: List[str] = []

        for rule in rules:
            # -------------------------------
            # Task 10: resolve columns
            # -------------------------------
            farm_col = _resolve_farm_col(rule)
            species_col = _resolve_species_col(rule)
            if not farm_col or not species_col:
                continue

            farm_val = farm_data.get(farm_col)
            sp_val = sp.get(species_col)

            # Task 9: missing data => None => skip
            res = _compare(farm_val, str(rule.get("op", "")), sp_val)
            if res is None:
                continue

            if res is False:
                # -------------------------------
                # Task 8: richer annotation
                # -------------------------------
                reasons.append(
                    _format_reason(
                        rule, farm_val, sp_val, include_values=include_values
                    )
                )

        if reasons:
            excluded.append(
                {
                    "id": sp_id,
                    "species_name": sp.get(SPECIES_COL["species_name"]),
                    "species_common_name": sp.get(SPECIES_COL["species_common_name"]),
                    "reasons": reasons,
                }
            )
        else:
            candidates.append(sp_id)

    # 2) Dependency pass (optional)
    dep_enabled = cfg.get("dependency", {}).get("enabled", False)

    if dep_enabled and dependencies_rows:
        dep_rules = parse_dependencies_rows(dependencies_rows)

        candidate_set = set(candidates)
        excluded_by_id = {e["id"]: e for e in excluded}

        for dep in dep_rules:
            focal_id = name_to_id.get(dep.focal_species_name.lower())
            if focal_id is None or focal_id not in candidate_set:
                continue

            partner_ids = {name_to_id.get(p.lower()) for p in dep.good_partners if p}
            partner_ids = {pid for pid in partner_ids if pid is not None}

            if not partner_ids.intersection(candidate_set):
                candidate_set.remove(focal_id)

                # Task 8: dependency reason is already human readable in DependencyRule.reason
                if focal_id in excluded_by_id:
                    excluded_by_id[focal_id]["reasons"].append(dep.reason)
                else:
                    sp = id_to_species.get(focal_id, {})
                    excluded_by_id[focal_id] = {
                        "id": focal_id,
                        "species_name": sp.get(SPECIES_COL["species_name"]),
                        "species_common_name": sp.get(
                            SPECIES_COL["species_common_name"]
                        ),
                        "reasons": [dep.reason],
                    }

        candidates = sorted(candidate_set)
        excluded = list(excluded_by_id.values())

    return {
        "candidate_ids": candidates,
        "excluded_species": excluded,
    }
