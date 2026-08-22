import { FormEvent, useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";

import { useAuth } from "../../../contexts/AuthContext";
import { getAllSpecies, Species } from "../../../utils/speciesApi";

type ModalMode = "create" | "edit" | null;

interface DependencyRuleDraft {
  id: number;
  focal_species_id: number;
  required_partner_id: number;
}

interface DependencyRuleFormData {
  focal_species_id: number;
  required_partner_id: number;
}

const emptyForm: DependencyRuleFormData = {
  focal_species_id: 0,
  required_partner_id: 0,
};

function DependencyRulesPage() {
  const { getAccessToken } = useAuth();

  const [species, setSpecies] = useState<Species[]>([]);
  const [draftRules, setDraftRules] = useState<DependencyRuleDraft[]>([]);

  const [speciesLoading, setSpeciesLoading] = useState(true);
  const [speciesError, setSpeciesError] = useState<string | null>(null);

  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<DependencyRuleFormData>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  const loadSpecies = useCallback(async () => {
    try {
      setSpeciesLoading(true);
      setSpeciesError(null);

      const token = getAccessToken();

      if (!token) {
        setSpeciesError(
          "You must be logged in as admin to configure dependency rules."
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

  function updateFormField<K extends keyof DependencyRuleFormData>(
    field: K,
    value: DependencyRuleFormData[K]
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

  function openEditModal(rule: DependencyRuleDraft) {
    setEditingId(rule.id);
    setFormData({
      focal_species_id: rule.focal_species_id,
      required_partner_id: rule.required_partner_id,
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
    if (formData.focal_species_id === 0) {
      return "Please select a focal species.";
    }

    if (formData.required_partner_id === 0) {
      return "Please select a required partner species.";
    }

    if (formData.focal_species_id === formData.required_partner_id) {
      return "A species cannot depend on itself.";
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
              }
            : rule
        )
      );
    }

    closeModal();
  }

  function handleDelete(id: number) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this dependency rule?"
    );

    if (!confirmed) return;

    setDraftRules(current => current.filter(rule => rule.id !== id));
  }

  return (
    <>
      <Helmet>
        <title>Dependency Rules | Planting Optimisation Tool</title>
      </Helmet>

      {/* <nav className="admin-back-nav">
        <Link to="/admin" className="admin-back-link">
          &larr; Back to Dashboard
        </Link>
      </nav> */}

      <section className="admin-page-card">
        <div className="admin-parameters-header">
          <div>
            <h2>Dependency Rules</h2>
            <p>
              Define biological relationships where one species requires another
              species to be planted with it.
            </p>
          </div>

          <button
            type="button"
            className="btn-primary"
            onClick={openCreateModal}
            disabled={speciesLoading || Boolean(speciesError)}
          >
            Add Dependency Rule
          </button>
        </div>

        {speciesLoading && <p>Loading species...</p>}

        {speciesError && <p className="admin-error-message">{speciesError}</p>}

        {!speciesLoading && !speciesError && draftRules.length === 0 && (
          <p>No dependency rules have been configured.</p>
        )}

        {draftRules.length > 0 && (
          <div className="admin-table-wrapper">
            <table className="admin-parameters-table">
              <thead>
                <tr>
                  <th>Focal Species</th>
                  <th>Required Partner</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {draftRules.map(rule => (
                  <tr key={rule.id}>
                    <td>{getSpeciesName(rule.focal_species_id)}</td>
                    <td>{getSpeciesName(rule.required_partner_id)}</td>
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
            aria-labelledby="dependency-rule-modal-title"
          >
            <div className="admin-modal-header">
              <div>
                <h3 id="dependency-rule-modal-title">
                  {modalMode === "create"
                    ? "Add Dependency Rule"
                    : "Edit Dependency Rule"}
                </h3>

                <p>
                  Select the species and the biological partner it requires.
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
                <h4>Species Dependency</h4>

                <div className="admin-form-grid">
                  <label>
                    Focal Species
                    <select
                      required
                      value={formData.focal_species_id}
                      onChange={event =>
                        updateFormField(
                          "focal_species_id",
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
                    Required Partner Species
                    <select
                      required
                      value={formData.required_partner_id}
                      onChange={event =>
                        updateFormField(
                          "required_partner_id",
                          Number(event.target.value)
                        )
                      }
                    >
                      <option value={0} disabled>
                        Select a partner species
                      </option>

                      {species.map(item => (
                        <option
                          key={item.id}
                          value={item.id}
                          disabled={item.id === formData.focal_species_id}
                        >
                          {item.name}
                        </option>
                      ))}
                    </select>
                  </label>
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

                <button type="submit" className="btn-primary">
                  {modalMode === "create"
                    ? "Add Dependency"
                    : "Update Dependency"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default DependencyRulesPage;
