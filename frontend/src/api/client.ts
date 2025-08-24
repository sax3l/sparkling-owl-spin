import { JobType, ExportCreate, ExportRead, JobStatus } from './types';

// API client configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const submitJob = async (url: string, type: JobType) => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ start_url: url, job_type: type }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to submit job:", error);
    throw error;
  }
};

export const submitExport = async (exportData: ExportCreate): Promise<ExportRead> => {
  try {
    const response = await fetch(`${API_BASE_URL}/exports`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(exportData),
    });

    if (!response.ok) {
      const errorBody = await response.json();
      throw new Error(`HTTP error! status: ${response.status}, detail: ${errorBody.detail || response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to submit export job:", error);
    throw error;
  }
};

export const getExportStatus = async (exportId: string): Promise<ExportRead> => {
  try {
    const response = await fetch(`${API_BASE_URL}/exports/${exportId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to get status for export ${exportId}:`, error);
    throw error;
  }
};

export const listExports = async (status?: JobStatus, exportType?: string): Promise<ExportRead[]> => {
  try {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (exportType) params.append('export_type', exportType);

    const response = await fetch(`${API_BASE_URL}/exports?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to list exports:", error);
    throw error;
  }
};

export const getDirectData = async (exportType: string, format: 'csv' | 'ndjson' | 'json', filters?: Record<string, any>, compress: boolean = false, limit?: number, offset?: number): Promise<Response> => {
  try {
    const params = new URLSearchParams();
    params.append('format', format);
    params.append('compress', String(compress));
    if (filters) params.append('filters', JSON.stringify(filters));
    if (limit !== undefined) params.append('limit', String(limit));
    if (offset !== undefined) params.append('offset', String(offset));

    const headers: HeadersInit = {};
    if (format === 'csv') headers['Accept'] = 'text/csv';
    else if (format === 'ndjson') headers['Accept'] = 'application/x-ndjson';
    else if (format === 'json') headers['Accept'] = 'application/json';

    const response = await fetch(`${API_BASE_URL}/data/${exportType}?${params.toString()}`, { headers });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response;
  } catch (error) {
    console.error(`Failed to fetch direct data for ${exportType}:`, error);
    throw error;
  }
};

export const submitDiagnosticJob = async (templateId: string, targetUrl?: string, sampleHtml?: string, tags?: string[]) => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/diagnostic`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ template_id: templateId, target_url: targetUrl, sample_html: sampleHtml, tags: tags || [] }),
    });

    if (!response.ok) {
      const errorBody = await response.json();
      throw new Error(`HTTP error! status: ${response.status}, detail: ${errorBody.detail || response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to submit diagnostic job:", error);
    throw error;
  }
};

// ============================================================================
// MISSING API INTEGRATIONS FOR COMPLETE FRONTEND-BACKEND SYNC
// ============================================================================

// Dashboard & Monitoring APIs
export const getDashboardData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/monitoring/dashboard`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to get dashboard data:", error);
    throw error;
  }
};

export const getRealTimeStats = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/stats/real-time`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to get real-time stats:", error);
    throw error;
  }
};

export const getSystemHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/system/health`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to get system health:", error);
    throw error;
  }
};

// Job Management APIs
export const getJobDetails = async (jobId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to get job details for ${jobId}:`, error);
    throw error;
  }
};

export const deleteJob = async (jobId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to delete job ${jobId}:`, error);
    throw error;
  }
};

export const pauseJob = async (jobId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/pause`, {
      method: 'POST'
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to pause job ${jobId}:`, error);
    throw error;
  }
};

export const resumeJob = async (jobId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/resume`, {
      method: 'POST'
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to resume job ${jobId}:`, error);
    throw error;
  }
};

// Template Management APIs
export const getTemplates = async (category?: string) => {
  try {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    
    const response = await fetch(`${API_BASE_URL}/templates?${params.toString()}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to get templates:", error);
    throw error;
  }
};

export const getTemplateDetails = async (templateId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/templates/${templateId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to get template details for ${templateId}:`, error);
    throw error;
  }
};

export const createTemplate = async (templateData: any) => {
  try {
    const response = await fetch(`${API_BASE_URL}/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(templateData)
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to create template:", error);
    throw error;
  }
};

export const updateTemplate = async (templateId: string, templateData: any) => {
  try {
    const response = await fetch(`${API_BASE_URL}/templates/${templateId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(templateData)
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to update template ${templateId}:`, error);
    throw error;
  }
};

export const deleteTemplate = async (templateId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/templates/${templateId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to delete template ${templateId}:`, error);
    throw error;
  }
};

// Proxy Management APIs
export const getProxyMonitoringData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/monitoring/proxies`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to get proxy monitoring data:", error);
    throw error;
  }
};

export const listProxies = async (poolId?: string, status?: string) => {
  try {
    const params = new URLSearchParams();
    if (poolId) params.append('pool_id', poolId);
    if (status) params.append('status', status);
    
    const response = await fetch(`${API_BASE_URL}/proxies?${params.toString()}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to list proxies:", error);
    throw error;
  }
};

export const testProxy = async (proxyId: string, targetUrl?: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/proxies/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proxy_id: proxyId, target_url: targetUrl })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to test proxy ${proxyId}:`, error);
    throw error;
  }
};

export const removeProxy = async (proxyId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/proxies/${proxyId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Failed to remove proxy ${proxyId}:`, error);
    throw error;
  }
};

// WebSocket connections for real-time updates
export const createDashboardWebSocket = (onMessage: (data: any) => void) => {
  const ws = new WebSocket(`ws://localhost:8000/ws/dashboard`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  
  ws.onerror = (error) => {
    console.error('Dashboard WebSocket error:', error);
  };
  
  return ws;
};

export const createJobProgressWebSocket = (jobId: string, onMessage: (data: any) => void) => {
  const ws = new WebSocket(`ws://localhost:8000/ws/jobs/${jobId}`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  
  ws.onerror = (error) => {
    console.error(`Job ${jobId} WebSocket error:`, error);
  };
  
  return ws;
};

// Additional utility functions for enhanced integration
export const getDetailedHealthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health/detailed`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to get detailed health check:", error);
    throw error;
  }
};