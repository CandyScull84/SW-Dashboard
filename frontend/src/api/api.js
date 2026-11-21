// src/api/api.js

import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    timeout: 10000,
})

api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("API error:", error?.response || error.message);
        return Promise.reject(error);
    }
);

export const getPushEvents = async (limit=10) => {
    const response = await api.get(`/push-events?limit=${limit}`);
    return response.data;
};

export const getMergeRequests = async (page = 1, perPage = 20) => {
    const response = await api.get(`/merge-requests?page=${page}&per_page=${perPage}`);
    return response.data;
};

export const getFailingPipelines = async (limit=10) => {
    const response = await api.get(`/failing-pipelines?limit_projects=${limit}`);
    return response.data;
};

export default api;