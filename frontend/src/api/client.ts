/**
 * API client for communicating with the backend
 */

import axios from 'axios';
import type { Document, SearchResponse, UploadResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Documents API
export const documentsApi = {
  upload: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<UploadResponse>(
      '/api/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  list: async (): Promise<{ documents: Document[]; total: number }> => {
    const response = await apiClient.get<{ documents: Document[]; total: number }>(
      '/api/documents'
    );
    return response.data;
  },

  get: async (id: number): Promise<Document> => {
    const response = await apiClient.get<Document>(`/api/documents/${id}`);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/documents/${id}`);
  },
};

// Search API
export const searchApi = {
  search: async (query: string, topK: number = 20): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>('/api/search', {
      query,
      top_k: topK,
    });
    return response.data;
  },

  getSimilar: async (documentId: number, chunkIndex: number, topK: number = 5) => {
    const response = await apiClient.get(
      `/api/search/similar/${documentId}/${chunkIndex}?top_k=${topK}`
    );
    return response.data;
  },

  getDocumentSummary: async (documentId: number) => {
    const response = await apiClient.get(`/api/search/document/${documentId}/summary`);
    return response.data;
  },
};

// Health API
export const healthApi = {
  check: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;
