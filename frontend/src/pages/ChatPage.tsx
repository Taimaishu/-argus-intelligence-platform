/**
 * Chat page
 */

import { ChatInterface } from '../components/chat/ChatInterface';
import { AIProviderSelector } from '../components/common/AIProviderSelector';

export const ChatPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Intelligence Assistant</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            AI-powered analyst for brainstorming theories, exploring connections, and deep investigation
          </p>
        </div>
        <AIProviderSelector />
      </div>
      <ChatInterface />
    </div>
  );
};
