// Uncomment this when agroforestry types endpoint is added

// import { useEffect, useState } from "react";

// const API_BASE = import.meta.env.VITE_API_URL;

// interface AgroforestryType {
//   id: number;
//   type_name: string;
// }

// export function useAgroforestryType() {
//   const [agroforestryTypes, setAgroforestryType] = useState<AgroforestryType[]>([]);
//   const [isLoading, setIsLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);

//   useEffect(() => {
//     let cancelled = false;

//     setIsLoading(true);
//     setError(null);

//     fetch(`${API_BASE}/agroforestry-type`)
//       .then(res => {
//         // Check res.ok before attempting to parse, so error bodies
//         // don't get silently set as valid
//         if (!res.ok) {
//           throw new Error(`Failed to load agroforestry types (${res.status})`);
//         }
//         return res.json();
//       })
//       .then((data: AgroforestryType[]) => {
//         if (!cancelled) setAgroforestryType(data);
//       })
//       .catch((err: unknown) => {
//         if (!cancelled) {
//           setError(err instanceof Error ? err.message : "Unexpected error");
//         }
//       })
//       .finally(() => {
//         if (!cancelled) setIsLoading(false);
//       });

//     return () => {
//       cancelled = true;
//     };
//   }, []);

//   return { agroforestryTypes, isLoading, error };
// }
