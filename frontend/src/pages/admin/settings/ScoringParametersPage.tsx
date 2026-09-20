import { FormEvent, useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";

import { useAuth } from "../../../contexts/AuthContext";
import { getAllSpecies, Species } from "../../../utils/speciesApi";
import {
  createParameter,
  deleteParameter,
  getAllParameters,
  Parameter,
  ParameterPayload,
  updateParameter,
} from "../../../utils/parametersApi";

type ModalMode = "create" | "edit" | null;

const emptyForm: ParameterPayload = {
  species_id: 0,
  feature: "",
  score_method: "",
  weight: 0,
  trap_left_tol: null,
  trap_right_tol: null,
};

const SCORE_METHODS = [
  "cat_compatibility",
  "cat_exact",
  "num_range",
  "trapezoid",
] as const;

const FEATURES = [
  "elevation_m",
  "ph",
  "rainfall_mm",
  "soil_texture",
  "temperature_celsius",
] as const;

function buildParameterPayload(param: Parameter): ParameterPayload {
  return {
    species_id: param.species_id,
    feature: param.feature,
    score_method: param.score_method ?? "",
    weight: param.weight ?? 0,
    trap_left_tol: param.trap_left_tol,
    trap_right_tol: param.trap_right_tol,
  };
}

function ScoringParametersPage() {
  const { getAccessToken } = useAuth();

  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [species, setSpecies] = useState<Species[]>([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<ParameterPayload>(emptyForm);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = getAccessToken();

      if (!token) {
        setError("You must be logged in as admin to view scoring parameters.");
        return;
      }

      const [paramData, speciesData] = await Promise.all([
        getAllParameters(token),
        getAllSpecies(token),
      ]);

      setParameters(paramData);
      setSpecies([...speciesData].sort((a, b) => a.name.localeCompare(b.name)));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load scoring parameters"
      );
    } finally {
      setLoading(false);
    }
  }, [getAccessToken]);

  function getSpeciesName(speciesId: number): string {
    const found = species.find(s => s.id === speciesId);
    return found ? found.name : `Species ${speciesId}`;
  }

  function openCreateModal() {
    setError(null);
    setEditingId(null);
    setFormData(emptyForm);
    setModalMode("create");
    setFormError(null);
  }

  function openEditModal(param: Parameter) {
    setError(null);
    setEditingId(param.id);
    setFormData(buildParameterPayload(param));
    setModalMode("edit");
    setFormError(null);
  }

  function closeModal() {
    setFormError(null);
    setError(null);
    setSaving(false);
    setModalMode(null);
    setEditingId(null);
    setFormData(emptyForm);
  }

  function updateFormField<K extends keyof ParameterPayload>(
    field: K,
    value: ParameterPayload[K]
  ) {
    setFormData(current => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const token = getAccessToken();

    if (!token) {
      setError("You must be logged in as admin to manage scoring parameters.");
      return;
    }

    if (formData.species_id === 0) {
      setFormError("Please select a species.");
      return;
    }

    try {
      setSaving(true);
      setError(null);

      if (modalMode === "create") {
        await createParameter(formData, token);
        toast.success("Scoring parameter created successfully");
      }

      if (modalMode === "edit" && editingId !== null) {
        const updatePayload = {
          species_id: formData.species_id,
          feature: formData.feature,
          score_method: formData.score_method,
          trap_left_tol: formData.trap_left_tol,
          trap_right_tol: formData.trap_right_tol,
        };
        await updateParameter(editingId, updatePayload, token);
        toast.success("Scoring parameter updated successfully");
      }

      closeModal();
      await loadData();
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Failed to save scoring parameter.";
      setFormError(message);
      setError(null);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    const token = getAccessToken();

    if (!token) {
      setError("You must be logged in as admin to delete scoring parameters.");
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete this scoring parameter?"
    );

    if (!confirmed) return;

    try {
      setError(null);
      await deleteParameter(id, token);
      toast.success("Scoring parameter deleted successfully");
      await loadData();
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Failed to delete scoring parameter";
      toast.error(message);
    }
  }

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return (
    <>
      <Helmet>
        <title>Admin | Scoring Parameters</title>
      </Helmet>

      <nav className="admin-back-nav">
        <Link to="/admin/settings/weighting" className="admin-back-link">
          &larr; Back to Weighting Hub
        </Link>
      </nav>

      <section className="admin-page-card">
        <div className="admin-parameters-header">
          <div>
            <h2>Scoring Parameters</h2>
            <p>
              Manage the scoring parameters used by the recommendation model for
              each species.
            </p>
          </div>

          <button
            type="button"
            className="btn-primary"
            onClick={openCreateModal}
          >
            Add Parameter
          </button>
        </div>

        {loading && <p>Loading scoring parameters...</p>}

        {error && <p className="admin-error-message">{error}</p>}

        {!loading && !error && parameters.length === 0 && (
          <p>No scoring parameters found.</p>
        )}

        {!loading && parameters.length > 0 && (
          <div className="admin-table-wrapper">
            <table className="admin-parameters-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Species</th>
                  <th>Feature</th>
                  <th>Score Method</th>
                  <th>Weight</th>
                  <th>Trap Left Tol</th>
                  <th>Trap Right Tol</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {parameters.map(param => (
                  <tr key={param.id}>
                    <td>{param.id}</td>
                    <td>{getSpeciesName(param.species_id)}</td>
                    <td>{param.feature}</td>
                    <td>{param.score_method ?? "—"}</td>
                    <td>
                      {param.weight != null
                        ? Number(param.weight.toFixed(4))
                        : "—"}
                    </td>
                    <td>{param.trap_left_tol ?? "—"}</td>
                    <td>{param.trap_right_tol ?? "—"}</td>
                    <td>
                      <button
                        type="button"
                        className="admin-action-btn"
                        onClick={() => openEditModal(param)}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="admin-action-btn admin-action-danger"
                        onClick={() => void handleDelete(param.id)}
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
          >
            <div className="admin-modal-header">
              <div>
                <h3>
                  {modalMode === "create"
                    ? "Add Scoring Parameter"
                    : "Edit Scoring Parameter"}
                </h3>
                <p>
                  Configure a scoring parameter for the recommendation model.
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

                <label>
                  Species
                  <select
                    required
                    value={formData.species_id}
                    onChange={event =>
                      updateFormField("species_id", Number(event.target.value))
                    }
                  >
                    <option value={0} disabled>
                      Select a species
                    </option>
                    {species.map(s => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Feature
                  <select
                    required
                    value={formData.feature}
                    onChange={event =>
                      updateFormField("feature", event.target.value)
                    }
                  >
                    <option value="" disabled>
                      Select a feature
                    </option>
                    {FEATURES.map(feature => (
                      <option key={feature} value={feature}>
                        {feature}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="admin-form-section">
                <h4>Scoring Configuration</h4>

                <div className="admin-form-grid">
                  <label>
                    Score Method
                    <select
                      required
                      value={formData.score_method}
                      onChange={event => {
                        updateFormField("score_method", event.target.value);
                        if (event.target.value !== "trapezoid") {
                          updateFormField("trap_left_tol", null);
                          updateFormField("trap_right_tol", null);
                        }
                      }}
                    >
                      <option value="" disabled>
                        Select a method
                      </option>
                      {SCORE_METHODS.map(method => (
                        <option key={method} value={method}>
                          {method}
                        </option>
                      ))}
                    </select>
                  </label>

                  {formData.score_method === "trapezoid" && (
                    <label>
                      Trap Left Tolerance
                      <input
                        type="number"
                        step="1"
                        min="0"
                        max="5000"
                        placeholder="Optional"
                        value={formData.trap_left_tol ?? ""}
                        onChange={event =>
                          updateFormField(
                            "trap_left_tol",
                            event.target.value === ""
                              ? null
                              : Number(event.target.value)
                          )
                        }
                      />
                    </label>
                  )}

                  {formData.score_method === "trapezoid" && (
                    <label>
                      Trap Right Tolerance
                      <input
                        type="number"
                        step="1"
                        min="0"
                        max="5000"
                        placeholder="Optional"
                        value={formData.trap_right_tol ?? ""}
                        onChange={event =>
                          updateFormField(
                            "trap_right_tol",
                            event.target.value === ""
                              ? null
                              : Number(event.target.value)
                          )
                        }
                      />
                    </label>
                  )}
                </div>
              </div>

              <div className="admin-modal-actions">
                <button
                  type="button"
                  className="admin-action-btn"
                  onClick={closeModal}
                >
                  Cancel
                </button>

                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving ? "Saving..." : "Save Parameter"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default ScoringParametersPage;
