/**
 * useVoiceInput hook for voice input with fallback
 *
 * Strategy:
 * 1. Try Web Speech API first (fast, free, works in Chrome/Edge)
 * 2. Fall back to browser Whisper if Web Speech fails (works everywhere)
 */
'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import type { SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionErrorEvent } from '@/types/speech.d'

export type VoiceLanguage = 'en-US' | 'ur-PK'
type VoiceBackend = 'web-speech' | 'whisper' | 'none'

interface UseVoiceInputState {
  isListening: boolean
  isSupported: boolean
  transcript: string
  error: string | null
  language: VoiceLanguage
  backend: VoiceBackend
  isModelLoading: boolean
  modelLoadProgress: number
}

interface UseVoiceInputActions {
  startListening: () => void
  stopListening: () => void
  toggleLanguage: () => void
  setLanguage: (lang: VoiceLanguage) => void
  clearTranscript: () => void
  clearError: () => void
}

export type UseVoiceInputReturn = UseVoiceInputState & UseVoiceInputActions

// Check if Web Speech API is supported
function isSpeechRecognitionSupported(): boolean {
  if (typeof window === 'undefined') return false
  return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window
}

// Get SpeechRecognition constructor
function getSpeechRecognition(): (new () => SpeechRecognition) | null {
  if (typeof window === 'undefined') return null
  return window.SpeechRecognition || window.webkitSpeechRecognition || null
}

// Lazy load Whisper transcriber
let whisperPipelinePromise: Promise<any> | null = null
let whisperLoadFailed = false

async function getWhisperTranscriber(onProgress?: (progress: number) => void) {
  if (whisperLoadFailed) return null

  if (!whisperPipelinePromise) {
    whisperPipelinePromise = (async () => {
      try {
        const { pipeline } = await import('@huggingface/transformers')
        return pipeline('automatic-speech-recognition', 'Xenova/whisper-tiny.en', {
          progress_callback: (progress: any) => {
            if (progress.status === 'progress' && onProgress) {
              onProgress(Math.round(progress.progress))
            }
          }
        })
      } catch (err) {
        whisperLoadFailed = true
        whisperPipelinePromise = null
        throw err
      }
    })()
  }
  return whisperPipelinePromise
}

