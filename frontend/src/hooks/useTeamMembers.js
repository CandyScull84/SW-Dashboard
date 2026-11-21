import useAutoRefresh from "./useAutoRefresh";

export default function useTeamMembers() {
    const { data: members, loading, error} = useAutoRefresh("/team-status");

    return {members, loading, error};
}