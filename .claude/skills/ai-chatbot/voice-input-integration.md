# Voice Input Integration Skill

## Purpose
Integrate Web Speech API for voice input in the AI Todo Chatbot with support for English and Urdu.

## Context7 Reference
- Web Speech API (browser native)
- Query: "SpeechRecognition API usage"

## Implementation Pattern

### 1. Voice Input Hook
```typescript
// frontend/hooks/useVoiceInput.ts
import { useState, useEffect, useCallback, useRef } from 'react';

type Language = 'en-US' | 'ur-PK';

interface UseVoiceInputReturn {
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  error: string | null;
  isSupported: boolean;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
  language: Language;
  setLanguage: (lang: Language) => void;
}

export function useVoiceInput(): UseVoiceInputReturn {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<Language>('en-US');
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const isSupported = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();

    const recognition = recognitionRef.current;
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      if (final) {
        setTranscript(prev => prev + final);
      }
      setInterimTranscript(interim);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      setError(event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimTranscript('');
    };

    return () => {
      recognition.abort();
    };
  }, [isSupported, language]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return;

    setTranscript('');
    setInterimTranscript('');
    recognitionRef.current.lang = language;
    recognitionRef.current.start();
  }, [isListening, language]);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) return;
    recognitionRef.current.stop();
  }, [isListening]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
  }, []);

  return {
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
    language,
    setLanguage,
  };
}
```

### 2. Voice Input Button Component
```tsx
// frontend/app/(protected)/chat/components/VoiceInputButton.tsx
import { Mic, MicOff, Globe } from 'lucide-react';
import { useVoiceInput } from '@/hooks/useVoiceInput';

interface VoiceInputButtonProps {
  onTranscript: (text: string) => void;
}

export function VoiceInputButton({ onTranscript }: VoiceInputButtonProps) {
  const {
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    startListening,
    stopListening,
    language,
    setLanguage,
  } = useVoiceInput();

  // Send transcript when recording stops
  useEffect(() => {
    if (!isListening && transcript) {
      onTranscript(transcript);
    }
  }, [isListening, transcript, onTranscript]);

  if (!isSupported) {
    return null; // Hide if not supported
  }

  return (
    <div className="flex items-center gap-2">
      {/* Language Toggle */}
      <button
        onClick={() => setLanguage(language === 'en-US' ? 'ur-PK' : 'en-US')}
        className="
          p-2 rounded-lg
          bg-white/5 hover:bg-white/10
          text-white/70 hover:text-white
          transition-colors
          text-xs font-medium
        "
        title={`Switch to ${language === 'en-US' ? 'Urdu' : 'English'}`}
      >
        {language === 'en-US' ? '🇬🇧' : '🇰'}
      </button>

      {/* Mic Button */}
      <button
        onClick={isListening ? stopListening : startListening}
        className={`
          p-2 rounded-lg
          transition-all duration-200
          ${isListening
            ? 'bg-red-500/20 text-red-400 animate-pulse'
            : 'bg-white/5 hover:bg-white/10 text-white/70 hover:text-white'
          }
        `}
        title={isListening ? 'Stop recording' : 'Start voice input'}
      >
        {isListening ? (
          <MicOff className="w-5 h-5" />
        ) : (
          <Mic className="w-5 h-5" />
        )}
      </button>

      {/* Visual Feedback */}
      {isListening && (
        <div className="
          absolute bottom-full mb-2 left-0 right-0
          p-3 rounded-xl
          bg-black/80 backdrop-blur-xl
          border border-white/10
          text-sm text-white/80
        ">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-xs text-white/50">Listening...</span>
          </div>
          <p className="text-white/90">
            {interimTranscript || 'Speak now...'}
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <span className="text-xs text-red-400">{error}</span>
      )}
    </div>
  );
}
```

### 3. TypeScript Declarations
```typescript
// frontend/types/speech.d.ts
interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => void) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => void) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => void) | null;
  onend: ((this: SpeechRecognition, ev: Event) => void) | null;
}

interface Window {
  SpeechRecognition: new () => SpeechRecognition;
  webkitSpeechRecognition: new () => SpeechRecognition;
}
```

### 4. Accessibility Requirements
```tsx
// ARIA labels for voice input
<button
  aria-label={isListening ? 'Stop voice recording' : 'Start voice recording'}
  aria-pressed={isListening}
  role="switch"
>
  {/* ... */}
</button>

// Screen reader announcement
{isListening && (
  <span className="sr-only" role="status" aria-live="polite">
    Recording voice input. Speak now.
  </span>
)}
```

## Key Principles
- **Progressive Enhancement**: Hide if not supported
- **Visual Feedback**: Show recording state clearly
- **Language Toggle**: Easy switch between English/Urdu
- **Accessibility**: ARIA labels and screen reader support
- **Error Handling**: Display errors gracefully
