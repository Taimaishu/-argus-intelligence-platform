/**
 * Documents page
 */

import { DocumentUpload } from '../components/documents/DocumentUpload';
import { DocumentList } from '../components/documents/DocumentList';

export const DocumentsPage = () => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Intelligence Documents</h2>
        <p className="text-gray-600 dark:text-gray-400">
          Upload and analyze documents with AI-powered processing
        </p>
      </div>

      <DocumentUpload />

      <div className="pt-8">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Document Library</h3>
        <DocumentList />
      </div>
    </div>
  );
};
