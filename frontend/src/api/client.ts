import { JobType } from './types';

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