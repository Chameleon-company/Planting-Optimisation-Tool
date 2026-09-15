import { FormEvent, useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";

import AdminToast, {
  type AdminToastType,
} from "../../../components/admin/AdminToast";
import { useAuth } from "../../../contexts/AuthContext";
import {
  createDependency,
  deleteDependency,
  getAllDependencies,
  SpeciesDependency,
  updateDependency,
} from "../../../utils/exclusionRulesApi";
import { getSpeciesDropdown, SpeciesDropdown } from "../../../utils/speciesApi";

type ModalMode = "create" | "edit" | null;

interface DependencyRuleFormData {
  focal_species_id: number;
  required_partner_id: number;
}

interface ToastState {
  message: string;
  type: AdminToastType;
}

const emptyForm: DependencyRuleFormData = {
  focal_species_id: 0,
  required_partner_id: 0,
};

function delay(ms: number): Promise<void> {
  return new Promise(resolve => {
    window.setTimeout(resolve, ms);
  });
}

function DependencyRulesPage() {
  const { getAccessToken } = useAuth();

  const [species, setSpecies] = useState<SpeciesDropdown[]>([]);
  const [dependencies, setDependencies] = useState<SpeciesDependency[]>([]);

  const [pageLoading, setPageLoading] = useState(true);
  const [pageError, setPageError] = useState<string | null>(null);

  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<DependencyRuleFormData>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [toast, setToast] = useState<ToastState | null>(null);

  const dismissToast = useCallback(() => {
    setToast(null);
  }, []);

  const showToast = useCallback((message: string, type: AdminToastType) => {
    setToast({
      message,
      type,
    });
  }, []);

  const loadPageData = useCallback(async () => {
    try {
      setPageLoading(true);
      setPageError(null);

      const token = getAccessToken();

      if (!token) {
        setPageError(
          "You must be logged in as admin to configure dependency rules."
        );
        return;
      }

      const [speciesData, dependencyData] = await Promise.all([
        getSpeciesDropdown(token),
        getAllDependencies(token),
      ]);

      setSpecies([...speciesData].sort((a, b) => a.name.localeCompare(b.name)));

      setDependencies(dependencyData);
    } catch (error) {
      setPageError(
        error instanceof Error
          ? error.message
          : "Failed to load dependency rules."
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

  function openEditModal(rule: SpeciesDependency) {
    setEditingId(rule.id);

    setFormData({
      focal_species_id: rule.focal_species_id,
      required_partner_id: rule.required_partner_id,
    });

    setFormError(null);
    setModalMode("edit");
  }

  function closeModal() {
    if (saving) {
      return;
    }

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

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (saving) {
      return;
    }

    const validationError = validateForm();

    if (validationError) {
      setFormError(validationError);
      return;
    }

    const token = getAccessToken();

    if (!token) {
      showToast(
        "You must be logged in as admin to save dependency rules.",
        "error"
      );
      return;
    }

    const payload = {
      focal_species_id: formData.focal_species_id,
      required_partner_id: formData.required_partner_id,
    };

    try {
      setSaving(true);
      setFormError(null);

      if (modalMode === "create") {
        const [createdDependency] = await Promise.all([
          createDependency(payload, token),
          delay(400),
        ]);

        setDependencies(current => [...current, createdDependency]);

        showToast("Dependency rule created successfully.", "success");
      }

      if (modalMode === "edit" && editingId !== null) {
        const [updatedDependency] = await Promise.all([
          updateDependency(editingId, payload, token),
          delay(400),
        ]);

        setDependencies(current =>
          current.map(rule =>
            rule.id === editingId ? updatedDependency : rule
          )
        );

        showToast("Dependency rule updated successfully.", "success");
      }

      setModalMode(null);
      setEditingId(null);
      setFormData(emptyForm);
      setFormError(null);
    } catch (error) {
      showToast(
        error instanceof Error
          ? error.message
          : "Failed to save dependency rule.",
        "error"
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (deletingId !== null) {
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete this dependency rule?"
    );

    if (!confirmed) {
      return;
    }

    const token = getAccessToken();

    if (!token) {
      showToast(
        "You must be logged in as admin to delete dependency rules.",
        "error"
      );
      return;
    }

    try {
      setDeletingId(id);

      await Promise.all([deleteDependency(id, token), delay(400)]);

      setDependencies(current => current.filter(rule => rule.id !== id));

      showToast("Dependency rule deleted successfully.", "success");
    } catch (error) {
      showToast(
        error instanceof Error
          ? error.message
          : "Failed to delete dependency rule.",
        "error"
      );
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <>
      <Helmet>
        <title>Dependency Rules | Planting Optimisation Tool</title>
      </Helmet>

      {toast && (
        <div className="admin-toast-container">
          <AdminToast
            message={toast.message}
            type={toast.type}
            onClose={dismissToast}
          />
        </div>
      )}

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
            disabled={pageLoading || Boolean(pageError) || deletingId !== null}
          >
            Add Dependency Rule
          </button>
        </div>

        {pageLoading && (
          <div className="admin-loading-state" role="status" aria-live="polite">
            <span className="admin-spinner" aria-hidden="true" />
            <span>Loading dependency rules...</span>
          </div>
        )}

        {pageError && <p className="admin-error-message">{pageError}</p>}

        {!pageLoading && !pageError && dependencies.length === 0 && (
          <p>No dependency rules have been configured.</p>
        )}

        {!pageLoading && dependencies.length > 0 && (
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
                {dependencies.map(rule => (
                  <tr key={rule.id}>
                    <td>{getSpeciesName(rule.focal_species_id)}</td>

                    <td>{getSpeciesName(rule.required_partner_id)}</td>

                    <td>
                      <button
                        type="button"
                        className="admin-action-btn"
                        onClick={() => openEditModal(rule)}
                        disabled={deletingId !== null}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="admin-action-btn admin-action-danger"
                        onClick={() => void handleDelete(rule.id)}
                        disabled={deletingId !== null}
                      >
                        {deletingId === rule.id ? "Deleting..." : "Delete"}
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
                disabled={saving}
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
                <h4>Species Dependency</h4>

                <div className="admin-form-grid">
                  <label>
                    Focal Species
                    <select
                      required
                      disabled={saving}
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
                      disabled={saving}
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
                  disabled={saving}
                >
                  Cancel
                </button>

                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving
                    ? "Saving..."
                    : modalMode === "create"
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
