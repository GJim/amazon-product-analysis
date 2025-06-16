/**
 * API service for interacting with the Amazon Product Analysis backend
 */

// API response types
export interface TaskResponse {
  task_id: string;
  status: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string;
  result: any | null;
}

export interface ProductAnalysisRequest {
  url: string;
  max_products: number;
  max_competitive: number;
}

/**
 * Base API URL - dynamically determined based on environment
 */
const getApiBaseUrl = () => {
  // During SSR, there's no window object
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  
  // For client-side requests, use relative URL to avoid CORS issues
  return '';
};

/**
 * Submit a product URL for analysis
 */
export const createAnalysisTask = async (data: ProductAnalysisRequest): Promise<TaskResponse> => {
  console.log(getApiBaseUrl())
  const response = await fetch(`${getApiBaseUrl()}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || `API error: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
};

/**
 * Get the status of an analysis task
 */
export const getTaskStatus = async (taskId: string): Promise<TaskStatusResponse> => {
  const response = await fetch(`${getApiBaseUrl()}/api/task/${taskId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail || `API error: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
};
