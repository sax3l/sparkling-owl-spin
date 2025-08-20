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