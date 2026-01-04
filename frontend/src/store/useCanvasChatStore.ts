/**
 * Canvas-specific chat state management
 * Handles chat interactions within the canvas context
 */

import { create } from 'zustand';
import { getApiUrl } from '../config/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: CanvasAction[];
}

interface CanvasAction {
  type: 'add_node' | 'remove_node' | 'highlight_nodes' | 'create_edge' | 'regenerate_layout';
  data?: any;
  node_id?: string;
  node_ids?: string[];
  source?: string;
  target?: string;
  label?: string;
}

interface CanvasChatState {
  // UI state
  isPanelOpen: boolean;
  isStreaming: boolean;
  error: string | null;

  // Chat state
  messages: Message[];
  currentInput: string;

  // Settings (inherited from main chat)
  provider: string;
  model: string | null;

  // Actions
  togglePanel: () => void;
  setCurrentInput: (input: string) => void;
  setProvider: (provider: string) => void;
  setModel: (model: string | null) => void;

  sendMessage: (
    message: string,
    canvasContext: { nodes: any[]; edges: any[] }
  ) => Promise<void>;

  clearMessages: () => void;
  executeAction: (action: CanvasAction) => void;
}

const API_BASE = getApiUrl('/api');

export const useCanvasChatStore = create<CanvasChatState>((set, get) => ({
  // Initial state
  isPanelOpen: false,
  isStreaming: false,
  error: null,
  messages: [],
  currentInput: '',
  provider: 'anthropic',
  model: null,

  togglePanel: () => {
    set((state) => ({ isPanelOpen: !state.isPanelOpen }));
  },

  setCurrentInput: (input: string) => {
    set({ currentInput: input });
  },

  setProvider: (provider: string) => {
    set({ provider });
  },

  setModel: (model: string | null) => {
    set({ model });
  },

  sendMessage: async (message: string, canvasContext: { nodes: any[]; edges: any[] }) => {
    const { provider, model, messages } = get();

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    set({
      messages: [...messages, userMessage],
      currentInput: '',
      isStreaming: true,
      error: null,
    });

    try {
      // Call canvas chat endpoint with streaming
      const response = await fetch(`${API_BASE}/chat/canvas-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          canvas_context: canvasContext,
          provider,
          model,
          session_id: 'canvas-session', // Use dedicated canvas session
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      // Handle SSE streaming
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      let assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        actions: [],
      };

      // Add assistant message placeholder
      set((state) => ({
        messages: [...state.messages, assistantMessage],
      }));

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);

            if (data === '[DONE]') {
              set({ isStreaming: false });
              break;
            }

            try {
              const parsed = JSON.parse(data);

              // Check if it's an action command
              if (parsed.action) {
                // Action command from AI
                const action: CanvasAction = {
                  type: parsed.action,
                  data: parsed.data,
                  node_id: parsed.node_id,
                  node_ids: parsed.node_ids,
                  source: parsed.source,
                  target: parsed.target,
                  label: parsed.label,
                };

                assistantMessage.actions = [...(assistantMessage.actions || []), action];

                // Update message
                set((state) => ({
                  messages: state.messages.map((msg) =>
                    msg.id === assistantMessage.id ? assistantMessage : msg
                  ),
                }));

                // Execute action immediately
                get().executeAction(action);
              } else {
                // Regular text chunk
                assistantMessage.content += parsed.content || parsed.text || data;

                // Update message
                set((state) => ({
                  messages: state.messages.map((msg) =>
                    msg.id === assistantMessage.id ? assistantMessage : msg
                  ),
                }));
              }
            } catch (e) {
              // Not JSON, append as text
              assistantMessage.content += data;

              set((state) => ({
                messages: state.messages.map((msg) =>
                  msg.id === assistantMessage.id ? assistantMessage : msg
                ),
              }));
            }
          }
        }
      }

      set({ isStreaming: false });
    } catch (err) {
      console.error('Canvas chat error:', err);
      set({
        error: 'Failed to send message',
        isStreaming: false,
      });

      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };

      set((state) => ({
        messages: [...state.messages, errorMessage],
      }));
    }
  },

  clearMessages: () => {
    set({ messages: [], error: null });
  },

  executeAction: (action: CanvasAction) => {
    console.log('Executing canvas action:', action);

    // Actions will be handled by the CanvasPage component
    // through a callback or event system
    // For now, just log them

    // Emit custom event for CanvasPage to handle
    window.dispatchEvent(
      new CustomEvent('canvas-action', {
        detail: action,
      })
    );
  },
}));
