/**
 * Text-to-Speech hook using Web Speech API
 */

import { useEffect, useState, useCallback, useRef } from 'react';

interface UseTTSOptions {
  autoSpeak?: boolean;
  rate?: number;
  pitch?: number;
  volume?: number;
}

export const useTTS = (options: UseTTSOptions = {}) => {
  const {
    autoSpeak = false,
    rate = 1,
    pitch = 1,
    volume = 1,
  } = options;

  const [isEnabled, setIsEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Load available voices with retry
  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 10;

    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();

      if (availableVoices.length === 0 && retryCount < maxRetries) {
        // Voices not loaded yet, retry
        retryCount++;
        setTimeout(loadVoices, 100);
        return;
      }

      if (availableVoices.length > 0) {
        console.log(`Loaded ${availableVoices.length} voices:`, availableVoices.map(v => v.name));
        setVoices(availableVoices);

        // Try to select a good default voice (prefer English)
        if (!selectedVoice) {
          const englishVoice = availableVoices.find(v => v.lang.startsWith('en')) || availableVoices[0];
          setSelectedVoice(englishVoice);
          console.log('Selected voice:', englishVoice?.name);
        }
      } else {
        console.warn('No voices available after retries');
      }
    };

    // Try loading immediately
    loadVoices();

    // Also listen for voiceschanged event
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, [selectedVoice]);

  const speakAlways = useCallback((text: string) => {
    if (!text) {
      console.warn('No text provided to speak');
      return;
    }

    // Check if speech synthesis is supported
    if (!window.speechSynthesis) {
      console.error('Speech synthesis not supported in this browser');
      alert('Text-to-speech is not supported in your browser. Please use Chrome, Edge, Safari, or Firefox.');
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    // Use a longer delay and ensure voices are loaded
    setTimeout(() => {
      try {
        // Force reload voices
        const availableVoices = window.speechSynthesis.getVoices();
        console.log('Available voices:', availableVoices.length);

        if (availableVoices.length === 0) {
          console.error('No voices available');
          alert('No voices available. Please wait a moment and try again, or restart your browser.');
          return;
        }

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = rate;
        utterance.pitch = pitch;
        utterance.volume = volume;
        utterance.lang = 'en-US';

        // Select voice
        const voice = selectedVoice || availableVoices.find(v => v.lang.startsWith('en')) || availableVoices[0];
        if (voice) {
          utterance.voice = voice;
          console.log('Using voice:', voice.name);
        }

        utterance.onstart = () => {
          console.log('✓ Speech started successfully');
          setIsSpeaking(true);
        };

        utterance.onend = () => {
          console.log('✓ Speech ended');
          setIsSpeaking(false);
        };

        utterance.onpause = () => {
          console.log('Speech paused');
        };

        utterance.onresume = () => {
          console.log('Speech resumed');
        };

        utterance.onerror = (e) => {
          console.error('✗ Speech synthesis error:', {
            error: e.error,
            message: e.message,
            type: e.type
          });

          let errorMsg = `Speech error: ${e.error}`;
          if (e.error === 'not-allowed') {
            errorMsg += '\n\nYour browser blocked speech. Please:\n1. Check browser permissions\n2. Make sure audio is not muted\n3. Try interacting with the page first (click something)';
          } else if (e.error === 'network') {
            errorMsg += '\n\nNetwork error. Check your internet connection.';
          }

          alert(errorMsg);
          setIsSpeaking(false);
        };

        console.log('▶ Starting speech synthesis:', {
          textLength: text.length,
          textPreview: text.substring(0, 50) + '...',
          voice: utterance.voice?.name,
          rate,
          pitch,
          volume
        });

        utteranceRef.current = utterance;
        window.speechSynthesis.speak(utterance);

        // Verify it started
        setTimeout(() => {
          if (!window.speechSynthesis.speaking && !window.speechSynthesis.pending) {
            console.error('✗ Speech did not start');
            alert('Speech did not start. Your browser may have blocked it. Try clicking the button again.');
          }
        }, 500);
      } catch (error) {
        console.error('Exception in speakAlways:', error);
        alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        setIsSpeaking(false);
      }
    }, 250);
  }, [rate, pitch, volume, selectedVoice]);

  const speak = useCallback((text: string) => {
    if (!isEnabled) return;
    speakAlways(text);
  }, [isEnabled, speakAlways]);

  const stop = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  const toggle = useCallback(() => {
    setIsEnabled(prev => !prev);
    if (isSpeaking) {
      stop();
    }
  }, [isSpeaking, stop]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  return {
    isEnabled,
    isSpeaking,
    voices,
    selectedVoice,
    setSelectedVoice,
    setIsEnabled,
    speak,
    speakAlways,
    stop,
    toggle,
  };
};
