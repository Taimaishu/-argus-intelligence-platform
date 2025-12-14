/**
 * Canvas state management with Zustand
 */

import { create } from 'zustand';
import type { Node, Edge, NodeChange, EdgeChange } from 'reactflow';

interface CanvasState {
  nodes: Node[];
  edges: Edge[];
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;

  // Actions
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  addNode: (node: Node) => void;
  addEdge: (edge: Edge) => void;
  updateNodeData: (nodeId: string, data: any) => void;
  deleteNode: (nodeId: string) => void;
  deleteEdge: (edgeId: string) => void;

  // API actions
  loadCanvas: () => Promise<void>;
  saveCanvas: () => Promise<void>;
  clearCanvas: () => Promise<void>;
}

const API_BASE = 'http://localhost:8000/api';

export const useCanvasStore = create<CanvasState>((set, get) => ({
  nodes: [],
  edges: [],
  isLoading: false,
  isSaving: false,
  error: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes) => {
    // Import applyNodeChanges dynamically to avoid circular deps
    import('reactflow').then(({ applyNodeChanges }) => {
      set({
        nodes: applyNodeChanges(changes, get().nodes),
      });

      // Auto-save after position changes
      const hasPositionChange = changes.some(c => c.type === 'position');
      if (hasPositionChange) {
        // Debounced save will be handled by the component
        setTimeout(() => get().saveCanvas(), 2000);
      }
    });
  },

  onEdgesChange: (changes) => {
    import('reactflow').then(({ applyEdgeChanges }) => {
      set({
        edges: applyEdgeChanges(changes, get().edges),
      });
    });
  },

  addNode: (node) => {
    set((state) => ({
      nodes: [...state.nodes, node],
    }));

    // Save to backend
    fetch(`${API_BASE}/canvas/nodes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(node),
    }).catch(err => {
      console.error('Failed to save node:', err);
      set({ error: 'Failed to save node' });
    });
  },

  addEdge: (edge) => {
    set((state) => ({
      edges: [...state.edges, edge],
    }));

    // Save to backend
    fetch(`${API_BASE}/canvas/edges`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(edge),
    }).catch(err => {
      console.error('Failed to save edge:', err);
      set({ error: 'Failed to save edge' });
    });
  },

  updateNodeData: (nodeId, data) => {
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
      ),
    }));

    // Update backend
    fetch(`${API_BASE}/canvas/nodes/${nodeId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data }),
    }).catch(err => {
      console.error('Failed to update node:', err);
    });
  },

  deleteNode: (nodeId) => {
    set((state) => ({
      nodes: state.nodes.filter((node) => node.id !== nodeId),
      edges: state.edges.filter(
        (edge) => edge.source !== nodeId && edge.target !== nodeId
      ),
    }));

    // Delete from backend
    fetch(`${API_BASE}/canvas/nodes/${nodeId}`, {
      method: 'DELETE',
    }).catch(err => {
      console.error('Failed to delete node:', err);
    });
  },

  deleteEdge: (edgeId) => {
    set((state) => ({
      edges: state.edges.filter((edge) => edge.id !== edgeId),
    }));

    // Delete from backend
    fetch(`${API_BASE}/canvas/edges/${edgeId}`, {
      method: 'DELETE',
    }).catch(err => {
      console.error('Failed to delete edge:', err);
    });
  },

  loadCanvas: async () => {
    set({ isLoading: true, error: null });

    try {
      const response = await fetch(`${API_BASE}/canvas/state`);
      if (!response.ok) throw new Error('Failed to load canvas');

      const data = await response.json();
      set({
        nodes: data.nodes || [],
        edges: data.edges || [],
        isLoading: false,
      });
    } catch (err) {
      console.error('Failed to load canvas:', err);
      set({
        error: 'Failed to load canvas',
        isLoading: false,
      });
    }
  },

  saveCanvas: async () => {
    const { nodes, edges, isSaving } = get();

    // Prevent concurrent saves
    if (isSaving) return;

    set({ isSaving: true, error: null });

    try {
      const response = await fetch(`${API_BASE}/canvas/state`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes, edges }),
      });

      if (!response.ok) throw new Error('Failed to save canvas');

      set({ isSaving: false });
    } catch (err) {
      console.error('Failed to save canvas:', err);
      set({
        error: 'Failed to save canvas',
        isSaving: false,
      });
    }
  },

  clearCanvas: async () => {
    try {
      const response = await fetch(`${API_BASE}/canvas/clear`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to clear canvas');

      set({
        nodes: [],
        edges: [],
        error: null,
      });
    } catch (err) {
      console.error('Failed to clear canvas:', err);
      set({ error: 'Failed to clear canvas' });
    }
  },
}));
