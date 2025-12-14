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
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Plus, FileText, Lightbulb, StickyNote, Save, Trash2 } from 'lucide-react';

import { useCanvasStore } from '../store/useCanvasStore';
import { DocumentNode } from '../components/canvas/DocumentNode';
import { InsightNode } from '../components/canvas/InsightNode';
import { NoteNode } from '../components/canvas/NoteNode';

// Define custom node types
const nodeTypes = {
  document: DocumentNode,
  insight: InsightNode,
  note: NoteNode,
};

export const CanvasPage = () => {
  const {
    nodes,
    edges,
    isLoading,
    isSaving,
    onNodesChange,
    onEdgesChange,
    addNode,
    addEdge: addEdgeToStore,
    loadCanvas,
    saveCanvas,
    clearCanvas,
  } = useCanvasStore();

  const [showAddMenu, setShowAddMenu] = useState(false);

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
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Investigation Canvas</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Visualize connections between documents, insights, and notes
        </p>
      </div>

      {/* Canvas */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border-2 border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden h-[calc(100vh-280px)]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
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
              if (node.type === 'document') return '#3b82f6';
              if (node.type === 'insight') return '#eab308';
              if (node.type === 'note') return '#22c55e';
              return '#6b7280';
            }}
          />

          {/* Toolbar Panel */}
          <Panel position="top-left" className="space-y-2">
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
            <div className="flex gap-2">
              <button
                onClick={saveCanvas}
                disabled={isSaving}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
              >
                <Save className="w-5 h-5" />
                {isSaving ? 'Saving...' : 'Save'}
              </button>

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

      {/* Instructions */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">How to use the canvas:</h3>
        <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Add nodes:</strong> Click "Add Node" to create document, insight, or note nodes</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Connect nodes:</strong> Drag from a connection point (circle) on one node to another</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Move nodes:</strong> Drag nodes to reposition them on the canvas</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Delete:</strong> Hover over a node to reveal the delete button</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 dark:text-blue-400">•</span>
            <span><strong>Auto-save:</strong> Changes are automatically saved after 2 seconds</span>
          </li>
        </ul>
      </div>
    </div>
  );
};
