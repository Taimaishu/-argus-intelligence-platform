/**
 * Patterns page for visualizing document relationships and clusters
 */

import { useState, useEffect } from 'react';
import { Network, Users, TrendingUp, Loader2, RefreshCw } from 'lucide-react';

interface NetworkAnalysis {
  central_documents: Array<{
    document_id: number;
    filename: string;
    connections: number;
    centrality_score: number;
  }>;
  isolated_documents: Array<{
    document_id: number;
    filename: string;
  }>;
  network_density: number;
  total_connections: number;
  total_documents: number;
}

interface Cluster {
  cluster_id: number;
  documents: Array<{
    id: number;
    filename: string;
    title: string;
  }>;
  size: number;
}

interface Theme {
  cluster_id: number;
  theme_name: string;
  document_count: number;
}

interface ClusteringResult {
  clusters: Cluster[];
  themes: Theme[];
  total_documents: number;
  n_clusters: number;
}

export const PatternsPage = () => {
  const [networkAnalysis, setNetworkAnalysis] = useState<NetworkAnalysis | null>(null);
  const [clustering, setClustering] = useState<ClusteringResult | null>(null);
  const [isLoadingNetwork, setIsLoadingNetwork] = useState(false);
  const [isLoadingClusters, setIsLoadingClusters] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNetworkAnalysis = async () => {
    setIsLoadingNetwork(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/patterns/network');
      if (!response.ok) throw new Error('Failed to fetch network analysis');

      const data = await response.json();
      setNetworkAnalysis(data);
    } catch (err) {
      console.error('Error fetching network analysis:', err);
      setError('Failed to load network analysis');
    } finally {
      setIsLoadingNetwork(false);
    }
  };

  const fetchClustering = async () => {
    setIsLoadingClusters(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/patterns/cluster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      if (!response.ok) throw new Error('Failed to fetch clustering');

      const data = await response.json();
      setClustering(data);
    } catch (err) {
      console.error('Error fetching clustering:', err);
      setError('Failed to load document clusters');
    } finally {
      setIsLoadingClusters(false);
    }
  };

  useEffect(() => {
    fetchNetworkAnalysis();
    fetchClustering();
  }, []);

  const handleRefresh = () => {
    fetchNetworkAnalysis();
    fetchClustering();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Pattern Analysis</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            AI-discovered patterns, themes, and relationships across your documents
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isLoadingNetwork || isLoadingClusters}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
        >
          <RefreshCw className={`w-5 h-5 ${(isLoadingNetwork || isLoadingClusters) ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Network Analysis */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-blue-600 dark:bg-blue-700 rounded-xl shadow-md">
            <Network className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Network Analysis</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Understanding document relationships and connectivity
            </p>
          </div>
        </div>

        {isLoadingNetwork ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-400" />
          </div>
        ) : networkAnalysis ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Network Stats */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                {networkAnalysis.total_documents}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Documents
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                {networkAnalysis.total_connections}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Strong Connections
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">
                {(networkAnalysis.network_density * 100).toFixed(1)}%
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Network Density
              </div>
            </div>
          </div>
        ) : null}

        {/* Central Documents */}
        {networkAnalysis && networkAnalysis.central_documents.length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              Most Connected Documents
            </h3>
            <div className="space-y-2">
              {networkAnalysis.central_documents.map((doc) => (
                <div
                  key={doc.document_id}
                  className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-blue-200 dark:border-blue-700 hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white truncate">
                        {doc.filename}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Centrality score: {(doc.centrality_score * 100).toFixed(1)}%
                      </p>
                    </div>
                    <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 rounded-full text-sm font-semibold ml-3">
                      {doc.connections} connections
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Isolated Documents */}
        {networkAnalysis && networkAnalysis.isolated_documents.length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Isolated Documents ({networkAnalysis.isolated_documents.length})
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              These documents have no strong semantic connections to others
            </p>
            <div className="flex flex-wrap gap-2">
              {networkAnalysis.isolated_documents.map((doc) => (
                <span
                  key={doc.document_id}
                  className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm"
                >
                  {doc.filename}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Document Clusters */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-6 shadow-lg">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-purple-600 dark:bg-purple-700 rounded-xl shadow-md">
            <Users className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Theme Clusters</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Documents grouped by content similarity
            </p>
          </div>
        </div>

        {isLoadingClusters ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-purple-600 dark:text-purple-400" />
          </div>
        ) : clustering ? (
          <div>
            <div className="flex items-center gap-4 mb-6">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {clustering.n_clusters} Themes
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                across {clustering.total_documents} documents
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {clustering.themes.map((theme) => {
                const cluster = clustering.clusters.find((c) => c.cluster_id === theme.cluster_id);
                return (
                  <div
                    key={theme.cluster_id}
                    className="bg-white dark:bg-gray-800 rounded-lg p-4 border-2 border-purple-200 dark:border-purple-700 hover:border-purple-400 dark:hover:border-purple-500 transition-all hover:scale-105"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                        {theme.theme_name}
                      </h3>
                      <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 rounded-full text-xs font-semibold">
                        {theme.document_count}
                      </span>
                    </div>
                    {cluster && (
                      <ul className="space-y-2">
                        {cluster.documents.slice(0, 3).map((doc) => (
                          <li
                            key={doc.id}
                            className="text-sm text-gray-600 dark:text-gray-400 truncate"
                          >
                            • {doc.title}
                          </li>
                        ))}
                        {cluster.documents.length > 3 && (
                          <li className="text-sm text-gray-500 dark:text-gray-500 italic">
                            + {cluster.documents.length - 3} more
                          </li>
                        )}
                      </ul>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
