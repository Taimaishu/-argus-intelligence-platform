/**
 * First-Run Setup Wizard - Appears when no API keys are configured
 */

import { useState } from 'react';
import { X, Key, Zap, CheckCircle, ArrowRight, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SetupWizardProps {
  onClose: () => void;
}

export const SetupWizard = ({ onClose }: SetupWizardProps) => {
  const [step, setStep] = useState(1);
  const [openaiKey, setOpenaiKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');
  const navigate = useNavigate();

  const handleComplete = () => {
    // Save keys to localStorage
    if (openaiKey) {
      localStorage.setItem('api_key_openai', openaiKey);
    }
    if (anthropicKey) {
      localStorage.setItem('api_key_anthropic', anthropicKey);
    }

    // Mark setup as complete
    localStorage.setItem('setup_completed', 'true');

    onClose();
  };

  const handleSkip = () => {
    localStorage.setItem('setup_completed', 'true');
    onClose();
  };

  const goToSettings = () => {
    localStorage.setItem('setup_completed', 'true');
    onClose();
    navigate('/settings');
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 rounded-t-2xl">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Welcome to Argus</h2>
                <p className="text-sm text-white/80">Intelligence Platform Setup</p>
              </div>
            </div>
            <button
              onClick={handleSkip}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-white" />
            </button>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center gap-2">
            <div className={`flex-1 h-2 rounded-full transition-all ${step >= 1 ? 'bg-white' : 'bg-white/30'}`}></div>
            <div className={`flex-1 h-2 rounded-full transition-all ${step >= 2 ? 'bg-white' : 'bg-white/30'}`}></div>
            <div className={`flex-1 h-2 rounded-full transition-all ${step >= 3 ? 'bg-white' : 'bg-white/30'}`}></div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8">
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Get Started with AI-Powered Intelligence
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Argus uses advanced AI models to help you analyze documents, extract entities,
                  generate insights, and build knowledge graphs. To get started, you'll need API keys
                  from AI providers.
                </p>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Key className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-blue-900 dark:text-blue-200 text-sm mb-1">
                      Why API Keys?
                    </h4>
                    <p className="text-xs text-blue-800 dark:text-blue-300">
                      API keys authenticate your requests to AI services. They're stored locally in your
                      browser and never sent to our servers. For live USB deployments, keys are cleared
                      when you close the browser.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
                  Supported AI Providers:
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="font-medium text-gray-900 dark:text-white text-sm">OpenAI</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">GPT-4, GPT-3.5</div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="font-medium text-gray-900 dark:text-white text-sm">Anthropic</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Claude Sonnet, Opus</div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="font-medium text-gray-900 dark:text-white text-sm">Ollama</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Local models (free)</div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="font-medium text-gray-900 dark:text-white text-sm">Wikipedia</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Image search (free)</div>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  Get Started
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={handleSkip}
                  className="px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors"
                >
                  Skip Setup
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Configure AI Provider Keys
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Add at least one API key to enable AI features. You can add more keys later in Settings.
                </p>
              </div>

              {/* OpenAI Key */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                  OpenAI API Key (Recommended)
                </label>
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <a
                  href="https://platform.openai.com/api-keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:underline mt-2"
                >
                  Get OpenAI API Key
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              {/* Anthropic Key */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                  Anthropic API Key (Optional)
                </label>
                <input
                  type="password"
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                  placeholder="sk-ant-..."
                  className="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <a
                  href="https://console.anthropic.com/account/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:underline mt-2"
                >
                  Get Anthropic API Key
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <p className="text-xs text-yellow-800 dark:text-yellow-300">
                  <strong>Note:</strong> If you don't have API keys yet, you can use Ollama for free local AI processing.
                  Install Ollama from <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer" className="underline">ollama.ai</a> and select "Ollama (Local)" as your provider.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={!openaiKey && !anthropicKey}
                  className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  Continue
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full mb-4">
                  <CheckCircle className="w-10 h-10 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  You're All Set!
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Your API keys have been saved. You can now use all AI-powered features in Argus.
                </p>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 dark:text-blue-200 text-sm mb-2">
                  Next Steps:
                </h4>
                <ul className="text-xs text-blue-800 dark:text-blue-300 space-y-1">
                  <li>• Upload documents to start analyzing</li>
                  <li>• Use Canvas to visualize entity relationships</li>
                  <li>• Generate AI insights on entities</li>
                  <li>• Chat with your documents</li>
                  <li>• Extract patterns and metadata</li>
                </ul>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={goToSettings}
                  className="px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium transition-colors"
                >
                  Go to Settings
                </button>
                <button
                  onClick={handleComplete}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  Start Using Argus
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
