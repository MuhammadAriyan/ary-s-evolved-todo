'use client'

import { Mic, MicOff, Loader2 } from 'lucide-react'
import { useVoiceInput, type VoiceLanguage } from '@/hooks/useVoiceInput'
import { cn } from '@/lib/utils'

interface VoiceInputButtonProps {
  onTranscript: (transcript: string, language: VoiceLanguage) => void
  className?: string
}

export function VoiceInputButton({ onTranscript, className }: VoiceInputButtonProps) {
  const {
    isListening,
    isSupported,
    transcript,
    error,
    language,
    backend,
    isModelLoading,
    modelLoadProgress,
    startListening,
    stopListening,
    toggleLanguage,
    clearError,
  } = useVoiceInput(onTranscript)

  if (!isSupported) {
    return null // Hide button on unsupported browsers
  }

  const isProcessing = isModelLoading || transcript === 'Transcribing...'

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {/* Language toggle */}
      <button
        type="button"
        onClick={toggleLanguage}
        disabled={isListening || isProcessing}
        className={cn(
          'p-2 rounded-full transition-all duration-200',
          'bg-white/5 hover:bg-white/10 border border-white/10',
          'text-white/70 hover:text-white',
          'disabled:opacity-50 disabled:cursor-not-allowed'
        )}
        title={`Switch to ${language === 'en-US' ? 'Urdu' : 'English'}`}
      >
        <span className="text-sm font-medium">
          {language === 'en-US' ? '🇬🇧' : '🇵🇰'}
        </span>
      </button>

      {/* Voice input button */}
      <button
        type="button"
        onClick={isListening ? stopListening : startListening}
        disabled={isProcessing}
        className={cn(
          'p-3 rounded-full transition-all duration-200',
          'border relative',
          isListening
            ? 'bg-red-500/20 border-red-500/50 text-red-400 animate-pulse'
            : isProcessing
            ? 'bg-aura-purple/20 border-aura-purple/50 text-aura-purple'
            : 'bg-white/5 hover:bg-white/10 border-white/10 text-white/70 hover:text-white',
          'disabled:cursor-wait'
        )}
        title={
          isProcessing
            ? 'Processing...'
            : isListening
            ? 'Stop listening'
            : `Start voice input${backend === 'whisper' ? ' (offline)' : ''}`
        }
      >
        {isProcessing ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : isListening ? (
          <MicOff className="w-5 h-5" />
        ) : (
          <Mic className="w-5 h-5" />
        )}
      </button>

      {/* Model loading progress */}
      {isModelLoading && (
        <div className="absolute bottom-full left-0 right-0 mb-2 p-2 rounded-lg bg-aura-purple/20 backdrop-blur-sm border border-aura-purple/30 text-sm text-white/80">
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Loading voice model... {modelLoadProgress}%</span>
          </div>
          <div className="mt-1 h-1 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-aura-purple transition-all duration-300"
              style={{ width: `${modelLoadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Transcript preview */}
      {(isListening || transcript === 'Transcribing...') && transcript && !isModelLoading && (
        <div className="absolute bottom-full left-0 right-0 mb-2 p-2 rounded-lg bg-black/50 backdrop-blur-sm border border-white/10 text-sm text-white/80">
          <div className="flex items-center gap-2">
            {transcript === 'Transcribing...' && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>{transcript}</span>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && !isModelLoading && (
        <div className="absolute bottom-full left-0 right-0 mb-2 p-2 rounded-lg bg-red-500/20 border border-red-500/30 text-sm text-red-300">
          {error}
          <button
            onClick={clearError}
            className="ml-2 text-red-400 hover:text-red-300"
          >
            ×
          </button>
        </div>
      )}
    </div>
  )
}
