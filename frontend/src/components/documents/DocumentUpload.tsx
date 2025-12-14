/**
 * Document upload component with drag-and-drop
 */

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { useDocumentStore } from '../../store/useDocumentStore';

export const DocumentUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const uploadDocument = useDocumentStore(state => state.uploadDocument);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadStatus(`Uploading ${file.name}...`);

    try {
      await uploadDocument(file);
      setUploadStatus(`✓ ${file.name} uploaded successfully! Processing...`);
      setTimeout(() => setUploadStatus(''), 3000);
    } catch (error) {
      setUploadStatus(`✗ Failed to upload ${file.name}`);
      setTimeout(() => setUploadStatus(''), 5000);
    } finally {
      setUploading(false);
    }
  }, [uploadDocument]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    disabled: uploading,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
          transition-all duration-300 transform hover:scale-[1.01]
          ${isDragActive
            ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 dark:border-blue-400 scale-[1.02]'
            : 'border-gray-300 dark:border-gray-700 bg-white/50 dark:bg-gray-900/50 hover:border-blue-400 dark:hover:border-blue-600 backdrop-blur-sm'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : 'shadow-lg hover:shadow-xl'}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center">
          {uploading ? (
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500/20 rounded-full animate-ping" />
              <Loader2 className="w-16 h-16 text-blue-600 dark:text-blue-400 animate-spin mb-4" />
            </div>
          ) : isDragActive ? (
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500/10 rounded-full animate-pulse" />
              <Upload className="w-16 h-16 text-blue-600 dark:text-blue-400 mb-4" />
            </div>
          ) : (
            <div className="p-4 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-full mb-4">
              <FileText className="w-12 h-12 text-blue-600 dark:text-blue-400" />
            </div>
          )}

          <p className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {isDragActive
              ? 'Drop file here'
              : 'Drag & drop a document here'
            }
          </p>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            or click to browse files
          </p>

          <div className="flex flex-wrap gap-2 justify-center">
            {['PDF', 'DOCX', 'XLSX', 'PPTX', 'MD', 'Code'].map(type => (
              <span key={type} className="px-3 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full">
                {type}
              </span>
            ))}
          </div>
        </div>
      </div>

      {uploadStatus && (
        <div className={`
          mt-4 p-4 rounded-xl shadow-lg animate-in fade-in slide-in-from-top-2 duration-300
          ${uploadStatus.startsWith('✓')
            ? 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 text-green-800 dark:text-green-400 border border-green-200 dark:border-green-800'
            : uploadStatus.startsWith('✗')
            ? 'bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 text-red-800 dark:text-red-400 border border-red-200 dark:border-red-800'
            : 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 text-blue-800 dark:text-blue-400 border border-blue-200 dark:border-blue-800'
          }
        `}>
          <div className="flex items-center gap-2">
            {uploadStatus.startsWith('✓') && <span className="text-2xl">✓</span>}
            {uploadStatus.startsWith('✗') && <span className="text-2xl">✗</span>}
            <span className="flex-1">{uploadStatus}</span>
          </div>
        </div>
      )}
    </div>
  );
};
