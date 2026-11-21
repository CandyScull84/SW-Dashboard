import useAutoRefresh from "./useAutoRefresh";

export default function useActiveProjects(limit = 8) {
     const { data: projects, loading:loadingProjects, error} = useAutoRefresh("/active-projects");
    return { projects, loadingProjects, error};
}