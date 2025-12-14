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
            <p className="mt-3 text-sm text-yellow-800 dark:text-yellow-200">
              <strong>Brave Browser users:</strong> Make sure you've granted microphone permissions
              and are accessing via localhost or HTTPS.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
