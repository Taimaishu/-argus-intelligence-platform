import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { MapPin, X } from 'lucide-react';
import { useCanvasStore } from '../../store/useCanvasStore';

interface LocationNodeData {
  label: string;
  confidence?: number;
  mention_count?: number;
  image_url?: string;
}

export const LocationNode = memo(({ id, data }: NodeProps<LocationNodeData>) => {
  const deleteNode = useCanvasStore((state) => state.deleteNode);

  return (
    <div className="relative group">
      <Handle type="target" position={Position.Top} className="!bg-green-500 !w-3 !h-3" />
      <div className="px-4 py-3 rounded-lg shadow-lg border-2 min-w-[200px] max-w-[300px] transition-all duration-200 hover:scale-105 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 border-green-300 dark:border-green-700">
        <button onClick={() => deleteNode(id)} className="absolute -top-2 -right-2 p-1 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity">
          <X className="w-3 h-3" />
        </button>

        {/* Image (if available) */}
        {data.image_url && (
          <div className="mb-3 -mx-4 -mt-3">
            <img
              src={data.image_url}
              alt={data.label}
              className="w-full h-32 object-cover rounded-t-lg"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
              }}
            />
          </div>
        )}

        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 bg-green-500 dark:bg-green-600 rounded">
            <MapPin className="w-4 h-4 text-white" />
          </div>
          <span className="text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wide">Location</span>
        </div>
        <div className="font-semibold text-gray-900 dark:text-white mb-1 break-words">{data.label}</div>
        {(data.confidence || data.mention_count) && (
          <div className="text-xs text-gray-600 dark:text-gray-400 mt-2 space-y-0.5">
            {data.confidence && <div>Confidence: {Math.round(data.confidence * 100)}%</div>}
            {data.mention_count && <div>Mentions: {data.mention_count}</div>}
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-green-500 !w-3 !h-3" />
    </div>
  );
});

LocationNode.displayName = 'LocationNode';
