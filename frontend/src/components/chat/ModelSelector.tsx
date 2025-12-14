/**
 * Model and Provider Selector for Chat
 */

import { useState, useEffect } from 'react';
import { Bot, Sparkles, Settings } from 'lucide-react';
import { getApiUrl } from '../../config/api';

interface ModelSelectorProps {
  provider: string;
  model: string | null;
  onProviderChange: (provider: string) => void;
  onModelChange: (model: string | null) => void;
}

interface ProviderStatus {
  available: boolean;
  configured: boolean;
}

export const ModelSelector = ({
  provider,
  model,
  onProviderChange,
  onModelChange
}: ModelSelectorProps) => {
  const [ollamaModels, setOllamaModels] = useState<string[]>([]);
  const [providerStatus, setProviderStatus] = useState<Record<string, ProviderStatus>>({});
  const [showSettings, setShowSettings] = useState(false);

  const providerModels: Record<string, string[]> = {
    ollama: ollamaModels,
    openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'],
    anthropic: ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229']
  };

  useEffect(() => {
    fetchProviderStatus();
    if (provider === 'ollama') {
      fetchOllamaModels();
    }
  }, [provider]);

  const fetchProviderStatus = async () => {
    try {
      const response = await fetch(getApiUrl('/api/models/providers/status'));
      const data = await response.json();
      setProviderStatus(data);
    } catch (err) {
      console.error('Error fetching provider status:', err);
    }
  };

  const fetchOllamaModels = async () => {
    try {
      const response = await fetch(getApiUrl('/api/models/ollama/list'));
      const data = await response.json();
      setOllamaModels(data.models?.map((m: any) => m.name) || []);
    } catch (err) {
      console.error('Error fetching Ollama models:', err);
    }
  };

  const getProviderIcon = (prov: string) => {
    if (prov === 'ollama') return <Bot className="w-4 h-4" />;
    return <Sparkles className="w-4 h-4" />;
  };

  const getProviderLabel = (prov: string) => {
    const labels: Record<string, string> = {
      ollama: 'Ollama (Local)',
      openai: 'OpenAI',
      anthropic: 'Anthropic'
    };
    return labels[prov] || prov;
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      {/* Provider Selector */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Provider:</span>
        <div className="flex gap-1">
          {Object.keys(providerModels).map((prov) => {
            const status = providerStatus[prov];
            const isAvailable = status?.available;
            const isActive = provider === prov;

            return (
              <button
                key={prov}
                onClick={() => {
                  if (isAvailable) {
                    onProviderChange(prov);
                    onModelChange(null);
                  }
                }}
                disabled={!isAvailable}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md'
                    : isAvailable
                    ? 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                    : 'bg-gray-100 dark:bg-gray-900 text-gray-400 dark:text-gray-600 cursor-not-allowed opacity-50'
                }`}
                title={!isAvailable ? 'Not available' : ''}
              >
                {getProviderIcon(prov)}
                {getProviderLabel(prov)}
              </button>
            );
          })}
        </div>
      </div>

      {/* Model Selector */}
      {providerModels[provider] && providerModels[provider].length > 0 && (
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Model:</span>
          <select
            value={model || ''}
            onChange={(e) => onModelChange(e.target.value || null)}
            className="px-3 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Default</option>
            {providerModels[provider].map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Settings Button */}
      <button
        onClick={() => setShowSettings(!showSettings)}
        className="ml-auto p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
        title="Model settings"
      >
        <Settings className="w-4 h-4" />
      </button>

      {/* Settings Panel */}
      {showSettings && (
        <div className="absolute right-4 top-16 z-50 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl p-4">
          <h3 className="font-bold text-gray-900 dark:text-white mb-3">Provider Status</h3>
          <div className="space-y-2">
            {Object.entries(providerStatus).map(([prov, status]) => (
              <div key={prov} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {getProviderLabel(prov)}
                </span>
                <span className={`text-xs px-2 py-1 rounded ${
                  status.available
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                    : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                }`}>
                  {status.available ? 'Available' : 'Not Available'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
