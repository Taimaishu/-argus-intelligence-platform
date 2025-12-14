/**
 * Document list component
 */

import { useEffect } from 'react';
import { FileText, Trash2, Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';
import { useDocumentStore } from '../../store/useDocumentStore';
import type { Document, ProcessingStatus } from '../../types';

const StatusIcon = ({ status }: { status: ProcessingStatus }) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case 'processing':
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    case 'failed':
      return <XCircle className="w-5 h-5 text-red-500" />;
    default:
      return <Clock className="w-5 h-5 text-gray-400" />;
  }
};

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

export const DocumentList = () => {
  const { documents, loading, error, fetchDocuments, deleteDocument } = useDocumentStore();

  useEffect(() => {
    fetchDocuments();
  }, []); // Only fetch on mount

  useEffect(() => {
    // Auto-refresh for processing documents
    const hasProcessing = documents.some(doc => doc.processing_status === 'processing');

    if (!hasProcessing) return;

    const interval = setInterval(() => {
      fetchDocuments();
    }, 3000);

    return () => clearInterval(interval);
  }, [documents, fetchDocuments]); // Separate effect for auto-refresh

  const handleDelete = async (id: number, filename: string) => {
    if (confirm(`Delete "${filename}"?`)) {
      try {
        await deleteDocument(id);
      } catch (error) {
        console.error('Failed to delete:', error);
      }
    }
  };

  if (loading && documents.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="w-8 h-8 text-blue-600 dark:text-blue-400 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-400">
        Error: {error}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
        <p className="text-lg">No documents yet</p>
        <p className="text-sm">Upload your first document to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {documents.map((doc: Document) => (
        <div
          key={doc.id}
          className="group bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-5 shadow-lg hover:shadow-2xl dark:shadow-gray-900/50 transition-all duration-300 transform hover:scale-[1.01] backdrop-blur-sm"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4 flex-1">
              <div className="p-3 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-lg group-hover:scale-110 transition-transform duration-300">
                <FileText className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>

              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {doc.title || doc.filename}
                </h3>

                {doc.title && doc.title !== doc.filename && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">{doc.filename}</p>
                )}

                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                  <span>{formatFileSize(doc.file_size)}</span>
                  <span>•</span>
                  <span className="uppercase">{doc.file_type}</span>
                  <span>•</span>
                  <span>{formatDate(doc.upload_date)}</span>
                </div>

                {doc.error_message && (
                  <div className="mt-2 text-sm text-red-600 dark:text-red-400">
                    Error: {doc.error_message}
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <StatusIcon status={doc.processing_status} />
                <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                  {doc.processing_status}
                </span>
              </div>

              <button
                onClick={() => handleDelete(doc.id, doc.filename)}
                className="p-2 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                title="Delete document"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
