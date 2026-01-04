/**
 * Settings Page - Configure API keys and platform settings
 */

import { useState, useEffect } from 'react';
import { Save, Eye, EyeOff, CheckCircle, AlertCircle, Key, Shield } from 'lucide-react';

interface ApiKeys {
  openai: string;
  anthropic: string;
  google: string;
  unsplash: string;
  pexels: string;
}

export const SettingsPage = () => {
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: '',
    anthropic: '',
    google: '',
    unsplash: '',
    pexels: '',
  });

  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({
    openai: false,
    anthropic: false,
    google: false,
    unsplash: false,
    pexels: false,
  });

  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load API keys from localStorage
    const loadedKeys: Partial<ApiKeys> = {};
    Object.keys(apiKeys).forEach((key) => {
      const storedKey = localStorage.getItem(`api_key_${key}`);
      if (storedKey) {
        loadedKeys[key as keyof ApiKeys] = storedKey;
      }
    });
    setApiKeys({ ...apiKeys, ...loadedKeys });
  }, []);

  const handleSave = () => {
    try {
      // Save to localStorage
      Object.entries(apiKeys).forEach(([key, value]) => {
        if (value) {
          localStorage.setItem(`api_key_${key}`, value);
        } else {
          localStorage.removeItem(`api_key_${key}`);
        }
      });

      setSaved(true);
      setError(null);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError('Failed to save API keys');
      console.error('Save error:', err);
    }
  };

  const toggleShowKey = (key: string) => {
    setShowKeys({ ...showKeys, [key]: !showKeys[key] });
  };

  const handleKeyChange = (key: keyof ApiKeys, value: string) => {
    setApiKeys({ ...apiKeys, [key]: value });
    setSaved(false);
  };

  const maskKey = (key: string) => {
    if (!key) return '';
    if (key.length <= 8) return '•'.repeat(key.length);
    return key.slice(0, 4) + '•'.repeat(key.length - 8) + key.slice(-4);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Key className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">API Key Configuration</h1>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 ml-12">
            Configure your API keys for AI providers and external services. Keys are stored locally in your browser.
          </p>
        </div>

        {/* Security Notice */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-start gap-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <Shield className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-yellow-900 dark:text-yellow-200 text-sm mb-1">Security Notice</h3>
              <p className="text-xs text-yellow-800 dark:text-yellow-300">
                API keys are stored in your browser's local storage. Never share your API keys with anyone.
                For live USB deployments, keys will be cleared when the session ends.
              </p>
            </div>
          </div>
        </div>

        {/* API Keys Form */}
        <div className="p-6 space-y-6">
          {/* OpenAI */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-1">
                  OpenAI API Key
                </label>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Required for GPT-4, GPT-3.5, and embedding models
                </p>
              </div>
              <button
                onClick={() => toggleShowKey('openai')}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                {showKeys.openai ? (
                  <EyeOff className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                ) : (
                  <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                )}
              </button>
            </div>
            <input
              type={showKeys.openai ? 'text' : 'password'}
              value={apiKeys.openai}
              onChange={(e) => handleKeyChange('openai', e.target.value)}
              placeholder="sk-..."
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Anthropic */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-1">
                  Anthropic API Key
                </label>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Required for Claude models (Sonnet, Opus, Haiku)
                </p>
              </div>
              <button
                onClick={() => toggleShowKey('anthropic')}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                {showKeys.anthropic ? (
                  <EyeOff className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                ) : (
                  <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                )}
              </button>
            </div>
            <input
              type={showKeys.anthropic ? 'text' : 'password'}
              value={apiKeys.anthropic}
              onChange={(e) => handleKeyChange('anthropic', e.target.value)}
              placeholder="sk-ant-..."
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Google */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-1">
                  Google API Key
                </label>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Optional - for Google Custom Search and Maps
                </p>
              </div>
              <button
                onClick={() => toggleShowKey('google')}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                {showKeys.google ? (
                  <EyeOff className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                ) : (
                  <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                )}
              </button>
            </div>
            <input
              type={showKeys.google ? 'text' : 'password'}
              value={apiKeys.google}
              onChange={(e) => handleKeyChange('google', e.target.value)}
              placeholder="AIza..."
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Unsplash */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-1">
                  Unsplash Access Key
                </label>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Optional - for high-quality image search
                </p>
              </div>
              <button
                onClick={() => toggleShowKey('unsplash')}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                {showKeys.unsplash ? (
                  <EyeOff className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                ) : (
                  <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                )}
              </button>
            </div>
            <input
              type={showKeys.unsplash ? 'text' : 'password'}
              value={apiKeys.unsplash}
              onChange={(e) => handleKeyChange('unsplash', e.target.value)}
              placeholder="..."
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Pexels */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-1">
                  Pexels API Key
                </label>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Optional - for additional image search
                </p>
              </div>
              <button
                onClick={() => toggleShowKey('pexels')}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                {showKeys.pexels ? (
                  <EyeOff className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                ) : (
                  <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                )}
              </button>
            </div>
            <input
              type={showKeys.pexels ? 'text' : 'password'}
              value={apiKeys.pexels}
              onChange={(e) => handleKeyChange('pexels', e.target.value)}
              placeholder="..."
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {saved && (
                <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">Settings saved successfully</span>
                </div>
              )}
              {error && (
                <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                  <AlertCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">{error}</span>
                </div>
              )}
            </div>
            <button
              onClick={handleSave}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Settings
            </button>
          </div>

          {/* Instructions */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Getting API Keys:</h3>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <li>• <strong>OpenAI:</strong> <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">platform.openai.com/api-keys</a></li>
              <li>• <strong>Anthropic:</strong> <a href="https://console.anthropic.com/account/keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">console.anthropic.com/account/keys</a></li>
              <li>• <strong>Google:</strong> <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">console.cloud.google.com/apis/credentials</a></li>
              <li>• <strong>Unsplash:</strong> <a href="https://unsplash.com/developers" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">unsplash.com/developers</a></li>
              <li>• <strong>Pexels:</strong> <a href="https://www.pexels.com/api/" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">pexels.com/api</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
