/**
 * OSINT store using Zustand
 */

import { create } from 'zustand';

export interface Artifact {
  id: number;
  artifact_type: string;
  value: string;
  analysis_status: string;
  threat_level: string;
  analysis_data: any;
  first_seen: string;
  last_analyzed: string | null;
  document_id: number | null;
  extracted: boolean;
  notes: string | null;
}

export interface OSINTStats {
  total_artifacts: number;
  by_type: Record<string, number>;
  by_threat_level: Record<string, number>;
}

interface OSINTStore {
  artifacts: Artifact[];
  currentArtifact: Artifact | null;
  stats: OSINTStats | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchArtifacts: (filters?: { artifact_type?: string; threat_level?: string }) => Promise<void>;
  fetchArtifact: (id: number) => Promise<void>;
  submitArtifact: (artifactType: string, value: string) => Promise<void>;
  deleteArtifact: (id: number) => Promise<void>;
  extractFromText: (text: string) => Promise<any>;
  extractFromDocument: (documentId: number) => Promise<void>;
  fetchStats: () => Promise<void>;
}

const API_URL = 'http://localhost:8000/api';

export const useOSINTStore = create<OSINTStore>((set) => ({
  artifacts: [],
  currentArtifact: null,
  stats: null,
  loading: false,
  error: null,

  fetchArtifacts: async (filters) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams();
      if (filters?.artifact_type) params.append('artifact_type', filters.artifact_type);
      if (filters?.threat_level) params.append('threat_level', filters.threat_level);

      const response = await fetch(`${API_URL}/osint/artifacts?${params}`);
      if (!response.ok) throw new Error('Failed to fetch artifacts');

      const data = await response.json();
      set({ artifacts: data.artifacts, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch artifacts',
        loading: false
      });
    }
  },

  fetchArtifact: async (id: number) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_URL}/osint/artifacts/${id}`);
      if (!response.ok) throw new Error('Failed to fetch artifact');

      const artifact = await response.json();
      set({ currentArtifact: artifact, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch artifact',
        loading: false
      });
    }
  },

  submitArtifact: async (artifactType: string, value: string) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_URL}/osint/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ artifact_type: artifactType, value })
      });

      if (!response.ok) throw new Error('Failed to submit artifact');

      const artifact = await response.json();
      set(state => ({
        artifacts: [artifact, ...state.artifacts],
        currentArtifact: artifact,
        loading: false
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to submit artifact',
        loading: false
      });
      throw error;
    }
  },

  deleteArtifact: async (id: number) => {
    try {
      const response = await fetch(`${API_URL}/osint/artifacts/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to delete artifact');

      set(state => ({
        artifacts: state.artifacts.filter(a => a.id !== id)
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete artifact'
      });
      throw error;
    }
  },

  extractFromText: async (text: string) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_URL}/osint/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!response.ok) throw new Error('Failed to extract artifacts');

      const result = await response.json();
      set({ loading: false });
      return result;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to extract artifacts',
        loading: false
      });
      throw error;
    }
  },

  extractFromDocument: async (documentId: number) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_URL}/osint/documents/${documentId}/extract`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Failed to extract from document');

      set({ loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to extract from document',
        loading: false
      });
      throw error;
    }
  },

  fetchStats: async () => {
    try {
      const response = await fetch(`${API_URL}/osint/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');

      const stats = await response.json();
      set({ stats });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch stats'
      });
    }
  }
}));
