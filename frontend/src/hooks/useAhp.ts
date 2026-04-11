import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useAsyncError } from '@/hooks/useAsyncError';
import { AhpResponse, CalculationRequest } from '@/utils/ahp_types';

const API_BASE = import.meta.env.VITE_API_URL;


// --- TYPES ---
export interface SpeciesDropdownItem {
    id: number;
    name: string;
    common_name: string;
}

export interface FactorsResponse {
    factors: string[];
}

// --- SPECIES DROPDOWN HOOK ---
export function useAhpSpecies() {
    const { getAccessToken } = useAuth();
    const token = getAccessToken();
    const throwAsyncError = useAsyncError();

    const [speciesList, setSpeciesList] = useState<SpeciesDropdownItem[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        if (!token) return;

        const fetchSpecies = async () => {
            setIsLoading(true);
            try {
                const response = await fetch(`${API_BASE}/species/dropdown`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (!response.ok) {
                    throw new Error(`Failed to fetch species: ${response.statusText}`);
                }

                const data: SpeciesDropdownItem[] = await response.json();
                setSpeciesList(data);
            } catch (err: any) {
                throwAsyncError(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchSpecies();
    }, [token, throwAsyncError]);

    return { speciesList, isLoading };
}


// --- AHP CONFIG (FEATURES) HOOK ---
export function useAhpFactors() {
    const { getAccessToken } = useAuth();
    const token = getAccessToken();
    const throwAsyncError = useAsyncError();

    const [factorsList, setFactorsList] = useState<FactorsResponse | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchFactors = async () => {
            setIsLoading(true);
            try {
                const headers: HeadersInit = { 'Accept': 'application/json' };
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const response = await fetch(`${API_BASE}/species/features`, {
                    method: 'GET',
                    headers,
                });
                if (!response.ok) {
                    throw new Error(`Could not load features: ${response.statusText}`);
                }

                const rawData: string[] = await response.json();
                setFactorsList({ factors: rawData });
            } catch (err: any) {
                throwAsyncError(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchFactors();
    }, [token, throwAsyncError]);

    return { factorsList, isLoading };
}


// --- AHP CALCULATION HOOK ---
export function useAhpCalculation() {
    const { getAccessToken } = useAuth();
    const token = getAccessToken();
    const throwAsyncError = useAsyncError();

    const [results, setResults] = useState<AhpResponse | null>(null);
    const [isCalculating, setIsCalculating] = useState<boolean>(false);

    const handleCalculate = async (payload: CalculationRequest) => {
        setIsCalculating(true);
        console.log("Calculating AHP with payload:", payload);
        try {
            const headers: HeadersInit = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const response = await fetch(`${API_BASE}/ahp/calculate-and-save`, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                let errorMessage = "Invalid matrix payload.";
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (e) {
                    errorMessage = response.statusText;
                }
                throw new Error(`Calculation failed: ${errorMessage}`);
            }

            const data = await response.json();
            setResults(data);
        } catch (err: any) {
            throwAsyncError(err);
        } finally {
            setIsCalculating(false);
        }
    };

    const resetCalculation = () => setResults(null);

    return { results, isCalculating, handleCalculate, resetCalculation };
}