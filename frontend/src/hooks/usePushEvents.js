import useAutoRefresh from "./useAutoRefresh";

export default function usePushEvents() {
    const { data: pushes, loading, error} = useAutoRefresh("/push-events");

    return { pushes, loading, error};
}