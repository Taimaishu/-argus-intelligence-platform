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

  // Load available voices
  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);

      // Try to select a good default voice (prefer English)
      if (availableVoices.length > 0 && !selectedVoice) {
        const englishVoice = availableVoices.find(v => v.lang.startsWith('en'));
        setSelectedVoice(englishVoice || availableVoices[0]);
      }
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, [selectedVoice]);

  const speakAlways = useCallback((text: string) => {
    if (!text) return;

    // Check if speech synthesis is supported
    if (!window.speechSynthesis) {
      console.error('Speech synthesis not supported in this browser');
      alert('Text-to-speech is not supported in your browser. Please use Chrome, Edge, Safari, or Firefox.');
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    // Small delay to ensure cancellation is processed
    setTimeout(() => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = rate;
      utterance.pitch = pitch;
      utterance.volume = volume;
      utterance.lang = 'en-US';

      // Get voices and select one if available
      const availableVoices = window.speechSynthesis.getVoices();
      if (availableVoices.length > 0) {
        const voice = selectedVoice || availableVoices.find(v => v.lang.startsWith('en')) || availableVoices[0];
        utterance.voice = voice;
      }

      utterance.onstart = () => {
        console.log('Speech started');
        setIsSpeaking(true);
      };

      utterance.onend = () => {
        console.log('Speech ended');
        setIsSpeaking(false);
      };

      utterance.onerror = (e) => {
        console.error('Speech synthesis error:', e);
        alert(`Speech error: ${e.error}. Try clicking the button again.`);
        setIsSpeaking(false);
      };

      console.log('Starting speech synthesis...', {
        text: text.substring(0, 50) + '...',
        voice: utterance.voice?.name,
        rate,
        pitch,
        volume
      });

      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    }, 100);
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
