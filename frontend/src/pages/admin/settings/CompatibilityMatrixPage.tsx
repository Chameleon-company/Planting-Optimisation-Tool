import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { useAuth } from "../../../contexts/AuthContext";
import { getAllSpecies, Species } from "../../../utils/speciesApi";

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

  function toggleCompatibility(speciesId: number, condition: CompatibilityKey) {
    setMatrix(current => ({
      ...current,
      [speciesId]: {
        ...current[speciesId],
        [condition]: !current[speciesId]?.[condition],
      },
    }));
  }

  return (
    <>
      <Helmet>
        <title>Compatibility Matrix | Planting Optimisation Tool</title>
      </Helmet>

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

        {!loading && !error && (
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
                          onChange={() =>
                            toggleCompatibility(item.id, condition.key)
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
