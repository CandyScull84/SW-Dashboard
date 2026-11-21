// src/hooks/useDashboardData.js
// import { useEffect, useState } from "react";
// import axios from "axios";

// export default function useDashboardData(intervalMs = 60000) {
//   const [data, setData] = useState({
//     members: [],
//     pipelines: [],
//     merges: [],
//     projects: [],
//     pushes: [],
//   });

//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   async function fetchAll() {
//     console.log(" FETCHING NOW ");
//     try {
//       setLoading(true);

//       const base = import.meta.env.VITE_API_URL;

//       // 🔥 ALL API-CALLS IN PARALLELL
//       const [
//         membersRes,
//         pipelinesRes,
//         mergesRes,
//         projectsRes,
//         pushesRes,
//       ] = await Promise.all([
//         axios.get(`${base}/team-status`),
//         axios.get(`${base}/failing-pipelines`),
//         axios.get(`${base}/merge-requests`),
//         axios.get(`${base}/active-projects`),
//         axios.get(`${base}/push-events`),
//       ]);

//       setData({
//         members: membersRes.data.items || membersRes.data || [],
//         pipelines: pipelinesRes.data.items || pipelinesRes.data || [],
//         merges: mergesRes.data.items || mergesRes.data || [],
//         projects: projectsRes.data.items || projectsRes.data || [],
//         pushes: pushesRes.data.items || pushesRes.data || [],
//       });

//       setError(null);
//     } catch (err) {
//       console.error("Dashboard fetch error:", err);
//       setError(err);
//     } finally {
//       setLoading(false);
//     }
//   }

//   // First fetch + refresh every 60s
//   useEffect(() => {
//     console.log("useDashboardData Mounted");
//     fetchAll();
//     const interval = setInterval(fetchAll, intervalMs);
//     return () => clearInterval(interval);
//   }, []);

//   return { ...data, loading, error };
// }

// import { useEffect, useState } from "react";
// import axios from "axios";

// /**
//  * Hämtar alla API-endpoints parallellt utan att blockera UI.
//  * Varje endpoint uppdaterar state direkt när den är klar.
//  */
// export default function useDashboardData(intervalMs = 60000) {
//   const [members, setMembers] = useState([]);
//   const [pipelines, setPipelines] = useState([]);
//   const [merges, setMerges] = useState([]);
//   const [projects, setProjects] = useState([]);
//   const [pushes, setPushes] = useState([]);

//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   const base = import.meta.env.VITE_API_URL;

//   function normalize(data) {
//     if (!data) return [];
//     if (Array.isArray(data)) return data;
//     if (data.items) return data.items;
//     if (data.active_list) return data.active_list;
//     return [];
//   }

//   async function fetchSingle(endpoint, setter) {
//     try {
//       const res = await axios.get(`${base}${endpoint}`);
//       setter(res.data.items || res.data || []);
//     } catch (err) {
//       console.error("Error fetching:", endpoint, err);
//       setError(err);
//     }
//   }

//   async function fetchAll() {
//     setLoading(true);

//     // 🔥 Kör alla parallellt UTAN await → UI blockeras inte
//     fetchSingle("/team-status", setMembers);
//     fetchSingle("/failing-pipelines", setPipelines);
//     fetchSingle("/merge-requests", setMerges);
//     fetchSingle("/active-projects", setProjects);
//     fetchSingle("/push-events", setPushes);

//     // liten kort timeout för att visa “loading” i början
//     setTimeout(() => setLoading(false), 300);
//   }

//   useEffect(() => {
//     fetchAll();
//     const id = setInterval(fetchAll, intervalMs);
//     return () => clearInterval(id);
//   }, []);

//   return {
//     members,
//     pipelines,
//     merges,
//     projects,
//     pushes,
//     loading,
//     error,
//   };
// }

import { useEffect, useState } from "react";
import axios from "axios";

/**
 * Hämtar alla API-endpoints parallellt utan att blockera UI.
 * Visar INGEN spinner vid första laddningen,
 * men spinner visas vid varje 60s uppdatering.
 */
export default function useDashboardData(intervalMs = 60000) {
    const [members, setMembers] = useState([]);
    const [pipelines, setPipelines] = useState([]);
    const [merges, setMerges] = useState([]);
    const [projects, setProjects] = useState([]);
    const [pushes, setPushes] = useState([]);

    const [loading, setLoading] = useState(false); // spinner startar inte
    const [error, setError] = useState(null);
    const [firstLoadDone, setFirstLoadDone] = useState(false);

    const base = import.meta.env.VITE_API_URL;

    async function fetchAll() {
        // ✅ Visa spinner endast efter första laddningen
        if (firstLoadDone) {
            setLoading(true);
        }

        const endpoints = [
            ["/team-status", setMembers],
            ["/failing-pipelines", setPipelines],
            ["/merge-requests", setMerges],
            ["/active-projects", setProjects],
            ["/push-events", setPushes],
        ];

        try {
            await Promise.allSettled(
            endpoints.map(async ([url, setter]) => {
                const res = await axios.get(`${base}${url}`);
                setter(
                    Array.isArray(res.data)
                        ? res.data
                        : res.data?.items || res.data?.active_list || []
                );
            })
            );

            setError(null);
        } catch (err) {
            setError(err);
        } finally {
            // ✅ Markera att första laddningen är klar
            if (!firstLoadDone) setFirstLoadDone(true);

            // ✅ Spinner visas i exakt 30 sek vid uppdatering
            if (firstLoadDone) {
            setTimeout(() => {
                setLoading(false);
            }, 30000); // ⏱ 30 SEK
            } else {
            setLoading(false);
            }
        }
    }



    useEffect(() => {
        fetchAll(); // första körningen → ingen spinner
        const id = setInterval(fetchAll, intervalMs); // kör varje 60s med spinner
        return () => clearInterval(id);
    }, []);

    return {
        members,
        pipelines,
        merges,
        projects,
        pushes,
        loading,
        error,
    };
}

