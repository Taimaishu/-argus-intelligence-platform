/**
 * Artifact list component
 */

import { useEffect } from 'react';
import { Shield, Trash2, AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react';
import { useOSINTStore } from '../../store/useOSINTStore';
import type { Artifact } from '../../store/useOSINTStore';

const ThreatBadge = ({ level }: { level: string }) => {
  const configs = {
    critical: { bg: 'from-red-100 to-rose-100 dark:from-red-900/30 dark:to-rose-900/30', text: 'text-red-700 dark:text-red-300', border: 'border-red-300 dark:border-red-700', icon: XCircle },
    high: { bg: 'from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30', text: 'text-orange-700 dark:text-orange-300', border: 'border-orange-300 dark:border-orange-700', icon: AlertTriangle },
    medium: { bg: 'from-yellow-100 to-amber-100 dark:from-yellow-900/30 dark:to-amber-900/30', text: 'text-yellow-700 dark:text-yellow-300', border: 'border-yellow-300 dark:border-yellow-700', icon: AlertTriangle },
    low: { bg: 'from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30', text: 'text-blue-700 dark:text-blue-300', border: 'border-blue-300 dark:border-blue-700', icon: Clock },
    safe: { bg: 'from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30', text: 'text-green-700 dark:text-green-300', border: 'border-green-300 dark:border-green-700', icon: CheckCircle },
    unknown: { bg: 'from-gray-100 to-slate-100 dark:from-gray-800 dark:to-slate-800', text: 'text-gray-700 dark:text-gray-300', border: 'border-gray-300 dark:border-gray-600', icon: Clock }
  };

  const config = configs[level as keyof typeof configs] || configs.unknown;
  const Icon = config.icon;

  return (
    <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r ${config.bg} border ${config.border}`}>
      <Icon className={`w-4 h-4 ${config.text}`} />
      <span className={`text-sm font-semibold ${config.text} uppercase`}>{level}</span>
    </div>
  );
};

const ArtifactCard = ({ artifact, onDelete }: { artifact: Artifact; onDelete: (id: number) => void }) => {
  return (
    <div className="group bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-5 shadow-lg hover:shadow-2xl dark:shadow-gray-900/50 transition-all duration-300 transform hover:scale-[1.01]">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-lg">
            <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <span className="px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full">
              {artifact.artifact_type.replace('_', ' ').toUpperCase()}
            </span>
          </div>
        </div>

        <button
          onClick={() => onDelete(artifact.id)}
          className="p-2 opacity-0 group-hover:opacity-100 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="mb-3">
        <code className="text-lg font-mono font-semibold text-gray-900 dark:text-white break-all">
          {artifact.value}
        </code>
      </div>

      <div className="flex items-center justify-between">
        <ThreatBadge level={artifact.threat_level} />
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {new Date(artifact.first_seen).toLocaleDateString()}
        </span>
      </div>

      {artifact.analysis_data && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-600 dark:text-gray-400">
          {artifact.artifact_type === 'ip_address' && artifact.analysis_data.geolocation && (
            <div>
              📍 {artifact.analysis_data.geolocation.city}, {artifact.analysis_data.geolocation.country}
            </div>
          )}
          {artifact.artifact_type === 'hash' && artifact.analysis_data.detections && (
            <div>
              🔍 {artifact.analysis_data.detections.detection_ratio} detections
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const ArtifactList = () => {
  const { artifacts, loading, error, fetchArtifacts, deleteArtifact } = useOSINTStore();

  useEffect(() => {
    fetchArtifacts();
  }, [fetchArtifacts]);

  const handleDelete = async (id: number) => {
    if (confirm('Delete this artifact?')) {
      try {
        await deleteArtifact(id);
      } catch (error) {
        console.error('Delete error:', error);
      }
    }
  };

  if (loading && artifacts.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400 animate-pulse" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-red-800 dark:text-red-400">
        Error: {error}
      </div>
    );
  }

  if (artifacts.length === 0) {
    return (
      <div className="text-center py-12">
        <Shield className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
        <p className="text-lg text-gray-500 dark:text-gray-400">No artifacts analyzed yet</p>
        <p className="text-sm text-gray-400 dark:text-gray-500">Submit an artifact to get started</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {artifacts.map(artifact => (
        <ArtifactCard
          key={artifact.id}
          artifact={artifact}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
};
