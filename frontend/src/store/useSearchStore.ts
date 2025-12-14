/**
 * Search store using Zustand
 */

import { create } from 'zustand';
import type { SearchResponse } from '../types';
import { searchApi } from '../api/client';

interface SearchStore {
  query: string;
  results: SearchResponse | null;
  loading: boolean;
  error: string | null;

  // Actions
  setQuery: (query: string) => void;
  search: (query: string, topK?: number) => Promise<void>;
  clearResults: () => void;
}

export const useSearchStore = create<SearchStore>((set) => ({
  query: '',
  results: null,
  loading: false,
  error: null,

  setQuery: (query: string) => set({ query }),

  search: async (query: string, topK: number = 20) => {
    if (!query.trim()) {
      set({ error: 'Please enter a search query' });
      return;
    }

    set({ loading: true, error: null, query });
    try {
      const results = await searchApi.search(query, topK);
      set({ results, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Search failed',
        loading: false,
        results: null
      });
    }
  },

  clearResults: () => set({ results: null, query: '', error: null }),
}));
