import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { Phone, X } from 'lucide-react';
import { useCanvasStore } from '../../store/useCanvasStore';

export const PhoneNode = memo(({ id, data }: NodeProps<any>) => {
  const deleteNode = useCanvasStore((state) => state.deleteNode);
  return (
    <div className="relative group">
      <Handle type="target" position={Position.Top} className="!bg-cyan-500 !w-3 !h-3" />
      <div className="px-4 py-3 rounded-lg shadow-lg border-2 min-w-[180px] max-w-[280px] transition-all hover:scale-105 bg-gradient-to-br from-cyan-50 to-sky-50 dark:from-cyan-900/30 dark:to-sky-900/30 border-cyan-300 dark:border-cyan-700">
        <button onClick={() => deleteNode(id)} className="absolute -top-2 -right-2 p-1 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity"><X className="w-3 h-3" /></button>

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

        <div className="flex items-center gap-2 mb-2"><div className="p-1.5 bg-cyan-500 rounded"><Phone className="w-4 h-4 text-white" /></div><span className="text-xs font-semibold text-cyan-600 dark:text-cyan-400 uppercase">Phone</span></div>
        <div className="font-semibold text-gray-900 dark:text-white break-words">{data.label}</div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-cyan-500 !w-3 !h-3" />
    </div>
  );
});
PhoneNode.displayName = 'PhoneNode';
