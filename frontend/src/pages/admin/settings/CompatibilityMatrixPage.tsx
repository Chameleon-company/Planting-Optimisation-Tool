import { useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import AdminToast, {
  type AdminToastType,
} from "../../../components/admin/AdminToast";
import { useAuth } from "../../../contexts/AuthContext";
import {
  getAllSpecies,
  Species,
  updateSpecies,
} from "../../../utils/speciesApi";

type CompatibilityKey =
  | "coastal"
  | "riparian"
  | "nitrogen_fixing"
  | "shade_tolerant"
  | "bank_stabilising";

interface MatrixCondition {
  key: CompatibilityKey;
  label: string;
  description: string;
}

type CompatibilityMatrixState = Record<
  number,
  Record<CompatibilityKey, boolean>
>;

interface ToastState {
  message: string;
  type: AdminToastType;
}

const CONDITIONS: MatrixCondition[] = [
  {
    key: "coastal",
    label: "Coastal",
    description: "Suitable for coastal site conditions.",
  },
  {
    key: "riparian",
    label: "Riparian",
    description: "Suitable for riparian or water-edge conditions.",
  },
  {
    key: "nitrogen_fixing",
    label: "Nitrogen Fixing",
    description: "Provides nitrogen-fixing capability.",
  },
  {
    key: "shade_tolerant",
    label: "Shade Tolerant",
    description: "Suitable for shaded planting conditions.",
  },
  {
    key: "bank_stabilising",
    label: "Bank Stabilising",
    description: "Suitable where bank stabilisation is required.",
  },
];

function buildInitialMatrix(speciesList: Species[]): CompatibilityMatrixState {
  return speciesList.reduce<CompatibilityMatrixState>((matrix, item) => {
    matrix[item.id] = {
      coastal: item.coastal,
      riparian: item.riparian,
      nitrogen_fixing: item.nitrogen_fixing,
      shade_tolerant: item.shade_tolerant,
      bank_stabilising: item.bank_stabilising,
    };

    return matrix;
  }, {});
}

function CompatibilityMatrixPage() {
  const { getAccessToken } = useAuth();

  const [species, setSpecies] = useState<Species[]>([]);
  const [matrix, setMatrix] = useState<CompatibilityMatrixState>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingCells, setSavingCells] = useState<Set<string>>(new Set());

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

  useEffect(() => {
    async function loadSpecies() {
      try {
        setLoading(true);
        setError(null);

        const token = getAccessToken();

        if (!token) {
          setError(
            "You must be logged in as admin to view the compatibility matrix."
          );
          return;
        }

        const speciesData = await getAllSpecies(token);

        const sortedSpecies = [...speciesData].sort((a, b) =>
          a.name.localeCompare(b.name)
        );

        setSpecies(sortedSpecies);
        setMatrix(buildInitialMatrix(sortedSpecies));
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Failed to load compatibility matrix."
        );
      } finally {
        setLoading(false);
      }
    }

    void loadSpecies();
  }, [getAccessToken]);

  async function toggleCompatibility(
    speciesId: number,
    condition: CompatibilityKey
  ) {
    const token = getAccessToken();

    if (!token) {
      showToast(
        "You must be logged in as admin to update the compatibility matrix.",
        "error"
      );
      return;
    }

    const currentValue = matrix[speciesId]?.[condition] ?? false;
    const nextValue = !currentValue;
    const cellKey = `${speciesId}-${condition}`;

    setMatrix(current => ({
      ...current,
      [speciesId]: {
        ...current[speciesId],
        [condition]: nextValue,
      },
    }));

    setSavingCells(current => {
      const next = new Set(current);
      next.add(cellKey);
      return next;
    });

    try {
      await updateSpecies(
        speciesId,
        {
          [condition]: nextValue,
        },
        token
      );

      showToast("Compatibility change saved successfully.", "success");
    } catch (saveError) {
      setMatrix(current => ({
        ...current,
        [speciesId]: {
          ...current[speciesId],
          [condition]: currentValue,
        },
      }));

      showToast(
        saveError instanceof Error
          ? saveError.message
          : "Failed to save compatibility change.",
        "error"
      );

      console.error("Failed to update species compatibility:", saveError);
    } finally {
      setSavingCells(current => {
        const next = new Set(current);
        next.delete(cellKey);
        return next;
      });
    }
  }

  return (
    <>
      <Helmet>
        <title>Compatibility Matrix | Planting Optimisation Tool</title>
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
            <h2>Compatibility Matrix</h2>
            <p>
              View and manage how species interact with different site
              conditions.
            </p>
          </div>
        </div>

        {loading && (
          <div className="admin-loading-state" role="status" aria-live="polite">
            <span className="admin-spinner" aria-hidden="true" />
            <span>Loading compatibility matrix...</span>
          </div>
        )}

        {error && <p className="admin-error-message">{error}</p>}

        {!loading && !error && species.length === 0 && (
          <p>
            No species are available to display in the compatibility matrix.
          </p>
        )}

        {!loading && !error && species.length > 0 && (
          <div className="admin-table-wrapper">
            <table className="admin-parameters-table compatibility-matrix-table">
              <thead>
                <tr>
                  <th>Species</th>

                  {CONDITIONS.map(condition => (
                    <th key={condition.key} title={condition.description}>
                      {condition.label}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {species.map(item => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.name}</strong>

                      {item.common_name && (
                        <div className="compatibility-species-common-name">
                          {item.common_name}
                        </div>
                      )}
                    </td>

                    {CONDITIONS.map(condition => (
                      <td
                        key={condition.key}
                        className="compatibility-matrix-cell"
                      >
                        <input
                          type="checkbox"
                          checked={matrix[item.id]?.[condition.key] ?? false}
                          disabled={savingCells.has(
                            `${item.id}-${condition.key}`
                          )}
                          onChange={() =>
                            void toggleCompatibility(item.id, condition.key)
                          }
                          aria-label={`${item.name} ${condition.label}`}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}

export default CompatibilityMatrixPage;
