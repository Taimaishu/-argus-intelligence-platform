/**
 * Chat store using Zustand
 */

import { create } from 'zustand';

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  model?: string;
}

export interface ChatSession {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

interface ChatStore {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  loading: boolean;
  streaming: boolean;
  error: string | null;
  provider: string;
  model: string | null;

  // Actions
  fetchSessions: () => Promise<void>;
  createSession: (title?: string) => Promise<void>;
  selectSession: (sessionId: number) => Promise<void>;
  deleteSession: (sessionId: number) => Promise<void>;
  sendMessage: (message: string, includeContext?: boolean) => Promise<void>;
  setProvider: (provider: string) => void;
  setModel: (model: string | null) => void;
}

const API_URL = 'http://localhost:8000/api';

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: [],
  currentSession: null,
  loading: false,
  streaming: false,
  error: null,
  provider: 'ollama',
  model: null,

  fetchSessions: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_URL}/chat/sessions`);
      if (!response.ok) throw new Error('Failed to fetch sessions');
      const data = await response.json();
      set({ sessions: data.sessions, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch sessions',
        loading: false
      });
    }
  },

  createSession: async (title = 'New Chat') => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_URL}/chat/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });
      if (!response.ok) throw new Error('Failed to create session');
      const session = await response.json();
      set(state => ({
        sessions: [session, ...state.sessions],
        currentSession: session,
        loading: false
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create session',
        loading: false
      });
    }
  },

  selectSession: async (sessionId: number) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_URL}/chat/sessions/${sessionId}`);
      if (!response.ok) throw new Error('Failed to fetch session');
      const session = await response.json();
      set({ currentSession: session, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch session',
        loading: false
      });
    }
  },

  deleteSession: async (sessionId: number) => {
    try {
      const response = await fetch(`${API_URL}/chat/sessions/${sessionId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete session');
      set(state => ({
        sessions: state.sessions.filter(s => s.id !== sessionId),
        currentSession: state.currentSession?.id === sessionId ? null : state.currentSession
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete session'
      });
    }
  },

  sendMessage: async (message: string, includeContext = true) => {
    const { currentSession, provider, model } = get();
    if (!currentSession) {
      set({ error: 'No active session' });
      return;
    }

    // Add user message optimistically
    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      created_at: new Date().toISOString()
    };

    set(state => ({
      currentSession: state.currentSession
        ? {
            ...state.currentSession,
            messages: [...state.currentSession.messages, userMessage]
          }
        : null,
      streaming: true,
      error: null
    }));

    try {
      const response = await fetch(
        `${API_URL}/chat/sessions/${currentSession.id}/messages`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message,
            include_context: includeContext,
            provider,
            model
          })
        }
      );

      if (!response.ok) throw new Error('Failed to send message');

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                set({ streaming: false });
                return;
              }
              if (data.startsWith('[ERROR]')) {
                set({ error: data, streaming: false });
                return;
              }
              assistantMessage += data;

              // Update the assistant message in real-time
              set(state => {
                if (!state.currentSession) return state;

                const messages = [...state.currentSession.messages];
                const lastMessage = messages[messages.length - 1];

                if (lastMessage && lastMessage.role === 'assistant') {
                  lastMessage.content = assistantMessage;
                } else {
                  messages.push({
                    id: Date.now(),
                    role: 'assistant',
                    content: assistantMessage,
                    created_at: new Date().toISOString()
                  });
                }

                return {
                  currentSession: {
                    ...state.currentSession,
                    messages
                  }
                };
              });
            }
          }
        }
      }

      set({ streaming: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to send message',
        streaming: false
      });
    }
  },

  setProvider: (provider: string) => {
    set({ provider });
  },

  setModel: (model: string | null) => {
    set({ model });
  }
}));
