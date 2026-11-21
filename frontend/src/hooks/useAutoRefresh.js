/* useAutoRefresh */

import { useEffect, useState } from "react";
import axios from "axios";

/**
 * useAutoRefresh — Fetch data automatically from API-endpoints and updates every 60 second.
 * @param {string} endpoint - API-endpoint, ex. '/merge-requests'
 * @param {number} intervalMs - Polling interval (default 60000 ms)
 */
export default function useAutoRefresh(endpoint, intervalMs = 60000) {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let intervalId;

        async function fetchData() {
            try {
                setLoading(true);
                const res = await axios.get(`${import.meta.env.VITE_API_URL}${endpoint}`);
                setData(
                    Array.isArray(res.data)
                        ? res.data
                        : res.data?.items || res.data?.active_list || []
                );
                setError(null);
            } catch (err) {
                console.error(`Error fetching ${endpoint}:`, err);
                setError(err);
            } finally {
                setLoading(false);
            }
        }

        // Go 
        fetchData();

        // Go every 60 second
        intervalId = setInterval(fetchData, intervalMs);

        // Clean when hook is removed
        return () => clearInterval(intervalId);
    }, [endpoint, intervalMs]);

    return { data, loading, error };
}
