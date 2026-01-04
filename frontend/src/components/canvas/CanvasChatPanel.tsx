/**
 * Canvas-specific chat panel
 * Allows AI to manipulate the canvas through natural language
 */

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Send, Loader2, Bot, User, Trash2, Sparkles, AlertCircle } from 'lucide-react';
import { useCanvasChatStore } from '../../store/useCanvasChatStore';
import { useCanvasStore } from '../../store/useCanvasStore';
import { useChatStore } from '../../store/useChatStore';

export const CanvasChatPanel = () => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isStreaming,
    error,
    sendMessage,
    clearMessages,
    setProvider,
    setModel,
  } = useCanvasChatStore();

  // Get canvas context
  const { nodes, edges } = useCanvasStore();

  // Sync provider/model from main chat store
  const { provider, model } = useChatStore();

  useEffect(() => {
    setProvider(provider);
    setModel(model);
  }, [provider, model, setProvider, setModel]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isStreaming) {
      await sendMessage(inputValue.trim(), { nodes, edges });
      setInputValue('');
    }
  };

  const handleClear = () => {
    if (confirm('Clear all canvas chat messages?')) {
      clearMessages();
    }
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">Canvas AI</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {nodes.length} nodes, {edges.length} edges
            </p>
          </div>
        </div>
        <button
          onClick={handleClear}
          className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          title="Clear messages"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="inline-block p-4 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl mb-4">
              <Sparkles className="w-12 h-12 text-purple-600 dark:text-purple-400" />
            </div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
              Canvas AI Assistant
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 max-w-xs mx-auto">
              Ask me to add nodes, create connections, highlight entities, or reorganize the canvas.
            </p>
            <div className="mt-4 space-y-2 text-xs text-gray-500 dark:text-gray-500">
              <p className="font-medium">Try asking:</p>
              <p>"Show me all connections to Maxwell"</p>
              <p>"Add Epstein as a person"</p>
              <p>"Connect Maxwell and Clinton"</p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}

            <div
              className={`flex-1 max-w-[85%] ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-lg p-3'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg p-3'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>

              {/* Show actions if any */}
              {message.actions && message.actions.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs font-semibold mb-1 opacity-75">Actions performed:</p>
                  <div className="space-y-1">
                    {message.actions.map((action, idx) => (
                      <div
                        key={idx}
                        className="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 px-2 py-1 rounded"
                      >
                        {action.type.replace(/_/g, ' ')}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <p className="text-xs opacity-50 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}

        {isStreaming && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-purple-600 dark:text-purple-400" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about the canvas..."
            disabled={isStreaming}
            className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isStreaming}
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-purple-400 disabled:to-pink-400 text-white rounded-lg transition-colors disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isStreaming ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          Using {provider} {model && `(${model})`}
        </p>
      </form>
    </div>
  );
};
