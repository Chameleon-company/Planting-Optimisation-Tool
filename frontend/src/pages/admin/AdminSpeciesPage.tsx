import { FormEvent, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";

import { useAuth } from "../../contexts/AuthContext";
import {
  AgroforestryType,
  createSpecies,
  deleteSpecies,
  getAllSpecies,
  getSoilTextures,
  SoilTexture,
  Species,
  SpeciesPayload,
  updateSpecies,
} from "../../utils/speciesApi";

type ModalMode = "create" | "edit" | null;

const emptyForm: SpeciesPayload = {
  name: "",
  common_name: "",
  rainfall_mm_min: 0,
  rainfall_mm_max: 0,
  temperature_celsius_min: 0,
  temperature_celsius_max: 0,
  elevation_m_min: 0,
  elevation_m_max: 0,
  ph_min: 0,
  ph_max: 0,
  coastal: false,
  riparian: false,
  nitrogen_fixing: false,
  shade_tolerant: false,
  bank_stabilising: false,
  soil_textures: [],
  agroforestry_types: [],
};

const AGROFORESTRY_TYPES = [
  { id: 1, type_name: "block" },
  { id: 2, type_name: "boundary" },
  { id: 3, type_name: "intercropping" },
  { id: 4, type_name: "mosaic" },
];

function buildSpeciesPayload(species: Species): SpeciesPayload {
  return {
    name: species.name,
    common_name: species.common_name,
    rainfall_mm_min: species.rainfall_mm_min,
    rainfall_mm_max: species.rainfall_mm_max,
    temperature_celsius_min: species.temperature_celsius_min,
    temperature_celsius_max: species.temperature_celsius_max,
    elevation_m_min: species.elevation_m_min,
    elevation_m_max: species.elevation_m_max,
    ph_min: species.ph_min,
    ph_max: species.ph_max,
    coastal: species.coastal,
    riparian: species.riparian,
    nitrogen_fixing: species.nitrogen_fixing,
    shade_tolerant: species.shade_tolerant,
    bank_stabilising: species.bank_stabilising,
    soil_textures: species.soil_textures.map(soil => soil.id),
    agroforestry_types: species.agroforestry_types.map(type => type.id),
  };
}

function AdminSpeciesPage() {
  const { getAccessToken } = useAuth();

  const [species, setSpecies] = useState<Species[]>([]);
  const [soilTextures, setSoilTextures] = useState<SoilTexture[]>([]);
  const [agroforestryTypes] = useState<AgroforestryType[]>(AGROFORESTRY_TYPES);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [editingSpeciesId, setEditingSpeciesId] = useState<number | null>(null);
  const [formData, setFormData] = useState<SpeciesPayload>(emptyForm);

  async function loadSpecies() {
    try {
      setLoading(true);
      setError(null);

      const token = getAccessToken();

      if (!token) {
        setError("You must be logged in as admin to view species.");
        return;
      }

      const [speciesData, soilData] = await Promise.all([
        getAllSpecies(token),
        getSoilTextures(),
      ]);

      setSpecies(speciesData);
      setSoilTextures(soilData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load species");
    } finally {
      setLoading(false);
    }
  }

  function openCreateModal() {
    setError(null);
    setSuccessMessage(null);
    setEditingSpeciesId(null);
    setFormData(emptyForm);
    setModalMode("create");
  }

  function openEditModal(item: Species) {
    setError(null);
    setSuccessMessage(null);
    setEditingSpeciesId(item.id);
    setFormData(buildSpeciesPayload(item));
    setModalMode("edit");
  }

  function closeModal() {
    setModalMode(null);
    setEditingSpeciesId(null);
    setFormData(emptyForm);
  }

  function updateFormField<K extends keyof SpeciesPayload>(
    field: K,
    value: SpeciesPayload[K]
  ) {
    setFormData(current => ({
      ...current,
      [field]: value,
    }));
  }

  function toggleNumberSelection(
    field: "soil_textures" | "agroforestry_types",
    id: number
  ) {
    setFormData(current => {
      const selected = current[field];
      const nextSelected = selected.includes(id)
        ? selected.filter(value => value !== id)
        : [...selected, id];

      return {
        ...current,
        [field]: nextSelected,
      };
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const token = getAccessToken();

    if (!token) {
      setError("You must be logged in as admin to manage species.");
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);

      if (modalMode === "create") {
        await createSpecies(formData, token);
        setSuccessMessage("Species created successfully.");
      }

      if (modalMode === "edit" && editingSpeciesId !== null) {
        await updateSpecies(editingSpeciesId, formData, token);
        setSuccessMessage("Species updated successfully.");
      }

      closeModal();
      await loadSpecies();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save species");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    const token = getAccessToken();

    if (!token) {
      setError("You must be logged in as admin to delete species.");
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete this species?"
    );

    if (!confirmed) return;

    try {
      setError(null);
      setSuccessMessage(null);
      await deleteSpecies(id, token);
      setSuccessMessage("Species deleted successfully.");
      await loadSpecies();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete species");
    }
  }

  useEffect(() => {
    void loadSpecies();
  }, []);

  return (
    <>
      <Helmet>
        <title>Admin | Species Management</title>
      </Helmet>

      <section className="admin-page-card">
        <div className="admin-species-header">
          <div>
            <h2>Species Management</h2>
            <p>
              Manage species records used by the planting recommendation model.
            </p>
          </div>

          <button
            type="button"
            className="admin-primary-btn"
            onClick={openCreateModal}
          >
            Add Species
          </button>
        </div>

        {loading && <p>Loading species...</p>}

        {error && <p className="admin-error-message">{error}</p>}

        {successMessage && (
          <p className="admin-success-message">{successMessage}</p>
        )}

        {!loading && !error && species.length === 0 && <p>No species found.</p>}

        {!loading && species.length > 0 && (
          <div className="admin-table-wrapper">
            <table className="admin-species-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Scientific Name</th>
                  <th>Common Name</th>
                  <th>Rainfall</th>
                  <th>Temperature</th>
                  <th>pH</th>
                  <th>Attributes</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {species.map(item => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.name}</td>
                    <td>{item.common_name}</td>
                    <td>
                      {item.rainfall_mm_min}–{item.rainfall_mm_max} mm
                    </td>
                    <td>
                      {item.temperature_celsius_min}–
                      {item.temperature_celsius_max}°C
                    </td>
                    <td>
                      {item.ph_min}–{item.ph_max}
                    </td>
                    <td>
                      <span className="admin-tag">
                        {item.soil_textures.length}{" "}
                        {item.soil_textures.length === 1 ? "soil" : "soils"}
                      </span>
                      <span className="admin-tag">
                        {item.agroforestry_types.length}{" "}
                        {item.agroforestry_types.length === 1
                          ? "type"
                          : "types"}
                      </span>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="admin-action-btn"
                        onClick={() => openEditModal(item)}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="admin-action-btn admin-action-danger"
                        onClick={() => void handleDelete(item.id)}
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
          <div className="admin-species-modal" role="dialog" aria-modal="true">
            <div className="admin-modal-header">
              <div>
                <h3>
                  {modalMode === "create" ? "Add Species" : "Edit Species"}
                </h3>
                <p>
                  Enter species parameters used by the recommendation model.
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

            <form className="admin-species-form" onSubmit={handleSubmit}>
              <div className="admin-form-section">
                <h4>Basic Details</h4>

                <label>
                  Scientific Name
                  <input
                    required
                    type="text"
                    value={formData.name}
                    onChange={event =>
                      updateFormField("name", event.target.value)
                    }
                  />
                </label>

                <label>
                  Common Name
                  <input
                    required
                    type="text"
                    value={formData.common_name}
                    onChange={event =>
                      updateFormField("common_name", event.target.value)
                    }
                  />
                </label>
              </div>

              <div className="admin-form-section">
                <h4>Environmental Ranges</h4>

                <div className="admin-form-grid">
                  <label>
                    Rainfall Min
                    <input
                      type="number"
                      value={formData.rainfall_mm_min}
                      onChange={event =>
                        updateFormField(
                          "rainfall_mm_min",
                          Number(event.target.value)
                        )
                      }
                    />
                  </label>

                  <label>
                    Rainfall Max
                    <input
                      type="number"
                      value={formData.rainfall_mm_max}
                      onChange={event =>
                        updateFormField(
                          "rainfall_mm_max",
                          Number(event.target.value)
                        )
                      }
                    />
                  </label>

                  <label>
                    Temperature Min
                    <input
                      type="number"
                      value={formData.temperature_celsius_min}
                      onChange={event =>
                        updateFormField(
                          "temperature_celsius_min",
                          Number(event.target.value)
                        )
                      }
                    />
                  </label>

                  <label>
                    Temperature Max
                    <input
                      type="number"
                      value={formData.temperature_celsius_max}
                      onChange={event =>
                        updateFormField(
                          "temperature_celsius_max",
                          Number(event.target.value)
                        )
                      }
                    />
                  </label>

                  <label>
                    Elevation Min
                    <input
                      type="number"
                      value={formData.elevation_m_min}
                      onChange={event =>
                        updateFormField(
                          "elevation_m_min",
                          Number(event.target.value)
                        )
                      }
                    />
                  </label>

                  <label>
                    Elevation Max
                    <input
                      type="number"
                      value={formData.elevation_m_max}
                      onChange={event =>
                        updateFormField(
                          "elevation_m_max",
                          Number(event.target.value)
                        )
                      }
                    />
                  </label>

                  <label>
                    pH Min
                    <input
                      step="0.1"
                      type="number"
                      value={formData.ph_min}
                      onChange={event =>
                        updateFormField("ph_min", Number(event.target.value))
                      }
                    />
                  </label>

                  <label>
                    pH Max
                    <input
                      step="0.1"
                      type="number"
                      value={formData.ph_max}
                      onChange={event =>
                        updateFormField("ph_max", Number(event.target.value))
                      }
                    />
                  </label>
                </div>
              </div>

              <div className="admin-form-section">
                <h4>Functional Traits</h4>

                <div className="admin-checkbox-grid">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.coastal}
                      onChange={event =>
                        updateFormField("coastal", event.target.checked)
                      }
                    />
                    Coastal
                  </label>

                  <label>
                    <input
                      type="checkbox"
                      checked={formData.riparian}
                      onChange={event =>
                        updateFormField("riparian", event.target.checked)
                      }
                    />
                    Riparian
                  </label>

                  <label>
                    <input
                      type="checkbox"
                      checked={formData.nitrogen_fixing}
                      onChange={event =>
                        updateFormField("nitrogen_fixing", event.target.checked)
                      }
                    />
                    Nitrogen fixing
                  </label>

                  <label>
                    <input
                      type="checkbox"
                      checked={formData.shade_tolerant}
                      onChange={event =>
                        updateFormField("shade_tolerant", event.target.checked)
                      }
                    />
                    Shade tolerant
                  </label>

                  <label>
                    <input
                      type="checkbox"
                      checked={formData.bank_stabilising}
                      onChange={event =>
                        updateFormField(
                          "bank_stabilising",
                          event.target.checked
                        )
                      }
                    />
                    Bank stabilising
                  </label>
                </div>
              </div>

              <div className="admin-form-section">
                <h4>Soil Textures</h4>

                <div className="admin-checkbox-grid">
                  {soilTextures.map(texture => (
                    <label key={texture.id}>
                      <input
                        type="checkbox"
                        checked={formData.soil_textures.includes(texture.id)}
                        onChange={() =>
                          toggleNumberSelection("soil_textures", texture.id)
                        }
                      />
                      {texture.name}
                    </label>
                  ))}
                </div>
              </div>

              <div className="admin-form-section">
                <h4>Agroforestry Types</h4>

                <div className="admin-checkbox-grid">
                  {agroforestryTypes.map(type => (
                    <label key={type.id}>
                      <input
                        type="checkbox"
                        checked={formData.agroforestry_types.includes(type.id)}
                        onChange={() =>
                          toggleNumberSelection("agroforestry_types", type.id)
                        }
                      />
                      {type.type_name}
                    </label>
                  ))}
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

                <button
                  type="submit"
                  className="admin-primary-btn"
                  disabled={saving}
                >
                  {saving ? "Saving..." : "Save Species"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default AdminSpeciesPage;
