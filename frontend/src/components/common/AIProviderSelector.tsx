/**
 * Compact AI Provider Selector for any page
 * Syncs with global chat store for consistent provider selection
 */

import { useState, useEffect } from 'react';
import { Bot, Sparkles, Zap } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { getApiUrl } from '../../config/api';

interface ProviderStatus {
  available: boolean;
  configured: boolean;
}

export const AIProviderSelector = () => {
  const { provider, model, setProvider, setModel } = useChatStore();
  const [providerStatus, setProviderStatus] = useState<Record<string, ProviderStatus>>({});
  const [showModelDropdown, setShowModelDropdown] = useState(false);

  useEffect(() => {
    fetchProviderStatus();
  }, []);

  const fetchProviderStatus = async () => {
    try {
      const response = await fetch(getApiUrl('/api/models/providers/status'));
      const data = await response.json();
      setProviderStatus(data);
    } catch (err) {
      console.error('Error fetching provider status:', err);
    }
  };

  const providerOptions = [
    { value: 'ollama', label: 'Ollama', icon: Bot, color: 'blue' },
    { value: 'openai', label: 'OpenAI', icon: Zap, color: 'green' },
    { value: 'anthropic', label: 'Anthropic', icon: Sparkles, color: 'purple' },
  ];

  const modelOptions: Record<string, { value: string; label: string }[]> = {
    ollama: [
      { value: '', label: 'Default' },
      { value: 'llama3:8b', label: 'Llama 3 8B' },
    ],
    openai: [
      { value: '', label: 'Default (GPT-4o Mini)' },
      { value: 'gpt-4o', label: 'GPT-4o' },
      { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
      { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    ],
    anthropic: [
      { value: '', label: 'Default (Claude 3.5 Sonnet)' },
      { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
      { value: 'claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku' },
      { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
    ],
  };

  const currentProvider = providerOptions.find(p => p.value === provider);
  const Icon = currentProvider?.icon || Bot;
  const color = currentProvider?.color || 'gray';

  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-700',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 border-purple-300 dark:border-purple-700',
    gray: 'bg-gray-50 dark:bg-gray-900/20 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-700',
  };

  return (
    <div className="flex items-center gap-2">
      {/* Provider Selector */}
      <div className="relative">
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border-2 ${colorClasses[color as keyof typeof colorClasses]} text-sm font-medium`}>
          <Icon className="w-4 h-4" />
          <select
            value={provider}
            onChange={(e) => {
              setProvider(e.target.value);
              setModel(null);
            }}
            className="bg-transparent border-none focus:outline-none cursor-pointer font-medium pr-1"
          >
            {providerOptions.map((opt) => {
              const status = providerStatus[opt.value];
              const isAvailable = status?.available;
              return (
                <option key={opt.value} value={opt.value} disabled={!isAvailable}>
                  {opt.label} {!isAvailable ? '(Unavailable)' : ''}
                </option>
              );
            })}
          </select>
        </div>
      </div>

      {/* Model Selector */}
      <div className="relative">
        <select
          value={model || ''}
          onChange={(e) => setModel(e.target.value || null)}
          className="px-3 py-1.5 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {modelOptions[provider]?.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};
