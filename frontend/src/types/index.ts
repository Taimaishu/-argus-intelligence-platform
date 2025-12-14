/**
 * Type definitions for the Research Tool frontend
 */

export type DocumentType = 'pdf' | 'docx' | 'xlsx' | 'pptx' | 'markdown' | 'code' | 'text';

export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Document {
  id: number;
  filename: string;
  file_type: DocumentType;
  file_size: number;
  title?: string;
  author?: string;
  processing_status: ProcessingStatus;
  error_message?: string;
  upload_date: string;
  processed_date?: string;
}

export interface SearchResultItem {
  document_id: number;
  document_title: string;
  document_filename: string;
  chunk_text: string;
  snippet: string;
  relevance_score: number;
  chunk_index: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
  total_results: number;
  embedding_model: string;
}

export interface UploadResponse {
  message: string;
  document: Document;
}
