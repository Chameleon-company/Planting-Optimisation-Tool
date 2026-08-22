import { FormEvent, useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";

import { useAuth } from "../../../contexts/AuthContext";
import {
  createExclusionRule,
  deleteExclusionRule,
  ExclusionOperator,
  ExclusionRule,
  ExclusionRuleValue,
  getAllExclusionRules,
  updateExclusionRule,
} from "../../../utils/exclusionRulesApi";
import { getSpeciesDropdown, SpeciesDropdown } from "../../../utils/speciesApi";

type ModalMode = "create" | "edit" | null;

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

function formatRuleValue(value: ExclusionRuleValue): string {
  if (Array.isArray(value)) {
    return value.join(", ");
  }

  return String(value);
}

function parseRuleValue(
  value: string,
  operator: ExclusionOperator
): ExclusionRuleValue {
  const trimmedValue = value.trim();

  if (operator === "in_set" || operator === "not_in_set") {
    return trimmedValue
      .split(",")
      .map(item => item.trim())
      .filter(Boolean);
  }

  const numericValue = Number(trimmedValue);

  if (trimmedValue !== "" && Number.isFinite(numericValue)) {
    return numericValue;
  }

  return trimmedValue;
}

function ExclusionRulesPage() {
  const { getAccessToken } = useAuth();

  const [species, setSpecies] = useState<SpeciesDropdown[]>([]);
  const [rules, setRules] = useState<ExclusionRule[]>([]);

  const [pageLoading, setPageLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);

  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<ExclusionRuleFormData>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  const loadPageData = useCallback(async () => {
    try {
      setPageLoading(true);
      setPageError(null);

      const token = getAccessToken();

      if (!token) {
        setPageError(
          "You must be logged in as admin to configure exclusion rules."
        );
        return;
      }

      const [speciesData, rulesData] = await Promise.all([
        getSpeciesDropdown(token),
        getAllExclusionRules(token),
      ]);

      setSpecies([...speciesData].sort((a, b) => a.name.localeCompare(b.name)));

      setRules(rulesData);
    } catch (error) {
      setPageError(
        error instanceof Error
          ? error.message
          : "Failed to load exclusion rules."
      );
    } finally {
      setPageLoading(false);
    }
  }, [getAccessToken]);

  useEffect(() => {
    void loadPageData();
  }, [loadPageData]);

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

  function openEditModal(rule: ExclusionRule) {
    setEditingId(rule.id);

    setFormData({
      species_id: rule.species_id,
      feature: rule.feature,
      operator: rule.operator,
      value: formatRuleValue(rule.value),
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

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationError = validateForm();

    if (validationError) {
      setFormError(validationError);
      return;
    }

    const token = getAccessToken();

    if (!token) {
      setFormError("You must be logged in as admin to save exclusion rules.");
      return;
    }

    const payload = {
      species_id: formData.species_id,
      feature: formData.feature.trim(),
      operator: formData.operator,
      value: parseRuleValue(formData.value, formData.operator),
      reason: formData.reason.trim(),
    };

    try {
      setFormError(null);

      if (modalMode === "create") {
        const createdRule = await createExclusionRule(payload, token);

        setRules(current => [...current, createdRule]);
      }

      if (modalMode === "edit" && editingId !== null) {
        const updatedRule = await updateExclusionRule(
          editingId,
          payload,
          token
        );

        setRules(current =>
          current.map(rule => (rule.id === editingId ? updatedRule : rule))
        );
      }

      closeModal();
    } catch (error) {
      setFormError(
        error instanceof Error
          ? error.message
          : "Failed to save exclusion rule."
      );
    }
  }

  async function handleDelete(id: number) {
    const token = getAccessToken();

    if (!token) {
      setPageError("You must be logged in as admin to delete exclusion rules.");
      return;
    }

    try {
      setPageError(null);

      await deleteExclusionRule(id, token);

      setRules(current => current.filter(rule => rule.id !== id));
    } catch (error) {
      setPageError(
        error instanceof Error
          ? error.message
          : "Failed to delete exclusion rule."
      );
    }
  }

  return (
    <>
      <Helmet>
        <title>Exclusion Rules | Planting Optimisation Tool</title>
      </Helmet>

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
            disabled={pageLoading || Boolean(pageError)}
          >
            Add Exclusion Rule
          </button>
        </div>

        {pageLoading && <p>Loading exclusion rules...</p>}

        {pageError && <p className="admin-error-message">{pageError}</p>}

        {!pageLoading && !pageError && rules.length === 0 && (
          <p>No exclusion rules have been configured.</p>
        )}

        {!pageLoading && rules.length > 0 && (
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
                {rules.map(rule => (
                  <tr key={rule.id}>
                    <td>{getSpeciesName(rule.species_id)}</td>
                    <td>{rule.feature}</td>
                    <td>{rule.operator}</td>
                    <td>{formatRuleValue(rule.value)}</td>
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
                        onClick={() => void handleDelete(rule.id)}
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

            <form
              className="admin-parameters-form"
              onSubmit={event => void handleSubmit(event)}
            >
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
