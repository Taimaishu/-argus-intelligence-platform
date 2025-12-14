/**
 * Text-to-Speech hook using Backend TTS API (gTTS)
 * Works reliably on all platforms including Linux
 */

import { useState, useCallback, useRef } from 'react';
import { getApiUrl } from '../config/api';

interface UseTTSOptions {
  autoSpeak?: boolean;
  lang?: string;
}

const API_URL = getApiUrl('/api');

export const useTTS = (options: UseTTSOptions = {}) => {
  const {
    autoSpeak = false,
    lang = 'en',
  } = options;

  const [isEnabled, setIsEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [speed, setSpeed] = useState(1.25); // Default to 1.25x speed
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const speakAlways = useCallback(async (text: string) => {
    if (!text) {
      console.warn('No text provided to speak');
      return;
    }

    if (text.length > 5000) {
      alert('Text too long for TTS (max 5000 characters)');
      return;
    }

    try {
      console.log('🎤 Requesting TTS from backend...', {
        textLength: text.length,
        textPreview: text.substring(0, 50) + '...',
        speed: speed
      });

      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      setIsSpeaking(true);
      setIsPaused(false);

      // Call backend TTS API
      const response = await fetch(`${API_URL}/tts/speak`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          lang,
          speed
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'TTS request failed');
      }

      // Get audio blob
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      console.log('✓ TTS audio received, playing...');

      // Create and play audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onplay = () => {
        console.log('✓ Audio playback started');
        setIsSpeaking(true);
      };

      audio.onended = () => {
        console.log('✓ Audio playback ended');
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = (e) => {
        console.error('✗ Audio playback error:', e);
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
        alert('Failed to play audio. Check your browser audio settings.');
      };

      await audio.play();

    } catch (error) {
      console.error('✗ TTS error:', error);
      setIsSpeaking(false);
      alert(`TTS failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [lang, speed]);

  const speak = useCallback(async (text: string) => {
    if (!isEnabled) return;
    await speakAlways(text);
  }, [isEnabled, speakAlways]);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    setIsSpeaking(false);
    setIsPaused(false);
  }, []);

  const pause = useCallback(() => {
    if (audioRef.current && !audioRef.current.paused) {
      audioRef.current.pause();
      setIsSpeaking(false);
      setIsPaused(true);
    }
  }, []);

  const resume = useCallback(() => {
    if (audioRef.current && audioRef.current.paused) {
      audioRef.current.play();
      setIsSpeaking(true);
      setIsPaused(false);
    }
  }, []);

  const toggle = useCallback(() => {
    setIsEnabled(prev => !prev);
    if (isSpeaking) {
      stop();
    }
  }, [isSpeaking, stop]);

  return {
    isEnabled,
    isSpeaking,
    isPaused,
    speed,
    setSpeed,
    voices: [], // Not used with backend TTS
    selectedVoice: null, // Not used with backend TTS
    setSelectedVoice: () => {}, // Not used with backend TTS
    setIsEnabled,
    speak,
    speakAlways,
    stop,
    pause,
    resume,
    toggle,
  };
};
