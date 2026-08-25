import { FormEvent, useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";

import { useAuth } from "../../../contexts/AuthContext";
import { getAllSpecies, Species } from "../../../utils/speciesApi";

type ModalMode = "create" | "edit" | null;

type ExclusionOperator =
  | "<"
  | ">"
  | "<="
  | ">="
  | "=="
  | "!="
  | "in_set"
  | "not_in_set";

interface ExclusionRuleDraft {
  id: number;
  species_id: number;
  feature: string;
  operator: ExclusionOperator;
  value: string;
  reason: string;
}

interface ExclusionRuleFormData {
  species_id: number;
  feature: string;
  operator: ExclusionOperator;
  value: string;
  reason: string;
}

const emptyForm: ExclusionRuleFormData = {
  species_id: 0,
  feature: "",
  operator: "<",
  value: "",
  reason: "",
};

const OPERATORS: ExclusionOperator[] = [
  "<",
  ">",
  "<=",
  ">=",
  "==",
  "!=",
  "in_set",
  "not_in_set",
];

const FEATURE_SUGGESTIONS = [
  "elevation_m",
  "ph",
  "rainfall_mm",
  "soil_texture",
  "temperature_celsius",
];

function ExclusionRulesPage() {
  const { getAccessToken } = useAuth();

  const [species, setSpecies] = useState<Species[]>([]);
  const [draftRules, setDraftRules] = useState<ExclusionRuleDraft[]>([]);

  const [speciesLoading, setSpeciesLoading] = useState(true);
  const [speciesError, setSpeciesError] = useState<string | null>(null);

  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<ExclusionRuleFormData>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  const loadSpecies = useCallback(async () => {
    try {
      setSpeciesLoading(true);
      setSpeciesError(null);

      const token = getAccessToken();

      if (!token) {
        setSpeciesError(
          "You must be logged in as admin to configure exclusion rules."
        );
        return;
      }

      const speciesData = await getAllSpecies(token);

      setSpecies([...speciesData].sort((a, b) => a.name.localeCompare(b.name)));
    } catch (error) {
      setSpeciesError(
        error instanceof Error ? error.message : "Failed to load species."
      );
    } finally {
      setSpeciesLoading(false);
    }
  }, [getAccessToken]);

  useEffect(() => {
    void loadSpecies();
  }, [loadSpecies]);

  function getSpeciesName(speciesId: number): string {
    const matchingSpecies = species.find(item => item.id === speciesId);

    return matchingSpecies ? matchingSpecies.name : `Species ${speciesId}`;
  }

  function updateFormField<K extends keyof ExclusionRuleFormData>(
    field: K,
    value: ExclusionRuleFormData[K]
  ) {
    setFormData(current => ({
      ...current,
      [field]: value,
    }));
  }

  function openCreateModal() {
    setEditingId(null);
    setFormData(emptyForm);
    setFormError(null);
    setModalMode("create");
  }

  function openEditModal(rule: ExclusionRuleDraft) {
    setEditingId(rule.id);
    setFormData({
      species_id: rule.species_id,
      feature: rule.feature,
      operator: rule.operator,
      value: rule.value,
      reason: rule.reason,
    });
    setFormError(null);
    setModalMode("edit");
  }

  function closeModal() {
    setModalMode(null);
    setEditingId(null);
    setFormData(emptyForm);
    setFormError(null);
  }

  function validateForm(): string | null {
    if (formData.species_id === 0) {
      return "Please select a species.";
    }

    if (!formData.feature.trim()) {
      return "Please enter a feature.";
    }

    if (!formData.value.trim()) {
      return "Please enter a rule value.";
    }

    if (!formData.reason.trim()) {
      return "Please enter a reason for the exclusion.";
    }

    return null;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationError = validateForm();

    if (validationError) {
      setFormError(validationError);
      return;
    }

    if (modalMode === "create") {
      const nextId =
        draftRules.length === 0
          ? 1
          : Math.max(...draftRules.map(rule => rule.id)) + 1;

      setDraftRules(current => [
        ...current,
        {
          id: nextId,
          ...formData,
          feature: formData.feature.trim(),
          value: formData.value.trim(),
          reason: formData.reason.trim(),
        },
      ]);
    }

    if (modalMode === "edit" && editingId !== null) {
      setDraftRules(current =>
        current.map(rule =>
          rule.id === editingId
            ? {
                ...rule,
                ...formData,
                feature: formData.feature.trim(),
                value: formData.value.trim(),
                reason: formData.reason.trim(),
              }
            : rule
        )
      );
    }

    closeModal();
  }

  function handleDelete(id: number) {
    setDraftRules(current => current.filter(rule => rule.id !== id));
  }

  return (
    <>
      <Helmet>
        <title>Exclusion Rules | Planting Optimisation Tool</title>
      </Helmet>

      {/* <nav className="admin-back-nav">
        <Link to="/admin" className="admin-back-link">
          &larr; Back to Dashboard
        </Link>
      </nav> */}

      <section className="admin-page-card">
        <div className="admin-parameters-header">
          <div>
            <h2>Exclusion Rules</h2>
            <p>
              Define environmental conditions that make a species unsuitable for
              planting.
            </p>
          </div>

          <button
            type="button"
            className="btn-primary"
            onClick={openCreateModal}
            disabled={speciesLoading || Boolean(speciesError)}
          >
            Add Exclusion Rule
          </button>
        </div>

        {speciesLoading && <p>Loading species...</p>}

        {speciesError && <p className="admin-error-message">{speciesError}</p>}

        {!speciesLoading && !speciesError && draftRules.length === 0 && (
          <p>No exclusion rules have been configured.</p>
        )}

        {draftRules.length > 0 && (
          <div className="admin-table-wrapper">
            <table className="admin-parameters-table">
              <thead>
                <tr>
                  <th>Species</th>
                  <th>Feature</th>
                  <th>Operator</th>
                  <th>Value</th>
                  <th>Reason</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {draftRules.map(rule => (
                  <tr key={rule.id}>
                    <td>{getSpeciesName(rule.species_id)}</td>
                    <td>{rule.feature}</td>
                    <td>{rule.operator}</td>
                    <td>{rule.value}</td>
                    <td>{rule.reason}</td>
                    <td>
                      <button
                        type="button"
                        className="admin-action-btn"
                        onClick={() => openEditModal(rule)}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="admin-action-btn admin-action-danger"
                        onClick={() => handleDelete(rule.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {modalMode && (
        <div className="admin-modal-backdrop">
          <div
            className="admin-parameters-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="exclusion-rule-modal-title"
          >
            <div className="admin-modal-header">
              <div>
                <h3 id="exclusion-rule-modal-title">
                  {modalMode === "create"
                    ? "Add Exclusion Rule"
                    : "Edit Exclusion Rule"}
                </h3>
                <p>
                  Configure the condition that excludes a species from a
                  recommendation.
                </p>
              </div>

              <button
                type="button"
                className="admin-modal-close"
                onClick={closeModal}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <form className="admin-parameters-form" onSubmit={handleSubmit}>
              {formError && (
                <div className="admin-error-message" role="alert">
                  {formError}
                </div>
              )}

              <div className="admin-form-section">
                <h4>Species and Feature</h4>

                <div className="admin-form-grid">
                  <label>
                    Species
                    <select
                      required
                      value={formData.species_id}
                      onChange={event =>
                        updateFormField(
                          "species_id",
                          Number(event.target.value)
                        )
                      }
                    >
                      <option value={0} disabled>
                        Select a species
                      </option>

                      {species.map(item => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Feature
                    <input
                      type="text"
                      required
                      list="exclusion-feature-options"
                      placeholder="e.g. rainfall_mm"
                      value={formData.feature}
                      onChange={event =>
                        updateFormField("feature", event.target.value)
                      }
                    />
                    <datalist id="exclusion-feature-options">
                      {FEATURE_SUGGESTIONS.map(feature => (
                        <option key={feature} value={feature} />
                      ))}
                    </datalist>
                  </label>
                </div>
              </div>

              <div className="admin-form-section">
                <h4>Rule Condition</h4>

                <div className="admin-form-grid">
                  <label>
                    Operator
                    <select
                      required
                      value={formData.operator}
                      onChange={event =>
                        updateFormField(
                          "operator",
                          event.target.value as ExclusionOperator
                        )
                      }
                    >
                      {OPERATORS.map(operator => (
                        <option key={operator} value={operator}>
                          {operator}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Value
                    <input
                      type="text"
                      required
                      placeholder={
                        formData.operator === "in_set" ||
                        formData.operator === "not_in_set"
                          ? "e.g. clay, loam, sandy"
                          : "e.g. 1500"
                      }
                      value={formData.value}
                      onChange={event =>
                        updateFormField("value", event.target.value)
                      }
                    />
                  </label>
                </div>
              </div>

              <div className="admin-form-section">
                <h4>Explanation</h4>

                <label>
                  Reason
                  <input
                    type="text"
                    required
                    placeholder="e.g. Rainfall is below the survival threshold"
                    value={formData.reason}
                    onChange={event =>
                      updateFormField("reason", event.target.value)
                    }
                  />
                </label>
              </div>

              <div className="admin-modal-actions">
                <button
                  type="button"
                  className="admin-action-btn"
                  onClick={closeModal}
                >
                  Cancel
                </button>

                <button type="submit" className="btn-primary">
                  {modalMode === "create" ? "Add Rule" : "Update Rule"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default ExclusionRulesPage;
