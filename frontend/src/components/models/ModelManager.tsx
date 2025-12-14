/**
 * Model Management Component
 * Manage Ollama models - list, pull, delete
 */

import { useState, useEffect } from 'react';
import { Download, Trash2, Loader2, RefreshCw, HardDrive } from 'lucide-react';

interface OllamaModel {
  name: string;
  size: string;
  modified: string;
}

export const ModelManager = () => {
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isPulling, setIsPulling] = useState(false);
  const [pullModel, setPullModel] = useState('');
  const [error, setError] = useState<string | null>(null);

  const recommendedModels = [
    { name: 'llama3.1:8b', desc: 'Best balance - general chat' },
    { name: 'qwen2.5:14b', desc: 'High quality responses' },
    { name: 'deepseek-r1:7b', desc: 'Fast and capable' },
    { name: 'mistral:7b', desc: 'Efficient and smart' },
    { name: 'nomic-embed-text', desc: 'For embeddings' },
  ];

  const fetchModels = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/models/ollama/list');
      if (!response.ok) throw new Error('Failed to fetch models');

      const data = await response.json();
      setModels(data.models || []);
    } catch (err) {
      console.error('Error fetching models:', err);
      setError('Failed to load models. Is Ollama running?');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handlePullModel = async () => {
    if (!pullModel.trim()) return;

    setIsPulling(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/models/ollama/pull', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_name: pullModel.trim() }),
      });

      if (!response.ok) throw new Error('Failed to pull model');

      const data = await response.json();
      if (data.success) {
        setPullModel('');
        await fetchModels();
      }
    } catch (err) {
      console.error('Error pulling model:', err);
      setError('Failed to pull model');
    } finally {
      setIsPulling(false);
    }
  };

  const handleDeleteModel = async (modelName: string) => {
    if (!confirm(`Delete ${modelName}?`)) return;

    try {
      const response = await fetch(`http://localhost:8000/api/models/ollama/${encodeURIComponent(modelName)}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await fetchModels();
      }
    } catch (err) {
      console.error('Error deleting model:', err);
      setError('Failed to delete model');
    }
  };

  const formatSize = (bytes: string) => {
    const num = parseInt(bytes);
    if (isNaN(num)) return bytes;
    const gb = num / (1024 * 1024 * 1024);
    return `${gb.toFixed(1)} GB`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">Ollama Models</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Manage local AI models
          </p>
        </div>
        <button
          onClick={fetchModels}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
          <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Pull Model */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Pull New Model</h4>
        <div className="flex gap-2">
          <input
            type="text"
            value={pullModel}
            onChange={(e) => setPullModel(e.target.value)}
            placeholder="e.g., llama3.1:8b"
            className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
            disabled={isPulling}
          />
          <button
            onClick={handlePullModel}
            disabled={isPulling || !pullModel.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors"
          >
            {isPulling ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Pulling...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Pull
              </>
            )}
          </button>
        </div>

        {/* Recommended Models */}
        <div className="mt-3 flex flex-wrap gap-2">
          {recommendedModels.map((model) => (
            <button
              key={model.name}
              onClick={() => setPullModel(model.name)}
              className="px-2 py-1 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 border border-blue-200 dark:border-blue-700 rounded text-xs transition-colors"
              title={model.desc}
            >
              {model.name}
            </button>
          ))}
        </div>
      </div>

      {/* Models List */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-400" />
          </div>
        ) : models.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <HardDrive className="w-12 h-12 text-gray-400 mb-3" />
            <p className="text-gray-600 dark:text-gray-400">No models installed</p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">Pull a model to get started</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {models.map((model) => (
              <div key={model.name} className="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <div className="flex-1">
                  <div className="font-medium text-gray-900 dark:text-white">{model.name}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {formatSize(model.size)}
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteModel(model.name)}
                  className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  title="Delete model"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
