//to be implemented when endpoint is added

// import { useEffect, useState } from "react";

// const API_BASE = import.meta.env.VITE_API_URL;

// interface AgroforestryType {
//   id: number;
//   name: string;
// }

// export function useAgroforestryTypes() {
//   const [agroforestryTypes, setAgroforestryTypes] = useState<AgroforestryType[]>([]);
//   const [isLoading, setIsLoading] = useState(true);

//   useEffect(() => {
//     fetch(`${API_BASE}/agroforestry-types`)
//       .then(res => res.json())
//       .then(data => setAgroforestryTypes(data))
//       .finally(() => setIsLoading(false));
//   }, []);

//   return { agroforestryTypes, isLoading };
// }