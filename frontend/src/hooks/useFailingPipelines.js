import useAutoRefresh from "./useAutoRefresh";

export default function useFailingPipelines() {
    const { data, loading, error} = useAutoRefresh("/failing-pipelines");
    const pipelines = data;

    return { pipelines, loading, error };
} 