export function useVoiceInput(
  onTranscript?: (transcript: string, language: VoiceLanguage) => void
): UseVoiceInputReturn {
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [language, setLanguageState] = useState<VoiceLanguage>('en-US')
  const [backend, setBackend] = useState<VoiceBackend>('none')
  const [isModelLoading, setIsModelLoading] = useState(false)
  const [modelLoadProgress, setModelLoadProgress] = useState(0)

  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const whisperRef = useRef<any>(null)
  const useWhisperFallback = useRef(false)

  // Check support on mount
  useEffect(() => {
    const webSpeechSupported = isSpeechRecognitionSupported()
    // Always supported - we have Whisper fallback
    setIsSupported(true)
    setBackend(webSpeechSupported ? 'web-speech' : 'whisper')
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
        recognitionRef.current = null
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  // Transcribe audio with Whisper
  const transcribeWithWhisper = useCallback(async (audioBlob: Blob): Promise<string | null> => {
    try {
      if (!whisperRef.current) {
        setIsModelLoading(true)
        setModelLoadProgress(0)
        whisperRef.current = await getWhisperTranscriber((progress) => {
          setModelLoadProgress(progress)
        })
        setIsModelLoading(false)
        setModelLoadProgress(100)
      }

      if (!whisperRef.current) {
        throw new Error('Failed to load Whisper model')
      }

      // Convert blob to array buffer
      const arrayBuffer = await audioBlob.arrayBuffer()

      // Decode audio using Web Audio API
      const audioContext = new AudioContext({ sampleRate: 16000 })
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

      // Get audio data as Float32Array (mono, 16kHz)
      let audioData: Float32Array
      if (audioBuffer.numberOfChannels > 1) {
        const left = audioBuffer.getChannelData(0)
        const right = audioBuffer.getChannelData(1)
        audioData = new Float32Array(left.length)
        for (let i = 0; i < left.length; i++) {
          audioData[i] = (left[i] + right[i]) / 2
        }
      } else {
        audioData = audioBuffer.getChannelData(0)
      }

      // Transcribe
      const result = await whisperRef.current(audioData)
      await audioContext.close()

      return result.text?.trim() || ''
    } catch (err) {
      console.error('Whisper transcription error:', err)
      return null
    }
  }, [])

  // Start recording with Whisper
  const startWhisperRecording = useCallback(async () => {
    try {
      // Start loading model in background
      if (!whisperRef.current && !isModelLoading) {
        setIsModelLoading(true)
        setModelLoadProgress(0)
        getWhisperTranscriber((progress) => {
          setModelLoadProgress(progress)
        }).then(transcriber => {
          whisperRef.current = transcriber
          setIsModelLoading(false)
          setModelLoadProgress(100)
        }).catch(() => {
          setIsModelLoading(false)
        })
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
      })

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start(100)
      setIsListening(true)
      setError(null)
      setTranscript('')
      setBackend('whisper')
    } catch (err) {
      setError('Microphone access denied. Please allow microphone access.')
      setIsListening(false)
    }
  }, [isModelLoading])

  // Stop Whisper recording and transcribe
  const stopWhisperRecording = useCallback(async () => {
    const mediaRecorder = mediaRecorderRef.current

    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
      setIsListening(false)
      return
    }

    return new Promise<void>((resolve) => {
      mediaRecorder.onstop = async () => {
        mediaRecorder.stream.getTracks().forEach(track => track.stop())

        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType
        })

        setTranscript('Transcribing...')
        const text = await transcribeWithWhisper(audioBlob)

        if (text) {
          setTranscript(text)
          if (onTranscript) {
            onTranscript(text, language)
          }
        } else {
          setTranscript('')
          setError('Could not transcribe audio. Please try again.')
        }

        setIsListening(false)
        resolve()
      }

      mediaRecorder.stop()
    })
  }, [transcribeWithWhisper, onTranscript, language])

  // Start listening with Web Speech API
  const startWebSpeech = useCallback(() => {
    const SpeechRecognitionClass = getSpeechRecognition()
    if (!SpeechRecognitionClass) {
      // Fall back to Whisper
      startWhisperRecording()
      return
    }

    if (recognitionRef.current) {
      recognitionRef.current.abort()
    }

    try {
      const recognition = new SpeechRecognitionClass()
      recognitionRef.current = recognition

      recognition.continuous = false
      recognition.interimResults = true
      recognition.lang = language
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        setIsListening(true)
        setError(null)
        setTranscript('')
        setBackend('web-speech')
      }

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          if (result.isFinal) {
            finalTranscript += result[0].transcript
          } else {
            interimTranscript += result[0].transcript
          }
        }

        const currentTranscript = finalTranscript || interimTranscript
        setTranscript(currentTranscript)

        if (finalTranscript && onTranscript) {
          onTranscript(finalTranscript.trim(), language)
        }
      }

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        setIsListening(false)
        recognitionRef.current = null

        // On network error (Brave blocks Google), fall back to Whisper
        if (event.error === 'network') {
          useWhisperFallback.current = true
          setError('Loading offline voice recognition...')
          startWhisperRecording()
          return
        }

        switch (event.error) {
          case 'no-speech':
            setError('No speech detected. Please try again.')
            break
          case 'audio-capture':
            setError('No microphone found. Please check your microphone settings.')
            break
          case 'not-allowed':
            setError('Microphone access denied. Please allow microphone access.')
            break
          case 'aborted':
            // User aborted, no error
            break
          default:
            setError(`Speech recognition error: ${event.error}`)
        }
      }

      recognition.onend = () => {
        setIsListening(false)
        recognitionRef.current = null
      }

      recognition.start()
    } catch (err) {
      // Fall back to Whisper
      startWhisperRecording()
    }
  }, [language, onTranscript, startWhisperRecording])

  const startListening = useCallback(() => {
    // If we've already determined Whisper is needed, use it directly
    if (useWhisperFallback.current || !isSpeechRecognitionSupported()) {
      startWhisperRecording()
    } else {
      startWebSpeech()
    }
  }, [startWebSpeech, startWhisperRecording])

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      stopWhisperRecording()
    } else {
      setIsListening(false)
    }
  }, [stopWhisperRecording])

  const toggleLanguage = useCallback(() => {
    setLanguageState(prev => prev === 'en-US' ? 'ur-PK' : 'en-US')
  }, [])

  const setLanguage = useCallback((lang: VoiceLanguage) => {
    setLanguageState(lang)
  }, [])

  const clearTranscript = useCallback(() => {
    setTranscript('')
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    // State
    isListening,
    isSupported,
    transcript,
    error,
    language,
    backend,
    isModelLoading,
    modelLoadProgress,
    // Actions
    startListening,
    stopListening,
    toggleLanguage,
    setLanguage,
    clearTranscript,
    clearError,
  }
}
