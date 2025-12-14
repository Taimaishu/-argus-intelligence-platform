/**
 * Pattern Insights Component
 * Shows similar documents, connections, and clustering information
 */

import { useState, useEffect } from 'react';
import { Network, TrendingUp, Users, Link as LinkIcon, Loader2 } from 'lucide-react';

interface SimilarDocument {
  document_id: number;
  filename: string;
  similarity: number;
  matching_chunks: number;
}

interface Connection {
  target_document_id: number;
  connection_type: string;
  strength: number;
  confidence: string;
  reason: string;
}

interface ClusterMembership {
  cluster_id: number;
  theme: string;
  size: number;
}

interface Insights {
  similar_documents: SimilarDocument[];
  suggested_connections: Connection[];
  cluster_membership: ClusterMembership | null;
  total_similar: number;
  total_connections: number;
}

interface PatternInsightsProps {
  documentId: number;
}

export const PatternInsights = ({ documentId }: PatternInsightsProps) => {
  const [insights, setInsights] = useState<Insights | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInsights = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`http://localhost:8000/api/patterns/insights/${documentId}`);
        if (!response.ok) throw new Error('Failed to fetch insights');

        const data = await response.json();
        setInsights(data);
      } catch (err) {
        console.error('Error fetching insights:', err);
        setError('Failed to load pattern insights');
      } finally {
        setIsLoading(false);
      }
    };

    if (documentId) {
      fetchInsights();
    }
  }, [documentId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6">
        <p className="text-red-600 dark:text-red-400">{error}</p>
      </div>
    );
  }

  if (!insights) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Network className="w-6 h-6 text-purple-600 dark:text-purple-400" />
          Pattern Insights
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          AI-discovered connections and relationships
        </p>
      </div>

      {/* Cluster Membership */}
      {insights.cluster_membership && (
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-500 dark:bg-purple-600 rounded-lg">
              <Users className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white">Theme Cluster</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                This document belongs to a themed group
              </p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Theme:</span>
              <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 rounded-full text-sm font-semibold">
                {insights.cluster_membership.theme}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Documents in group:</span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {insights.cluster_membership.size}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Similar Documents */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-500 dark:bg-blue-600 rounded-lg">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white">Similar Documents</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {insights.total_similar} related {insights.total_similar === 1 ? 'document' : 'documents'} found
            </p>
          </div>
        </div>

        {insights.similar_documents.length > 0 ? (
          <div className="space-y-2">
            {insights.similar_documents.map((doc) => (
              <div
                key={doc.document_id}
                className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-blue-200 dark:border-blue-700 hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 dark:text-white truncate">
                      {doc.filename}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {doc.matching_chunks} matching {doc.matching_chunks === 1 ? 'section' : 'sections'}
                    </p>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className={`text-xs font-semibold px-2 py-1 rounded ${
                      doc.similarity > 0.85
                        ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
                        : doc.similarity > 0.75
                        ? 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}>
                      {(doc.similarity * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            No similar documents found
          </p>
        )}
      </div>

      {/* Suggested Connections */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-green-500 dark:bg-green-600 rounded-lg">
            <LinkIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white">Suggested Connections</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {insights.total_connections} high-confidence {insights.total_connections === 1 ? 'connection' : 'connections'}
            </p>
          </div>
        </div>

        {insights.suggested_connections.length > 0 ? (
          <div className="space-y-2">
            {insights.suggested_connections.slice(0, 5).map((conn, idx) => (
              <div
                key={idx}
                className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-green-200 dark:border-green-700"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      Document #{conn.target_document_id}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {conn.reason}
                    </p>
                  </div>
                  <span className={`text-xs font-semibold px-2 py-1 rounded ${
                    conn.confidence === 'high'
                      ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
                      : 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300'
                  }`}>
                    {conn.confidence}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            No strong connections detected
          </p>
        )}
      </div>
    </div>
  );
};
