/**
 * Canvas page for visualizing connections
 */

import { useEffect, useCallback, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Connection,
  BackgroundVariant,
  Panel,
  ReactFlowProvider,
  useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Plus, FileText, Lightbulb, StickyNote, Save, Trash2,
  Sparkles, Network, MessageSquare, ChevronLeft, ChevronRight, Image
} from 'lucide-react';

import { useCanvasStore } from '../store/useCanvasStore';
import { useForceDirectedLayout } from '../hooks/useForceDirectedLayout';
import { getApiUrl } from '../config/api';

// Original node types
import { DocumentNode } from '../components/canvas/DocumentNode';
import { InsightNode } from '../components/canvas/InsightNode';
import { NoteNode } from '../components/canvas/NoteNode';

// Entity node types
import { PersonNode } from '../components/canvas/PersonNode';
import { OrganizationNode } from '../components/canvas/OrganizationNode';
import { LocationNode } from '../components/canvas/LocationNode';
import { DateNode } from '../components/canvas/DateNode';
import { EventNode } from '../components/canvas/EventNode';
import { VehicleNode } from '../components/canvas/VehicleNode';
import { FinancialNode } from '../components/canvas/FinancialNode';
import { PhoneNode } from '../components/canvas/PhoneNode';
import { EmailNode } from '../components/canvas/EmailNode';
import { AddressNode } from '../components/canvas/AddressNode';

// Canvas chat panel
import { CanvasChatPanel } from '../components/canvas/CanvasChatPanel';

// Entity detail panel
import { EntityDetailPanel } from '../components/canvas/EntityDetailPanel';

// AI Provider Selector
import { AIProviderSelector } from '../components/common/AIProviderSelector';

// Define custom node types
const nodeTypes = {
  // Original types
  document: DocumentNode,
  insight: InsightNode,
  note: NoteNode,
  // Entity types
  person: PersonNode,
  organization: OrganizationNode,
  location: LocationNode,
  date: DateNode,
  event: EventNode,
  vehicle: VehicleNode,
  financial: FinancialNode,
  phone: PhoneNode,
  email: EmailNode,
  address: AddressNode,
};

