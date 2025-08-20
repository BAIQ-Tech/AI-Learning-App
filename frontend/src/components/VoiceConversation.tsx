import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './VoiceConversation.css';

interface VoiceConversationProps {
  selectedLanguage: string;
}

interface ConversationEntry {
  type: 'user' | 'ai';
  text: string;
  aiAudioUrl?: string;
  timestamp: Date;
}

const VoiceConversation: React.FC<VoiceConversationProps> = ({ selectedLanguage }) => {
  const { t } = useTranslation();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [conversation, setConversation] = useState<ConversationEntry[]>([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      
      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
        // Process audio after a short delay to ensure all data is collected
        setTimeout(() => {
          if (audioChunksRef.current.length > 0) {
            processAudio();
          }
        }, 100);
      };

      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];
      recorder.start(1000); // Record in 1-second chunks
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert(t('common.error') + ': ' + (error as Error).message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  const processAudio = async () => {
    try {
      // Check if we have enough audio data
      if (audioChunksRef.current.length === 0) {
        console.log('No audio data to process');
        return;
      }

      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Check minimum duration (at least 1 second)
      if (audioBlob.size < 1000) {
        alert('Recording too short. Please record for at least 1 second.');
        return;
      }

      const reader = new FileReader();
      
      reader.onloadend = async () => {
        const base64Audio = (reader.result as string).split(',')[1];
        
        const token = localStorage.getItem('authToken');
        if (!token) {
          alert('Please sign in to use voice conversation');
          return;
        }

        const response = await fetch('http://localhost:8000/api/voice-conversation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            audio_data: base64Audio,
            language_code: selectedLanguage || 'en'
          })
        });

        if (response.ok) {
          const data = await response.json();
          
          const userEntry: ConversationEntry = {
            type: 'user',
            text: data.user_text,
            timestamp: new Date()
          };
          
          const aiEntry: ConversationEntry = {
            type: 'ai',
            text: data.ai_response,
            aiAudioUrl: data.ai_audio,
            timestamp: new Date()
          };
          
          setConversation(prev => [...prev, userEntry, aiEntry]);
          
          if (data.ai_audio) {
            playAudio(data.ai_audio);
          }
        } else {
          const errorText = await response.text();
          console.error('Voice conversation failed:', response.status, errorText);
          alert(`${t('common.error')}: ${response.status} - ${errorText}`);
        }
      };
      
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Error processing audio:', error);
      alert(t('common.error'));
    } finally {
      setIsProcessing(false);
      audioChunksRef.current = [];
    }
  };

  // Remove the useEffect that was causing duplicate processing
  // Audio processing is now handled in the recorder.onstop callback

  const playAudio = (base64Audio: string) => {
    try {
      const audioBlob = new Blob([Uint8Array.from(atob(base64Audio), c => c.charCodeAt(0))], {
        type: 'audio/mpeg'
      });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
      }
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };


  const clearConversation = () => {
    setConversation([]);
  };

  return (
    <div className="voice-conversation-container">
      <div className="voice-header">
        <h2>{t('voice.title')}</h2>
        <p>{t('voice.welcome')}</p>
        <p className="voice-description">
          {t('voice.description')}
        </p>
      </div>
      <div className="messages-container">
        {conversation.length === 0 ? (
          <div className="welcome-message">
            <p>{t('voice.welcome')}</p>
            <p>{t('voice.description')}</p>
          </div>
        ) : (
          conversation.map((entry, index) => (
            <div key={index} className={`message ${entry.type}`}>
              <div className="message-content">
                <div className="message-text">{entry.text}</div>
                {entry.aiAudioUrl && (
                  <button 
                    onClick={() => playAudio(entry.aiAudioUrl!)}
                    className="replay-btn"
                  >
                    🔊 {t('voice.replay')}
                  </button>
                )}
              </div>
              <div className="message-time">
                {entry.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      <button 
        className="clear-button"
        onClick={clearConversation}
        disabled={conversation.length === 0}
      >
        {t('voice.clearConversation')}
      </button>
      <div className="recording-controls">
        <button 
          className={`record-button ${isRecording ? 'recording' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
        >
          {isRecording ? t('voice.stopRecording') : t('voice.startRecording')}
        </button>
        {isProcessing && (
          <div className="processing-indicator">
            {t('voice.processing')}
          </div>
        )}
      </div>
      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  );
};

export default VoiceConversation;
