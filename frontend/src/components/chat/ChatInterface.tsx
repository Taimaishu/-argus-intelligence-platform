/**
 * Chat interface component
 */

import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Send, Loader2, Bot, User, Plus, Trash2, Volume2, VolumeX, Pause, Mic, MicOff } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { ModelSelector } from './ModelSelector';
import { useSpeech } from '../../hooks/useSpeech';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { BrowserCompatibilityAlert } from './BrowserCompatibilityAlert';

export const ChatInterface = () => {
  const [inputValue, setInputValue] = useState('');
  const [speakingMessageId, setSpeakingMessageId] = useState<number | null>(null);
  const {
    sessions,
    currentSession,
    streaming,
    error,
    provider,
    model,
    fetchSessions,
    createSession,
    selectSession,
    deleteSession,
    sendMessage,
    setProvider,
    setModel
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Text-to-Speech hook
  const { speak, stop, isSpeaking, isPaused, pause, resume, supported: ttsSupported } = useSpeech();

  // Speech-to-Text hook
  const {
    transcript,
    isListening,
    startListening,
    stopListening,
    resetTranscript,
    supported: sttSupported,
    error: sttError
  } = useSpeechRecognition({ continuous: false, interimResults: true });

  // Hide STT errors after 10 seconds to avoid clutter
  useEffect(() => {
    if (sttError) {
      const timer = setTimeout(() => {
        // Error will naturally be cleared by the hook
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [sttError]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages]);

  // Update input with speech transcript
  useEffect(() => {
    if (transcript) {
      setInputValue(transcript);
    }
  }, [transcript]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !streaming) {
      await sendMessage(inputValue.trim());
      setInputValue('');
      resetTranscript();
    }
  };

  const handleSpeakMessage = (messageId: number, text: string) => {
    if (speakingMessageId === messageId && isSpeaking) {
      // Stop if already speaking this message
      stop();
      setSpeakingMessageId(null);
    } else {
      // Start speaking this message
      stop(); // Stop any current speech
      speak(text);
      setSpeakingMessageId(messageId);
    }
  };

  const handlePauseSpeech = () => {
    if (isPaused) {
      resume();
    } else {
      pause();
    }
  };

  const handleMicrophoneToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      setInputValue('');
      startListening();
    }
  };

  const handleNewChat = async () => {
    await createSession('New Chat');
  };

  const handleDeleteSession = async (sessionId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this chat session?')) {
      await deleteSession(sessionId);
    }
  };

  return (
    <div className="flex h-[calc(100vh-12rem)] gap-6">
      {/* Sidebar - Session list */}
      <div className="w-72 bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-5 overflow-y-auto shadow-lg backdrop-blur-sm">
        <button
          onClick={handleNewChat}
          className="w-full mb-6 px-5 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 dark:hover:from-blue-600 dark:hover:to-indigo-600 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 font-medium"
        >
          <Plus className="w-5 h-5" />
          New Chat
        </button>

        <div className="space-y-3">
          {sessions.map(session => (
            <div
              key={session.id}
              onClick={() => selectSession(session.id)}
              className={`
                p-4 rounded-xl cursor-pointer flex items-center justify-between group transition-all duration-300
                ${currentSession?.id === session.id
                  ? 'bg-blue-600 dark:bg-blue-700 border-2 border-blue-500 dark:border-blue-600 shadow-lg'
                  : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750 border-2 border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md'
                }
              `}
            >
              <span className={`text-sm font-semibold truncate flex-1 ${
                currentSession?.id === session.id
                  ? 'text-white'
                  : 'text-gray-900 dark:text-gray-100'
              }`}>
                {session.title}
              </span>
              <button
                onClick={(e) => handleDeleteSession(session.id, e)}
                className={`opacity-0 group-hover:opacity-100 p-1.5 rounded-lg transition-all ${
                  currentSession?.id === session.id
                    ? 'hover:bg-blue-700 dark:hover:bg-blue-800'
                    : 'hover:bg-red-50 dark:hover:bg-red-900/30'
                }`}
              >
                <Trash2 className={`w-4 h-4 ${
                  currentSession?.id === session.id
                    ? 'text-white'
                    : 'text-red-600 dark:text-red-400'
                }`} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg backdrop-blur-sm">
        {/* Model Selector */}
        <ModelSelector
          provider={provider}
          model={model}
          onProviderChange={setProvider}
          onModelChange={setModel}
        />

        {!currentSession ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center p-8 bg-white/50 dark:bg-gray-800/50 rounded-2xl shadow-lg backdrop-blur-sm border border-gray-200 dark:border-gray-700">
              <Bot className="w-20 h-20 mx-auto mb-6 text-blue-600 dark:text-blue-400" />
              <p className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Select or create a chat to start</p>
              <p className="text-base text-gray-700 dark:text-gray-300">Brainstorm theories and explore connections</p>
            </div>
          </div>
        ) : (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {/* Browser compatibility alert */}
              <BrowserCompatibilityAlert />
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-400">
                  {error}
                </div>
              )}

              {currentSession.messages.length === 0 && (
                <div className="text-center py-12">
                  <div className="inline-block p-8 bg-white/50 dark:bg-gray-800/50 rounded-2xl shadow-lg backdrop-blur-sm border border-gray-200 dark:border-gray-700">
                    <Bot className="w-20 h-20 mx-auto mb-6 text-blue-600 dark:text-blue-400" />
                    <p className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Start a conversation</p>
                    <p className="text-base text-gray-700 dark:text-gray-300">Ask about your documents, brainstorm theories, or explore connections</p>
                  </div>
                </div>
              )}

              {currentSession.messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-500`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/40 dark:to-indigo-900/40 flex items-center justify-center flex-shrink-0 shadow-lg">
                      <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  )}

                  <div className="flex flex-col gap-2 max-w-[70%]">
                    <div
                      className={`
                        px-5 py-3 rounded-2xl shadow-lg
                        ${message.role === 'user'
                          ? 'bg-gradient-to-br from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 text-white'
                          : 'bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-800 dark:to-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
                        }
                      `}
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    </div>

                    {/* Audio controls for assistant messages */}
                    {message.role === 'assistant' && ttsSupported && (
                      <div className="flex gap-2 ml-2">
                        <button
                          onClick={() => handleSpeakMessage(message.id, message.content)}
                          className={`
                            p-2 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md
                            ${speakingMessageId === message.id && isSpeaking
                              ? 'bg-red-100 dark:bg-red-900/30 hover:bg-red-200 dark:hover:bg-red-900/50 text-red-600 dark:text-red-400'
                              : 'bg-blue-100 dark:bg-blue-900/30 hover:bg-blue-200 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-400'
                            }
                          `}
                          title={speakingMessageId === message.id && isSpeaking ? "Stop reading" : "Read aloud"}
                        >
                          {speakingMessageId === message.id && isSpeaking ? (
                            <VolumeX className="w-4 h-4" />
                          ) : (
                            <Volume2 className="w-4 h-4" />
                          )}
                        </button>

                        {speakingMessageId === message.id && isSpeaking && (
                          <button
                            onClick={handlePauseSpeech}
                            className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 hover:bg-yellow-200 dark:hover:bg-yellow-900/50 text-yellow-600 dark:text-yellow-400 transition-all duration-200 shadow-sm hover:shadow-md"
                            title={isPaused ? "Resume" : "Pause"}
                          >
                            <Pause className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                      <User className="w-6 h-6 text-gray-700 dark:text-gray-300" />
                    </div>
                  )}
                </div>
              ))}

              {streaming && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="bg-gray-100 dark:bg-gray-800 px-4 py-3 rounded-lg">
                    <Loader2 className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input form */}
            <div className="border-t-2 border-gray-200 dark:border-gray-700 p-6 bg-gradient-to-r from-gray-50/80 to-blue-50/30 dark:from-gray-800/80 dark:to-blue-900/10 backdrop-blur-sm">
              {sttError && (
                <div className="mb-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
                  {sttError}
                </div>
              )}

              <form onSubmit={handleSubmit} className="flex gap-3">
                {/* Microphone button - only show if supported and no persistent network error */}
                {sttSupported && sttError !== 'Network blocked. Brave users: Disable Shields or use text input instead.' && (
                  <button
                    type="button"
                    onClick={handleMicrophoneToggle}
                    disabled={streaming}
                    className={`
                      px-4 py-3 rounded-xl flex items-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105
                      ${isListening
                        ? 'bg-gradient-to-r from-red-500 to-red-600 dark:from-red-600 dark:to-red-700 text-white animate-pulse'
                        : 'bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 text-gray-700 dark:text-gray-300 hover:from-gray-300 hover:to-gray-400 dark:hover:from-gray-600 dark:hover:to-gray-500'
                      }
                      disabled:from-gray-300 disabled:to-gray-400 dark:disabled:from-gray-700 dark:disabled:to-gray-800 disabled:cursor-not-allowed
                    `}
                    title={isListening ? "Stop recording" : "Voice input"}
                  >
                    {isListening ? (
                      <MicOff className="w-5 h-5" />
                    ) : (
                      <Mic className="w-5 h-5" />
                    )}
                  </button>
                )}

                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={isListening ? "Listening... speak now" : "Ask about your documents, theories, or connections..."}
                  className="flex-1 px-5 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-4 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 focus:border-blue-500 dark:focus:border-blue-400 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm text-gray-900 dark:text-white shadow-lg transition-all duration-300"
                  disabled={streaming || isListening}
                />
                <button
                  type="submit"
                  disabled={streaming || !inputValue.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 dark:hover:from-blue-600 dark:hover:to-indigo-600 disabled:from-gray-300 disabled:to-gray-400 dark:disabled:from-gray-700 dark:disabled:to-gray-800 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                >
                  {streaming ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
