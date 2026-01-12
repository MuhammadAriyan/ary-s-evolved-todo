/**
 * useWhisperTranscription hook - Browser-based Whisper transcription
 *
 * Uses Transformers.js to run Whisper locally in the browser.
 * No API calls, completely free, works in all browsers.
 * Model downloads once (~39MB) and is cached.
 */
'use client'

import { useState, useCallback, useRef, useEffect } from 'react'

type TranscriberStatus = 'idle' | 'loading' | 'ready' | 'recording' | 'transcribing' | 'error'

interface UseWhisperTranscriptionState {
  status: TranscriberStatus
  transcript: string
  error: string | null
  isModelLoaded: boolean
  loadingProgress: number
}

interface UseWhisperTranscriptionActions {
  loadModel: () => Promise<boolean>
  startRecording: () => Promise<void>
  stopRecording: () => Promise<string | null>
  transcribeAudio: (audioBlob: Blob) => Promise<string | null>
  clearTranscript: () => void
  clearError: () => void
}

export type UseWhisperTranscriptionReturn = UseWhisperTranscriptionState & UseWhisperTranscriptionActions

// Lazy load the pipeline to avoid SSR issues
let pipelinePromise: Promise<any> | null = null

async function getTranscriber(onProgress?: (progress: number) => void) {
  if (!pipelinePromise) {
    pipelinePromise = (async () => {
      const { pipeline } = await import('@huggingface/transformers')
      return pipeline('automatic-speech-recognition', 'Xenova/whisper-tiny.en', {
        progress_callback: (progress: any) => {
          if (progress.status === 'progress' && onProgress) {
            onProgress(Math.round(progress.progress))
          }
        }
      })
    })()
  }
  return pipelinePromise
}

export function useWhisperTranscription(): UseWhisperTranscriptionReturn {
  const [status, setStatus] = useState<TranscriberStatus>('idle')
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isModelLoaded, setIsModelLoaded] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const transcriberRef = useRef<any>(null)

  const loadModel = useCallback(async (): Promise<boolean> => {
    if (isModelLoaded && transcriberRef.current) {
      return true
    }

    try {
      setStatus('loading')
      setError(null)
      setLoadingProgress(0)

      transcriberRef.current = await getTranscriber((progress) => {
        setLoadingProgress(progress)
      })

      setIsModelLoaded(true)
      setStatus('ready')
      setLoadingProgress(100)
      return true
    } catch (err) {
      setError('Failed to load speech recognition model')
      setStatus('error')
      console.error('Whisper model load error:', err)
      return false
    }
  }, [isModelLoaded])

  const transcribeAudio = useCallback(async (audioBlob: Blob): Promise<string | null> => {
    if (!transcriberRef.current) {
      const loaded = await loadModel()
      if (!loaded) return null
    }

    try {
      setStatus('transcribing')
      setError(null)

      // Convert blob to array buffer
      const arrayBuffer = await audioBlob.arrayBuffer()

      // Decode audio using Web Audio API
      const audioContext = new AudioContext({ sampleRate: 16000 })
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

      // Get audio data as Float32Array (mono, 16kHz)
      let audioData: Float32Array
      if (audioBuffer.numberOfChannels > 1) {
        // Mix to mono
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
      const result = await transcriberRef.current(audioData)
      const text = result.text?.trim() || ''

      setTranscript(text)
      setStatus('ready')

      await audioContext.close()
      return text
    } catch (err) {
      setError('Failed to transcribe audio')
      setStatus('error')
      console.error('Transcription error:', err)
      return null
    }
  }, [loadModel])

  const startRecording = useCallback(async () => {
    try {
      // Load model in background while recording
      if (!isModelLoaded) {
        loadModel()
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
      mediaRecorder.start(100) // Collect data every 100ms
      setStatus('recording')
      setError(null)
      setTranscript('')
    } catch (err) {
      setError('Microphone access denied')
      setStatus('error')
      console.error('Recording error:', err)
    }
  }, [isModelLoaded, loadModel])

  const stopRecording = useCallback(async (): Promise<string | null> => {
    return new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current

      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        resolve(null)
        return
      }

      mediaRecorder.onstop = async () => {
        // Stop all tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop())

        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType
        })

        // Transcribe
        const text = await transcribeAudio(audioBlob)
        resolve(text)
      }

      mediaRecorder.stop()
    })
  }, [transcribeAudio])

  const clearTranscript = useCallback(() => {
    setTranscript('')
  }, [])

  const clearError = useCallback(() => {
    setError(null)
    if (status === 'error') {
      setStatus(isModelLoaded ? 'ready' : 'idle')
    }
  }, [status, isModelLoaded])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  return {
    // State
    status,
    transcript,
    error,
    isModelLoaded,
    loadingProgress,
    // Actions
    loadModel,
    startRecording,
    stopRecording,
    transcribeAudio,
    clearTranscript,
    clearError,
  }
}
