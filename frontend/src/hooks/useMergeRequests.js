import useAutoRefresh from "./useAutoRefresh";

export default function useMergeRequests() {
    const { data: merges, loading, error } = useAutoRefresh("/merge-requests");

    return { merges, loading, error };
}