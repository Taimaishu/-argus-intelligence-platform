/**
 * Browser compatibility alert for speech features
 */

import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';

export const BrowserCompatibilityAlert = () => {
  const ttsSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;
  const sttSupported = typeof window !== 'undefined' &&
    (('SpeechRecognition' in window) || ('webkitSpeechRecognition' in window));

  // Don't show if both are supported
  if (ttsSupported && sttSupported) {
    return null;
  }

  return (
    <div className="mb-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
            Speech Features Status
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              {ttsSupported ? (
                <>
                  <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                  <span className="text-yellow-900 dark:text-yellow-100">Text-to-Speech: Supported</span>
                </>
              ) : (
                <>
                  <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                  <span className="text-yellow-900 dark:text-yellow-100">Text-to-Speech: Not supported</span>
                </>
              )}
            </div>
            <div className="flex items-center gap-2">
              {sttSupported ? (
                <>
                  <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                  <span className="text-yellow-900 dark:text-yellow-100">Speech-to-Text: Supported</span>
                </>
              ) : (
                <>
                  <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                  <span className="text-yellow-900 dark:text-yellow-100">
                    Speech-to-Text: Not supported or requires HTTPS
                  </span>
                </>
              )}
            </div>
          </div>
          {!sttSupported && (
            <div className="mt-3 text-sm text-yellow-800 dark:text-yellow-200 space-y-2">
              <p>
                <strong>Brave Browser users:</strong> Speech-to-text requires Google services which Brave blocks by default.
              </p>
              <p className="font-semibold">To enable voice input in Brave:</p>
              <ol className="list-decimal ml-5 space-y-1">
                <li>Click the Brave Shields icon (🦁) in the address bar</li>
                <li>Click "Advanced View"</li>
                <li>Under "Block cross-site cookies", select "All cookies allowed"</li>
                <li>Refresh this page</li>
              </ol>
              <p className="italic">
                Or use text input instead - voice features are optional!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