const CanvasPageInner = () => {
  const {
    nodes,
    edges,
    isLoading,
    isSaving,
    isGenerating,
    generationProgress,
    onNodesChange,
    onEdgesChange,
    addNode,
    addEdge: addEdgeToStore,
    deleteNode,
    loadCanvas,
    saveCanvas,
    clearCanvas,
    autoGenerateEpstein,
    highlightNodes,
    setNodes,
  } = useCanvasStore();

  const [showAddMenu, setShowAddMenu] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedLayout, setSelectedLayout] = useState<'hierarchical' | 'force_directed' | 'circular'>('hierarchical');
  const [selectedEntity, setSelectedEntity] = useState<any>(null);
  const [isSearchingPhotos, setIsSearchingPhotos] = useState(false);
  const [photoSearchResults, setPhotoSearchResults] = useState<any>(null);
  const { fitView } = useReactFlow();
  const { applyLayout } = useForceDirectedLayout();

  // Load canvas on mount
  useEffect(() => {
    loadCanvas();
  }, [loadCanvas]);

  // Handle new connections
  const onConnect = useCallback(
    (connection: Connection) => {
      const edge = {
        id: `edge-${Date.now()}-${Math.random()}`,
        source: connection.source!,
        target: connection.target!,
        type: 'default',
      };
      addEdgeToStore(edge);
    },
    [addEdgeToStore]
  );

  // Handle node click to show entity details
  const onNodeClick = useCallback((event: React.MouseEvent, node: any) => {
    setSelectedEntity(node);
  }, []);

  // Add new node
  const handleAddNode = (type: 'document' | 'insight' | 'note') => {
    const newNode = {
      id: `${type}-${Date.now()}-${Math.random()}`,
      type,
      position: {
        x: Math.random() * 400 + 100,
        y: Math.random() * 400 + 100,
      },
      data: {
        label: `New ${type.charAt(0).toUpperCase() + type.slice(1)}`,
        content: '',
      },
    };

    addNode(newNode);
    setShowAddMenu(false);
  };

  const handleClearCanvas = async () => {
    if (confirm('Are you sure you want to clear the entire canvas? This cannot be undone.')) {
      await clearCanvas();
    }
  };

  // Auto-generate from Epstein files
  const handleAutoGenerate = async () => {
    if (nodes.length > 0) {
      const confirmed = confirm(
        'This will replace the current canvas with auto-generated content. Continue?'
      );
      if (!confirmed) return;
    }

    await autoGenerateEpstein();

    // Fit view after generation
    setTimeout(() => {
      fitView({ padding: 0.2, duration: 800 });
    }, 500);
  };

  // Find photos for all entities
  const handleFindAllPhotos = async () => {
    setIsSearchingPhotos(true);
    setPhotoSearchResults(null);

    try {
      const response = await fetch(getApiUrl('/api/canvas/search-all-images'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        const results = await response.json();
        setPhotoSearchResults(results);

        // Reload canvas to show new images
        await loadCanvas();

        // Show results
        const message = `Photo search complete!\n\nTotal entities: ${results.total}\nPhotos found: ${results.found}\nAlready had photos: ${results.skipped}\n\nUpdated entities:\n${results.updated.map((u: any) => `- ${u.name}`).join('\n')}`;
        alert(message);
      } else {
        throw new Error('Failed to search for photos');
      }
    } catch (error) {
      console.error('Photo search error:', error);
      alert('Failed to search for photos. Check console for details.');
    } finally {
      setIsSearchingPhotos(false);
    }
  };

  // Apply force-directed layout
  const handleApplyLayout = useCallback(async () => {
    if (nodes.length === 0) return;

    const layoutedNodes = await applyLayout(nodes, edges, {
      strength: -300,
      distance: 150,
      iterations: 300,
    });

    setNodes(layoutedNodes);

    // Fit view after layout
    setTimeout(() => {
      fitView({ padding: 0.2, duration: 800 });
      saveCanvas();
    }, 500);
  }, [nodes, edges, applyLayout, setNodes, fitView, saveCanvas]);

  // Handle canvas actions from chat
  useEffect(() => {
    const handleCanvasAction = (event: CustomEvent) => {
      const action = event.detail;

      switch (action.type) {
        case 'add_node':
          if (action.data) {
            const newNode = {
              id: `${action.data.type}-${Date.now()}-${Math.random()}`,
              type: action.data.type,
              position: {
                x: Math.random() * 400 + 200,
                y: Math.random() * 400 + 200,
              },
              data: action.data,
            };
            addNode(newNode);
          }
          break;

        case 'remove_node':
          if (action.node_id) {
            deleteNode(action.node_id);
          }
          break;

        case 'highlight_nodes':
          if (action.node_ids) {
            highlightNodes(action.node_ids);
          }
          break;

        case 'create_edge':
          if (action.source && action.target) {
            const newEdge = {
              id: `edge-${Date.now()}-${Math.random()}`,
              source: action.source,
              target: action.target,
              type: 'default',
              data: { label: action.label },
            };
            addEdgeToStore(newEdge);
          }
          break;

        case 'regenerate_layout':
          handleApplyLayout();
          break;

        default:
          console.warn('Unknown canvas action:', action.type);
      }
    };

    window.addEventListener('canvas-action', handleCanvasAction as EventListener);

    return () => {
      window.removeEventListener('canvas-action', handleCanvasAction as EventListener);
    };
  }, [addNode, deleteNode, highlightNodes, addEdgeToStore, handleApplyLayout]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-200px)]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading canvas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Investigation Canvas</h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Visualize connections between entities, documents, and insights
              </p>
            </div>
            {/* AI Provider Selector */}
            <AIProviderSelector />
          </div>
        </div>

        {/* Chat Toggle */}
        <button
          onClick={() => setIsChatOpen(!isChatOpen)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg shadow-lg transition-all duration-200 hover:scale-105 ${
            isChatOpen
              ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
              : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
          }`}
        >
          <MessageSquare className="w-5 h-5" />
          {isChatOpen ? 'Hide Chat' : 'Show Chat'}
          {isChatOpen ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Split View: Canvas + Chat */}
      <div className="flex gap-4 h-[calc(100vh-280px)]">
        {/* Canvas Container */}
        <div
          className={`bg-white dark:bg-gray-900 rounded-xl border-2 border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden transition-all duration-300 ${
            isChatOpen ? 'w-[70%]' : 'w-full'
          }`}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-right"
          >
            <Background
              variant={BackgroundVariant.Dots}
              gap={20}
              size={1}
              className="bg-gray-50 dark:bg-gray-800"
            />
            <Controls className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg" />
            <MiniMap
              className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg"
              nodeColor={(node) => {
                // Original types
                if (node.type === 'document') return '#3b82f6';
                if (node.type === 'insight') return '#eab308';
                if (node.type === 'note') return '#22c55e';
                // Entity types
                if (node.type === 'person') return '#a855f7';
                if (node.type === 'organization') return '#f97316';
                if (node.type === 'location') return '#10b981';
                if (node.type === 'date') return '#ec4899';
                if (node.type === 'event') return '#eab308';
                if (node.type === 'vehicle') return '#ef4444';
                if (node.type === 'financial') return '#059669';
                if (node.type === 'phone') return '#06b6d4';
                if (node.type === 'email') return '#6366f1';
                if (node.type === 'address') return '#8b5cf6';
                return '#6b7280';
              }}
            />

            {/* Toolbar Panel */}
            <Panel position="top-left" className="space-y-2">
            {/* Layout Selector */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2">
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Layout Type</label>
              <select
                value={selectedLayout}
                onChange={(e) => setSelectedLayout(e.target.value as any)}
                className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="hierarchical">Hierarchical (Flow)</option>
                <option value="force_directed">Force Directed (Organic)</option>
                <option value="circular">Circular (Ring)</option>
              </select>
            </div>

            {/* Add Node Menu */}
            <div className="relative">
              <button
                onClick={() => setShowAddMenu(!showAddMenu)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg shadow-lg transition-all duration-200 hover:scale-105"
              >
                <Plus className="w-5 h-5" />
                Add Node
              </button>

              {showAddMenu && (
                <div className="absolute top-full mt-2 left-0 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden z-10">
                  <button
                    onClick={() => handleAddNode('document')}
                    className="flex items-center gap-3 w-full px-4 py-3 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors text-left"
                  >
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded">
                      <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Document</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Link to a document</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleAddNode('insight')}
                    className="flex items-center gap-3 w-full px-4 py-3 hover:bg-yellow-50 dark:hover:bg-yellow-900/30 transition-colors text-left"
                  >
                    <div className="p-2 bg-yellow-100 dark:bg-yellow-900/50 rounded">
                      <Lightbulb className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Insight</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Key finding or theory</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleAddNode('note')}
                    className="flex items-center gap-3 w-full px-4 py-3 hover:bg-green-50 dark:hover:bg-green-900/30 transition-colors text-left"
                  >
                    <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded">
                      <StickyNote className="w-5 h-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Note</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Quick annotation</div>
                    </div>
                  </button>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col gap-2">
              {/* Auto-generate */}
              <button
                onClick={handleAutoGenerate}
                disabled={isGenerating}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-purple-400 disabled:to-pink-400 text-white rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
              >
                <Sparkles className="w-5 h-5" />
                {isGenerating ? `Generating... ${generationProgress}%` : 'Auto-Generate'}
              </button>

              {/* Find All Photos */}
              <button
                onClick={handleFindAllPhotos}
                disabled={isSearchingPhotos || nodes.length === 0}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 disabled:from-cyan-400 disabled:to-blue-400 text-white rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
              >
                <Image className="w-5 h-5" />
                {isSearchingPhotos ? 'Searching...' : 'Find All Photos'}
              </button>

              {/* Force Layout */}
              <button
                onClick={handleApplyLayout}
                disabled={nodes.length === 0}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
              >
                <Network className="w-5 h-5" />
                Re-layout
              </button>

              <div className="h-px bg-gray-300 dark:bg-gray-600 my-1"></div>

              {/* Save */}
              <button
                onClick={saveCanvas}
                disabled={isSaving}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
              >
                <Save className="w-5 h-5" />
                {isSaving ? 'Saving...' : 'Save'}
              </button>

              {/* Clear */}
              <button
                onClick={handleClearCanvas}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg shadow-lg transition-all duration-200 hover:scale-105"
              >
                <Trash2 className="w-5 h-5" />
                Clear
              </button>
            </div>
          </Panel>
        </ReactFlow>
        </div>

        {/* Chat Panel - Collapsible */}
        {isChatOpen && (
          <div className="w-[30%] bg-white dark:bg-gray-900 rounded-xl border-2 border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden transition-all duration-300">
            <CanvasChatPanel />
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">How to use the canvas:</h3>
        <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Auto-Generate:</strong> Click "Auto-Generate" to create a knowledge graph from Epstein documents</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Re-layout:</strong> Apply force-directed layout to organize nodes organically</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Add nodes:</strong> Click "Add Node" to manually create nodes</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Connect nodes:</strong> Drag from a connection point (circle) on one node to another</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Chat panel:</strong> Click "Show Chat" to open the AI assistant for canvas manipulation</span>
          </li>
        </ul>
      </div>

      {/* Entity Detail Panel - Shows when clicking entities */}
      {selectedEntity && (
        <EntityDetailPanel
          entity={selectedEntity}
          onClose={() => setSelectedEntity(null)}
        />
      )}
    </div>
  );
};

// Wrapper component to provide ReactFlow context
export const CanvasPage = () => {
  return (
    <ReactFlowProvider>
      <CanvasPageInner />
    </ReactFlowProvider>
  );
};
