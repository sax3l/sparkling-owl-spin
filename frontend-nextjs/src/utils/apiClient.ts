import axios from 'axios';
import { supabase } from './supabaseClient';

// Create axios instance for REST API calls
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(async (config) => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
  } catch (error) {
    console.warn('Failed to get session for API request:', error);
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - maybe refresh token or redirect to login
      console.warn('API returned 401 - token might be expired');
      // Could trigger a redirect to login page here
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login';
      }
    }
    return Promise.reject(error);
  }
);

// API endpoints configuration
export const API_ENDPOINTS = {
  // Jobs
  jobs: '/api/jobs',
  jobStart: '/api/jobs/start',
  jobStop: (id: string) => `/api/jobs/${id}/stop`,
  jobStatus: (id: string) => `/api/jobs/${id}/status`,
  
  // Templates
  templates: '/api/templates',
  templateById: (id: string) => `/api/templates/${id}`,
  templateValidate: '/api/templates/validate',
  
  // Data entities
  persons: '/api/persons',
  companies: '/api/companies',
  vehicles: '/api/vehicles',
  
  // Exports
  exports: '/api/exports',
  exportStart: '/api/exports/start',
  exportStatus: (id: string) => `/api/exports/${id}/status`,
  
  // Proxies
  proxies: '/api/proxies',
  proxyHealth: '/api/proxies/health',
  
  // System
  health: '/api/health',
  metrics: '/api/metrics',
};

export default apiClient;
