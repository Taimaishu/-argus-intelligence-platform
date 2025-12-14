/**
 * Custom Document Node for React Flow
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { FileText, X } from 'lucide-react';
import { useCanvasStore } from '../../store/useCanvasStore';

interface DocumentNodeData {
  label: string;
  content?: string;
  color?: string;
  document_id?: number;
}

export const DocumentNode = memo(({ id, data }: NodeProps<DocumentNodeData>) => {
  const deleteNode = useCanvasStore((state) => state.deleteNode);

  return (
    <div className="relative group">
      <Handle type="target" position={Position.Top} className="!bg-blue-500 !w-3 !h-3" />

      <div className={`px-4 py-3 rounded-lg shadow-lg border-2 min-w-[200px] max-w-[300px] transition-all duration-200 hover:scale-105 ${
        data.color || 'bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border-blue-300 dark:border-blue-700'
      }`}>
        {/* Delete button */}
        <button
          onClick={() => deleteNode(id)}
          className="absolute -top-2 -right-2 p-1 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <X className="w-3 h-3" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 bg-blue-500 dark:bg-blue-600 rounded">
            <FileText className="w-4 h-4 text-white" />
          </div>
          <span className="text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wide">
            Document
          </span>
        </div>

        {/* Title */}
        <div className="font-semibold text-gray-900 dark:text-white mb-1 break-words">
          {data.label}
        </div>

        {/* Content preview */}
        {data.content && (
          <div className="text-xs text-gray-600 dark:text-gray-400 line-clamp-3 mt-2">
            {data.content}
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-blue-500 !w-3 !h-3" />
    </div>
  );
});

DocumentNode.displayName = 'DocumentNode';
