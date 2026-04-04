import { useState, useEffect } from "react";
import { useAuth } from '../contexts/AuthContext';
import { useAsyncError } from '../hooks/useAsyncError';

export interface Recommendation {
    species_id: number;
    rank_overall: number;
    species_common_name: string;
    species_name: string;
    score_mcda: number;
    key_reasons: string[];
}

export interface ExcludedSpecies {
    id: number;
    species_common_name: string;
    species_name: string;
    reasons: string[];
}

export function useRecommendations(farmId: string) {
    const { token } = useAuth();
    const throwAsyncError = useAsyncError();

    const [recs, setRecs] = useState<Recommendation[]>([]);
    const [excludes, setExcludes] = useState<ExcludedSpecies[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);

    useEffect(() => {
        if (!farmId) return;

        const fetchRecs = async () => {
            setIsLoading(true);
            setRecs([]);
            setExcludes([]);

            try {
                const response = await fetch(`http://127.0.0.1:8080/recommendations/${farmId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    const errorData = await response.text();
                    throw new Error(errorData);
                }

                const data = await response.json();
                setRecs(data.recommendations || []);
                setExcludes(data.excluded_species || []);
                setHasSearched(true);
            } catch (err: any) {
                throwAsyncError(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchRecs();
    }, [farmId, token, throwAsyncError]);

    return { recs, excludes, isLoading, hasSearched };
}