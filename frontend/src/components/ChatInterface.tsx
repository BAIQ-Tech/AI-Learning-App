import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FaMicrophone, FaMicrophoneSlash, FaPaperPlane } from 'react-icons/fa';
import { useTranslation } from 'react-i18next';
import { ConversationMessage } from '../types';
import { languageApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 500px;
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  background: white;
  overflow: hidden;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Message = styled.div<{ isUser: boolean }>`
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  background: ${props => props.isUser ? '#667eea' : '#f7fafc'};
  color: ${props => props.isUser ? 'white' : '#2d3748'};
  word-wrap: break-word;
  animation: fadeIn 0.3s ease-in;
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const InputContainer = styled.div`
  display: flex;
  padding: 16px;
  border-top: 1px solid #e1e5e9;
  gap: 12px;
  align-items: center;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e1e5e9;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  
  &:focus {
    border-color: #667eea;
  }
`;

const ActionButton = styled.button<{ isActive?: boolean }>`
  padding: 12px;
  border: none;
  border-radius: 50%;
  background: ${props => props.isActive ? '#e53e3e' : '#667eea'};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  
  &:hover {
    transform: scale(1.05);
  }
  
  &:disabled {
    background: #a0aec0;
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingMessage = styled.div`
  align-self: flex-start;
  padding: 12px 16px;
  border-radius: 18px;
  background: #f7fafc;
  color: #718096;
  font-style: italic;
`;

interface ChatInterfaceProps {
  selectedLanguage: string;
  userId?: number;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ selectedLanguage, userId }) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Debug authentication state
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const userStr = localStorage.getItem('ai-learning-user');
    console.log('Chat Debug - Token:', token ? 'Present' : 'Missing');
    console.log('Chat Debug - User from localStorage:', userStr ? JSON.parse(userStr) : 'Missing');
    console.log('Chat Debug - User from context:', user);
    console.log('Chat Debug - UserId prop:', userId);
  }, [userId, user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedLanguage || isLoading) return;

    const userMessage: ConversationMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Check authentication using context instead of localStorage directly
      if (!user) {
        throw new Error('Authentication required');
      }
      
      const token = localStorage.getItem('authToken');
      console.log('Send Message Debug:', {
        token: token ? 'Present' : 'Missing',
        userFromContext: user,
        userId: userId
      });
      
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await languageApi.sendMessage(inputMessage, selectedLanguage, userId);
      
      const aiMessage: ConversationMessage = {
        role: 'assistant',
        content: response.ai_response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error: any) {
      console.error('Failed to send message:', error);
      let errorText = t('common.error');
      
      if (error.message === 'Authentication required') {
        errorText = 'Please sign in to use the chat feature.';
      } else if (error.response?.status === 401) {
        errorText = 'Session expired. Please sign in again.';
      } else if (error.response?.status === 500) {
        errorText = 'Server error. Please try again later.';
      }
      
      const errorMessage: ConversationMessage = {
        role: 'assistant',
        content: errorText,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const startListening = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      
      // Set language for speech recognition
      const langMap: { [key: string]: string } = {
        'en': 'en-US',
        'ja': 'ja-JP',
        'zh': 'zh-CN',
        'es': 'es-ES',
        'el': 'el-GR',
        'he': 'he-IL'
      };
      recognition.lang = langMap[selectedLanguage] || 'en-US';

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.start();
    } else {
      alert(t('common.error'));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <ChatContainer>
      <MessagesContainer>
        {messages.length === 0 && (
          <Message isUser={false}>
            {t('chat.welcome')}
          </Message>
        )}
        {messages.map((message, index) => (
          <Message key={index} isUser={message.role === 'user'}>
            {message.content}
          </Message>
        ))}
        {isLoading && (
          <LoadingMessage>{t('common.loading')}</LoadingMessage>
        )}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      
      <InputContainer>
        <MessageInput
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={t('chat.placeholder')}
          disabled={isLoading || !selectedLanguage}
        />
        <ActionButton
          onClick={startListening}
          isActive={isListening}
          disabled={!selectedLanguage}
          title={t('voice.startRecording')}
        >
          {isListening ? <FaMicrophoneSlash /> : <FaMicrophone />}
        </ActionButton>
        <ActionButton
          onClick={sendMessage}
          disabled={!inputMessage.trim() || isLoading || !selectedLanguage}
          title={t('chat.send')}
        >
          <FaPaperPlane />
        </ActionButton>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatInterface;
