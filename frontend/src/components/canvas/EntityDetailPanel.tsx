/**
 * Entity Detail Panel - Shows detailed information and AI insights when clicking canvas entities
 */

import { useState, useEffect } from 'react';
import { X, User, Building2, MapPin, Calendar, Sparkles, Search, Network, TrendingUp, AlertTriangle, Database, DollarSign, Phone, Mail } from 'lucide-react';
import { getApiUrl } from '../../config/api';
import { useCanvasStore } from '../../store/useCanvasStore';

interface EntityDetailPanelProps {
  entity: any;
  onClose: () => void;
}

export const EntityDetailPanel = ({ entity, onClose }: EntityDetailPanelProps) => {
  const [aiInsights, setAiInsights] = useState<any>(null);
  const [entityInfo, setEntityInfo] = useState<any>(null);
  const [metadata, setMetadata] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [infoLoading, setInfoLoading] = useState(false);
  const [metadataLoading, setMetadataLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'info' | 'connections' | 'metadata' | 'insights'>('info');
  const [provider, setProvider] = useState<string>('openai');  // Use OpenAI as default
  const [model, setModel] = useState<string | null>(''); // Empty string = use default model
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const [searchingImage, setSearchingImage] = useState(false);
  const [entityImageUrl, setEntityImageUrl] = useState<string | null>(entity.data.image_url || null);

  useEffect(() => {
    // Reset entity info when entity changes
    setEntityInfo(null);
    setAiInsights(null);
    setMetadata(null);
  }, [entity]);

  useEffect(() => {
    if (entity && activeTab === 'insights' && !aiInsights) {
      loadAIInsights();
    }
    if (entity && activeTab === 'info' && !entityInfo) {
      loadEntityInfo();
    }
    if (entity && activeTab === 'metadata' && !metadata) {
      loadMetadata();
    }
  }, [entity, activeTab, entityInfo, aiInsights, metadata]);

  const loadAIInsights = async () => {
    setLoading(true);
    try {
      const response = await fetch(getApiUrl(`/api/canvas/analyze-entity`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entity_name: entity.data.label,
          entity_type: entity.type,
          context: entity.data,
          provider: provider,
          model: model,
          system_prompt: systemPrompt || null
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAiInsights(data);
      }
    } catch (error) {
      console.error('Failed to load AI insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadEntityInfo = async () => {
    setInfoLoading(true);
    try {
      const response = await fetch(getApiUrl(`/api/canvas/entity-info`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entity_name: entity.data.label,
          entity_type: entity.type,
          provider: provider,
          model: model || null
        })
      });

      if (response.ok) {
        const data = await response.json();
        setEntityInfo(data);
      }
    } catch (error) {
      console.error('Failed to load entity info:', error);
    } finally {
      setInfoLoading(false);
    }
  };

  const loadMetadata = async () => {
    setMetadataLoading(true);
    try {
      const response = await fetch(getApiUrl(`/api/canvas/analyze-metadata`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entity_name: entity.data.label
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMetadata(data);
      }
    } catch (error) {
      console.error('Failed to load metadata:', error);
    } finally {
      setMetadataLoading(false);
    }
  };

  const searchForImage = async () => {
    setSearchingImage(true);
    try {
      const response = await fetch(getApiUrl(`/api/canvas/search-image`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entity_name: entity.data.label,
          entity_type: entity.type
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.images && data.images.length > 0) {
          // Update entity with first image
          const imageUrl = data.images[0].url;

          // Update local state to show image immediately
          setEntityImageUrl(imageUrl);

          // Update entity data
          entity.data.image_url = imageUrl;

          // Update the canvas store to persist the change
          const { updateNodeData } = useCanvasStore.getState();
          updateNodeData(entity.id, {
            image_url: imageUrl
          });
        }
      }
    } catch (error) {
      console.error('Failed to search for image:', error);
    } finally {
      setSearchingImage(false);
    }
  };

  const getEntityIcon = (type: string) => {
    switch (type) {
      case 'person': return <User className="w-5 h-5" />;
      case 'organization': return <Building2 className="w-5 h-5" />;
      case 'location': return <MapPin className="w-5 h-5" />;
      case 'date': return <Calendar className="w-5 h-5" />;
      default: return <Network className="w-5 h-5" />;
    }
  };

  const getEntityColor = (type: string) => {
    switch (type) {
      case 'person': return 'from-purple-500 to-pink-500';
      case 'organization': return 'from-orange-500 to-red-500';
      case 'location': return 'from-green-500 to-teal-500';
      case 'date': return 'from-blue-500 to-indigo-500';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  if (!entity) return null;

  return (
    <div className="fixed right-4 top-20 bottom-4 w-96 bg-white dark:bg-gray-900 rounded-xl shadow-2xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden z-50 flex flex-col">
      {/* Header */}
      <div className={`bg-gradient-to-r ${getEntityColor(entity.type)} p-4 text-white`}>
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-3">
            {/* Entity Photo or Icon */}
            {entityImageUrl ? (
              <img
                src={entityImageUrl}
                alt={entity.data.label}
                className="w-16 h-16 rounded-lg object-cover border-2 border-white/30 shadow-lg"
                onError={(e) => {
                  // Fallback to icon if image fails to load
                  e.currentTarget.style.display = 'none';
                  const iconDiv = e.currentTarget.nextElementSibling as HTMLElement;
                  if (iconDiv) iconDiv.style.display = 'flex';
                }}
              />
            ) : null}
            <div className={`p-2 bg-white/20 rounded-lg backdrop-blur-sm ${entityImageUrl ? 'hidden' : 'flex'}`}>
              {getEntityIcon(entity.type)}
            </div>
            <div>
              <h3 className="font-bold text-lg">{entity.data.label}</h3>
              <p className="text-sm text-white/80 capitalize">{entity.type}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex items-center justify-between">
          {entity.data.mention_count && (
            <div className="text-sm text-white/90">
              <span className="font-semibold">{entity.data.mention_count}</span> mentions across documents
            </div>
          )}
          {!entityImageUrl && (
            <button
              onClick={searchForImage}
              disabled={searchingImage}
              className="text-xs px-3 py-1 bg-white/20 hover:bg-white/30 rounded-lg transition-colors disabled:opacity-50"
            >
              {searchingImage ? 'Searching...' : '🔍 Find Photo'}
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <button
          onClick={() => setActiveTab('info')}
          className={`flex-1 px-3 py-3 text-sm font-medium transition-colors ${
            activeTab === 'info'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 bg-white dark:bg-gray-900'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          Info
        </button>
        <button
          onClick={() => setActiveTab('connections')}
          className={`flex-1 px-3 py-3 text-sm font-medium transition-colors ${
            activeTab === 'connections'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 bg-white dark:bg-gray-900'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          Links
        </button>
        <button
          onClick={() => setActiveTab('metadata')}
          className={`flex-1 px-3 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-1 ${
            activeTab === 'metadata'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 bg-white dark:bg-gray-900'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <Database className="w-4 h-4" />
          Data
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex-1 px-3 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-1 ${
            activeTab === 'insights'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 bg-white dark:bg-gray-900'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          AI
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'info' && (
          <div className="space-y-4">
            {infoLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mb-2"></div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Loading comprehensive information...</p>
                </div>
              </div>
            ) : entityInfo ? (
              <div className="space-y-6">
                {/* Who They Are */}
                {entityInfo.who_they_are && (
                  <div>
                    <h4 className="text-sm font-bold text-blue-600 dark:text-blue-400 mb-2 uppercase tracking-wide">Who They Are</h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{entityInfo.who_they_are}</p>
                  </div>
                )}

                {/* Background & Past */}
                {entityInfo.background && (
                  <div>
                    <h4 className="text-sm font-bold text-purple-600 dark:text-purple-400 mb-2 uppercase tracking-wide">Background & Past</h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">{entityInfo.background}</p>
                  </div>
                )}

                {/* Connection to Investigation */}
                {entityInfo.connection && (
                  <div>
                    <h4 className="text-sm font-bold text-orange-600 dark:text-orange-400 mb-2 uppercase tracking-wide">Connection to Investigation</h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{entityInfo.connection}</p>
                  </div>
                )}

                {/* Evidence from Documents */}
                {entityInfo.evidence && entityInfo.evidence.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-green-600 dark:text-green-400 mb-2 uppercase tracking-wide">Evidence (Document Excerpts)</h4>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {entityInfo.evidence.map((doc: any, idx: number) => (
                        <div key={idx} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border-l-4 border-green-500">
                          <p className="text-xs text-gray-700 dark:text-gray-300 mb-1">"{doc.excerpt}"</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                              {doc.document_name || 'Document'}
                            </span>
                            {doc.document_id && (
                              <a
                                href={`/documents?doc=${doc.document_id}`}
                                className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                View Source →
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Key Associations */}
                {entityInfo.associations && entityInfo.associations.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-indigo-600 dark:text-indigo-400 mb-2 uppercase tracking-wide">Key Associations</h4>
                    <div className="flex flex-wrap gap-2">
                      {entityInfo.associations.map((assoc: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded text-xs font-medium">
                          {assoc}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Theory/Conclusion */}
                {entityInfo.theory && (
                  <div className="border-t-2 border-gray-200 dark:border-gray-700 pt-4">
                    <h4 className="text-sm font-bold text-red-600 dark:text-red-400 mb-2 uppercase tracking-wide">Theory & Conclusion</h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed italic">{entityInfo.theory}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Basic Details</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Type:</span>
                      <span className="font-medium text-gray-900 dark:text-white capitalize">{entity.type}</span>
                    </div>
                    {entity.data.confidence && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Confidence:</span>
                        <span className="font-medium text-gray-900 dark:text-white">{(entity.data.confidence * 100).toFixed(0)}%</span>
                      </div>
                    )}
                    {entity.data.normalized_name && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Normalized:</span>
                        <span className="font-medium text-gray-900 dark:text-white">{entity.data.normalized_name}</span>
                      </div>
                    )}
                  </div>
                </div>

                {entity.data.metadata && Object.keys(entity.data.metadata).length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Metadata</h4>
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-sm">
                      <pre className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                        {JSON.stringify(entity.data.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'connections' && (
          <div className="space-y-4">
            {infoLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mb-2"></div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Discovering connections...</p>
                </div>
              </div>
            ) : entityInfo?.connected_entities && entityInfo.connected_entities.length > 0 ? (
              <div>
                <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 mb-4">
                  <Network className="w-5 h-5" />
                  <h4 className="font-semibold">Related Entities ({entityInfo.connected_entities.length})</h4>
                </div>
                <div className="space-y-2">
                  {entityInfo.connected_entities.map((conn: any, idx: number) => (
                    <div key={idx} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          {getEntityIcon(conn.type)}
                          <span className="font-medium text-gray-900 dark:text-white">{conn.label}</span>
                        </div>
                        <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded capitalize">
                          {conn.type}
                        </span>
                      </div>
                      {conn.relationship && (
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          Relationship: <span className="font-medium">{conn.relationship}</span>
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <Network className="w-12 h-12 text-gray-400 dark:text-gray-600 mx-auto mb-3 opacity-50" />
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  No connections found for this entity yet.
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                  Connections will appear as more documents are analyzed.
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'metadata' && (
          <div className="space-y-4">
            {metadataLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 dark:border-emerald-400 mb-2"></div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Extracting metadata...</p>
                </div>
              </div>
            ) : metadata ? (
              <div className="space-y-6">
                {/* Dates */}
                {metadata.dates && metadata.dates.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 mb-3">
                      <Calendar className="w-5 h-5" />
                      <h4 className="font-semibold">Dates ({metadata.dates.length})</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {metadata.dates.slice(0, 20).map((date: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs font-medium">
                          {date}
                        </span>
                      ))}
                      {metadata.dates.length > 20 && (
                        <span className="px-2 py-1 text-xs text-gray-500 dark:text-gray-400">
                          +{metadata.dates.length - 20} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Locations */}
                {metadata.locations && metadata.locations.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-green-600 dark:text-green-400 mb-3">
                      <MapPin className="w-5 h-5" />
                      <h4 className="font-semibold">Locations ({metadata.locations.length})</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {metadata.locations.map((loc: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded text-xs font-medium">
                          {loc}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Organizations */}
                {metadata.organizations && metadata.organizations.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-orange-600 dark:text-orange-400 mb-3">
                      <Building2 className="w-5 h-5" />
                      <h4 className="font-semibold">Organizations ({metadata.organizations.length})</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {metadata.organizations.map((org: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded text-xs font-medium">
                          {org}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Phone Numbers */}
                {metadata.phone_numbers && metadata.phone_numbers.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 mb-3">
                      <Phone className="w-5 h-5" />
                      <h4 className="font-semibold">Phone Numbers ({metadata.phone_numbers.length})</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {metadata.phone_numbers.map((phone: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded text-xs font-mono">
                          {phone}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Emails */}
                {metadata.emails && metadata.emails.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 mb-3">
                      <Mail className="w-5 h-5" />
                      <h4 className="font-semibold">Email Addresses ({metadata.emails.length})</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {metadata.emails.map((email: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded text-xs font-mono">
                          {email}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Financial Amounts */}
                {metadata.financial_amounts && metadata.financial_amounts.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 mb-3">
                      <DollarSign className="w-5 h-5" />
                      <h4 className="font-semibold">Financial Amounts ({metadata.financial_amounts.length})</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {metadata.financial_amounts.map((amount: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded text-xs font-medium">
                          ${amount}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Co-occurring Entities */}
                {metadata.co_occurring_entities && metadata.co_occurring_entities.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-pink-600 dark:text-pink-400 mb-3">
                      <Network className="w-5 h-5" />
                      <h4 className="font-semibold">Frequently Mentioned With ({metadata.co_occurring_entities.length})</h4>
                    </div>
                    <div className="space-y-2">
                      {metadata.co_occurring_entities.slice(0, 10).map((coEntity: any, idx: number) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                          <span className="text-sm text-gray-900 dark:text-white font-medium">{coEntity.entity}</span>
                          <span className="text-xs px-2 py-1 bg-pink-100 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300 rounded">
                            {coEntity.mentions} mentions
                          </span>
                        </div>
                      ))}
                      {metadata.co_occurring_entities.length > 10 && (
                        <p className="text-xs text-center text-gray-500 dark:text-gray-400">
                          +{metadata.co_occurring_entities.length - 10} more entities
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Documents */}
                {metadata.documents && metadata.documents.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400 mb-3">
                      <Search className="w-5 h-5" />
                      <h4 className="font-semibold">Mentioned in Documents ({metadata.documents.length})</h4>
                    </div>
                    <div className="space-y-2">
                      {metadata.documents.map((doc: string, idx: number) => (
                        <div key={idx} className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs text-gray-700 dark:text-gray-300">
                          {doc}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Total Mentions */}
                {metadata.total_mentions && (
                  <div className="border-t pt-4 border-gray-200 dark:border-gray-700">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{metadata.total_mentions}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Total mentions across all documents</div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <Database className="w-12 h-12 text-gray-400 dark:text-gray-600 mx-auto mb-3 opacity-50" />
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  No metadata extracted yet.
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                  Click to load metadata from documents.
                </p>
                <button
                  onClick={loadMetadata}
                  className="mt-4 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium transition-all"
                >
                  Load Metadata
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-4">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 dark:border-purple-400 mb-2"></div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Analyzing with AI...</p>
                </div>
              </div>
            ) : aiInsights ? (
              <div className="space-y-4">
                {aiInsights.theories && aiInsights.theories.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 mb-2">
                      <TrendingUp className="w-4 h-4" />
                      <h4 className="font-semibold text-sm">Theories</h4>
                    </div>
                    <ul className="space-y-2">
                      {aiInsights.theories.map((theory: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-700 dark:text-gray-300 pl-4 border-l-2 border-purple-300 dark:border-purple-700">
                          {theory}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {aiInsights.suggestions && aiInsights.suggestions.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 mb-2">
                      <Search className="w-4 h-4" />
                      <h4 className="font-semibold text-sm">Suggestions</h4>
                    </div>
                    <ul className="space-y-2">
                      {aiInsights.suggestions.map((suggestion: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-700 dark:text-gray-300 pl-4 border-l-2 border-blue-300 dark:border-blue-700">
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {aiInsights.warnings && aiInsights.warnings.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-orange-600 dark:text-orange-400 mb-2">
                      <AlertTriangle className="w-4 h-4" />
                      <h4 className="font-semibold text-sm">Considerations</h4>
                    </div>
                    <ul className="space-y-2">
                      {aiInsights.warnings.map((warning: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-700 dark:text-gray-300 pl-4 border-l-2 border-orange-300 dark:border-orange-700">
                          {warning}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <Sparkles className="w-12 h-12 text-purple-600 dark:text-purple-400 mx-auto mb-3 opacity-50" />
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Click to generate AI-powered insights, theories, and investigation suggestions
                </p>

                {/* System Prompt (Optional) */}
                <div className="max-w-md mx-auto mb-4">
                  <button
                    onClick={() => setShowSystemPrompt(!showSystemPrompt)}
                    className="text-xs text-blue-600 dark:text-blue-400 hover:underline mb-2"
                  >
                    {showSystemPrompt ? '- Hide' : '+ Add'} Custom System Prompt
                  </button>
                  {showSystemPrompt && (
                    <textarea
                      value={systemPrompt}
                      onChange={(e) => setSystemPrompt(e.target.value)}
                      placeholder="Custom instructions for AI analysis (optional)..."
                      className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-purple-500"
                      rows={3}
                    />
                  )}
                </div>

                {/* Provider Selection */}
                <div className="max-w-xs mx-auto mb-4 space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">AI Provider</label>
                    <select
                      value={provider}
                      onChange={(e) => setProvider(e.target.value)}
                      className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="ollama">Ollama (Local)</option>
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                    </select>
                  </div>

                  {/* Model Selection */}
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Model (Optional)</label>
                    <select
                      value={model || ''}
                      onChange={(e) => setModel(e.target.value || null)}
                      className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="">Default</option>
                      {provider === 'openai' && (
                        <>
                          <option value="gpt-4o">GPT-4o</option>
                          <option value="gpt-4o-mini">GPT-4o Mini</option>
                          <option value="gpt-4-turbo">GPT-4 Turbo</option>
                        </>
                      )}
                      {provider === 'anthropic' && (
                        <>
                          <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
                          <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                          <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                        </>
                      )}
                      {provider === 'ollama' && (
                        <option value="llama3:8b">Llama 3 8B</option>
                      )}
                    </select>
                  </div>
                </div>

                <button
                  onClick={loadAIInsights}
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg text-sm font-medium transition-all"
                >
                  Generate Insights
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
