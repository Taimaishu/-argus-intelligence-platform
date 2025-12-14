/**
 * Chat interface component
 */

import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Send, Loader2, Bot, User, Plus, Trash2 } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { ModelSelector } from './ModelSelector';

export const ChatInterface = () => {
  const [inputValue, setInputValue] = useState('');
  const {
    sessions,
    currentSession,
    streaming,
    error,
    provider,
    model,
    fetchSessions,
    createSession,
    selectSession,
    deleteSession,
    sendMessage,
    setProvider,
    setModel
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !streaming) {
      await sendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleNewChat = async () => {
    await createSession('New Chat');
  };

  const handleDeleteSession = async (sessionId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this chat session?')) {
      await deleteSession(sessionId);
    }
  };

  return (
    <div className="flex h-[calc(100vh-12rem)] gap-6">
      {/* Sidebar - Session list */}
      <div className="w-72 bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-5 overflow-y-auto shadow-lg backdrop-blur-sm">
        <button
          onClick={handleNewChat}
          className="w-full mb-6 px-5 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 dark:hover:from-blue-600 dark:hover:to-indigo-600 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 font-medium"
        >
          <Plus className="w-5 h-5" />
          New Chat
        </button>

        <div className="space-y-3">
          {sessions.map(session => (
            <div
              key={session.id}
              onClick={() => selectSession(session.id)}
              className={`
                p-4 rounded-xl cursor-pointer flex items-center justify-between group transition-all duration-300
                ${currentSession?.id === session.id
                  ? 'bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 border-2 border-blue-300 dark:border-blue-700 shadow-md scale-105'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800 border-2 border-transparent hover:scale-102'
                }
              `}
            >
              <span className="text-sm font-medium text-gray-900 dark:text-white truncate flex-1">
                {session.title}
              </span>
              <button
                onClick={(e) => handleDeleteSession(session.id, e)}
                className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all"
              >
                <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg backdrop-blur-sm">
        {/* Model Selector */}
        <ModelSelector
          provider={provider}
          model={model}
          onProviderChange={setProvider}
          onModelChange={setModel}
        />

        {!currentSession ? (
          <div className="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <Bot className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
              <p className="text-lg">Select or create a chat to start</p>
              <p className="text-sm mt-2">Brainstorm theories and explore connections</p>
            </div>
          </div>
        ) : (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-400">
                  {error}
                </div>
              )}

              {currentSession.messages.length === 0 && (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  <Bot className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
                  <p className="text-lg">Start a conversation</p>
                  <p className="text-sm">Ask about your documents, brainstorm theories, or explore connections</p>
                </div>
              )}

              {currentSession.messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-500`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/40 dark:to-indigo-900/40 flex items-center justify-center flex-shrink-0 shadow-lg">
                      <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  )}

                  <div
                    className={`
                      max-w-[70%] px-5 py-3 rounded-2xl shadow-lg
                      ${message.role === 'user'
                        ? 'bg-gradient-to-br from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 text-white'
                        : 'bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-800 dark:to-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
                      }
                    `}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  </div>

                  {message.role === 'user' && (
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                      <User className="w-6 h-6 text-gray-700 dark:text-gray-300" />
                    </div>
                  )}
                </div>
              ))}

              {streaming && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="bg-gray-100 dark:bg-gray-800 px-4 py-3 rounded-lg">
                    <Loader2 className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input form */}
            <div className="border-t-2 border-gray-200 dark:border-gray-700 p-6 bg-gradient-to-r from-gray-50/80 to-blue-50/30 dark:from-gray-800/80 dark:to-blue-900/10 backdrop-blur-sm">
              <form onSubmit={handleSubmit} className="flex gap-3">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask about your documents, theories, or connections..."
                  className="flex-1 px-5 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-4 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 focus:border-blue-500 dark:focus:border-blue-400 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm text-gray-900 dark:text-white shadow-lg transition-all duration-300"
                  disabled={streaming}
                />
                <button
                  type="submit"
                  disabled={streaming || !inputValue.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 dark:hover:from-blue-600 dark:hover:to-indigo-600 disabled:from-gray-300 disabled:to-gray-400 dark:disabled:from-gray-700 dark:disabled:to-gray-800 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                >
                  {streaming ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
