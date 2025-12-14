/**
 * Document store using Zustand
 */

import { create } from 'zustand';
import type { Document } from '../types';
import { documentsApi } from '../api/client';

interface DocumentStore {
  documents: Document[];
  loading: boolean;
  error: string | null;

  // Actions
  fetchDocuments: () => Promise<void>;
  uploadDocument: (file: File) => Promise<void>;
  deleteDocument: (id: number) => Promise<void>;
  refreshDocument: (id: number) => Promise<void>;
}

export const useDocumentStore = create<DocumentStore>((set) => ({
  documents: [],
  loading: false,
  error: null,

  fetchDocuments: async () => {
    set({ loading: true, error: null });
    try {
      const data = await documentsApi.list();
      set({ documents: data.documents, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch documents',
        loading: false
      });
    }
  },

  uploadDocument: async (file: File) => {
    set({ loading: true, error: null });
    try {
      const response = await documentsApi.upload(file);
      set(state => ({
        documents: [response.document, ...state.documents],
        loading: false
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to upload document',
        loading: false
      });
      throw error;
    }
  },

  deleteDocument: async (id: number) => {
    try {
      await documentsApi.delete(id);
      set(state => ({
        documents: state.documents.filter(doc => doc.id !== id)
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete document'
      });
      throw error;
    }
  },

  refreshDocument: async (id: number) => {
    try {
      const document = await documentsApi.get(id);
      set(state => ({
        documents: state.documents.map(doc =>
          doc.id === id ? document : doc
        )
      }));
    } catch (error) {
      console.error('Failed to refresh document:', error);
    }
  },
}));
