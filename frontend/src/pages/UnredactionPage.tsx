/**
 * Unredaction page - recover redacted text from documents
 */

import { useState, useCallback } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, Eye, EyeOff, TrendingUp } from 'lucide-react';
import { getApiUrl } from '../config/api';

interface RedactedRegion {
  page: number;
  bbox: number[];
  type: string;
  context_before: string;
  context_after: string;
}

interface Prediction {
  original: string;
  predicted: string;
  confidence: number;
  method: string;
  context: string;
}

interface AnalysisResult {
  filename: string;
  file_type: string;
  total_pages: number;
  summary: {
    total_redactions: number;
    predictions_made: number;
    high_confidence: number;
    medium_confidence: number;
    low_confidence: number;
  };
  redacted_regions: RedactedRegion[];
  predictions: Prediction[];
  analysis_complete: boolean;
}

export const UnredactionPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [useAI, setUseAI] = useState(false);  // Default OFF - AI is slow (10-20s per redaction)
  const [useOCR, setUseOCR] = useState(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setResult(null);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const url = getApiUrl(`/api/unredaction/analyze?use_ai=${useAI}&use_ocr=${useOCR}`);
      console.log('=== UNREDACTION DEBUG ===');
      console.log('Submitting to:', url);
      console.log('File:', file.name, 'Size:', file.size);
      console.log('Use AI:', useAI, 'Use OCR:', useOCR);

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      }).catch(err => {
        console.error('Fetch error:', err);
        throw err;
      });

      console.log('Response received!');
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error response:', errorData);
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data: AnalysisResult = await response.json();
      console.log('Success! Result:', data);
      setResult(data);
    } catch (err) {
      console.error('Caught error:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyze document');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600 dark:text-green-400';
    if (confidence >= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getConfidenceBg = (confidence: number) => {
    if (confidence >= 80) return 'bg-green-100 dark:bg-green-900/30';
    if (confidence >= 50) return 'bg-yellow-100 dark:bg-yellow-900/30';
    return 'bg-red-100 dark:bg-red-900/30';
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Document Unredaction</h2>
        <p className="text-gray-600 dark:text-gray-400">
          Recover redacted information from documents using AI-powered analysis
        </p>
      </div>

      {/* Upload Form */}
      <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl">
            <Eye className="w-6 h-6 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">Upload Document</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">PDF or image files supported</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center hover:border-purple-500 dark:hover:border-purple-400 transition-colors">
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
              disabled={loading}
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center gap-3"
            >
              <Upload className="w-12 h-12 text-gray-400 dark:text-gray-500" />
              <div>
                <span className="text-purple-600 dark:text-purple-400 font-medium">
                  Click to upload
                </span>
                <span className="text-gray-600 dark:text-gray-400"> or drag and drop</span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                PDF, PNG, JPG, TIFF (max 50MB)
              </p>
            </label>
          </div>

          {file && (
            <div className="flex items-center gap-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <FileText className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <span className="flex-1 text-sm text-gray-700 dark:text-gray-300">{file.name}</span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>
          )}

          {/* Options */}
          <div className="flex items-center gap-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                disabled={loading}
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">AI Inference</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useOCR}
                onChange={(e) => setUseOCR(e.target.checked)}
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                disabled={loading}
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                OCR (requires Tesseract)
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading || !file}
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-500 dark:to-pink-500 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 dark:hover:from-purple-600 dark:hover:to-pink-600 disabled:from-gray-300 disabled:to-gray-400 dark:disabled:from-gray-700 dark:disabled:to-gray-800 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 font-medium"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Eye className="w-5 h-5" />
                Analyze Document
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
          <span className="text-red-800 dark:text-red-400">{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">Analysis Complete</h3>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {result.summary.total_redactions}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Redactions</div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {result.summary.high_confidence}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">High Confidence</div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {result.summary.medium_confidence}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Medium Confidence</div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {result.summary.low_confidence}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Low Confidence</div>
              </div>
            </div>
          </div>

          {/* Predictions */}
          {result.predictions.length > 0 && (
            <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                Recovered Information
              </h3>

              <div className="space-y-3">
                {result.predictions.map((pred, idx) => (
                  <div
                    key={idx}
                    className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border-l-4 border-purple-500"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                            Original:
                          </span>
                          <code className="text-sm text-gray-700 dark:text-gray-300 font-mono">
                            {pred.original}
                          </code>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                            Predicted:
                          </span>
                          <code className="text-sm font-semibold text-purple-600 dark:text-purple-400 font-mono">
                            {pred.predicted}
                          </code>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <TrendingUp className={`w-4 h-4 ${getConfidenceColor(pred.confidence)}`} />
                        <span
                          className={`px-3 py-1 ${getConfidenceBg(pred.confidence)} ${getConfidenceColor(pred.confidence)} rounded-full text-sm font-semibold`}
                        >
                          {pred.confidence}%
                        </span>
                      </div>
                    </div>

                    {pred.context && (
                      <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                        <span className="text-xs text-gray-500 dark:text-gray-400">Context: </span>
                        <span className="text-xs text-gray-600 dark:text-gray-400 italic">
                          {pred.context}
                        </span>
                      </div>
                    )}

                    <div className="mt-2">
                      <span className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">
                        {pred.method}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detected Regions */}
          {result.redacted_regions.length > 0 && (
            <div className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-lg">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                Detected Redactions ({result.redacted_regions.length})
              </h3>

              <div className="space-y-2 max-h-60 overflow-y-auto">
                {result.redacted_regions.map((region, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg flex items-center justify-between"
                  >
                    <div>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Page {region.page}
                      </span>
                      <span className="mx-2 text-gray-400">•</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                        {region.type}
                      </span>
                    </div>
                    <EyeOff className="w-4 h-4 text-gray-400 dark:text-gray-500" />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
