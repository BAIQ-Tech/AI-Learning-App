import React, { useState } from 'react';
import styled from 'styled-components';
import { FaExchangeAlt, FaCopy } from 'react-icons/fa';
import { useTranslation } from 'react-i18next';
import { Language } from '../types';
import { languageApi } from '../services/api';
import LanguageSelector from './LanguageSelector';
import { useAuth } from '../contexts/AuthContext';

const TranslationContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  color: #2d3748;
  margin-bottom: 24px;
  text-align: center;
`;

const TranslationArea = styled.div`
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
  align-items: start;
  margin-bottom: 20px;
`;

const TextSection = styled.div`
  display: flex;
  flex-direction: column;
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 120px;
  padding: 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &:disabled {
    background: #f7fafc;
    color: #718096;
  }
`;

const SwapButton = styled.button`
  padding: 12px;
  border: none;
  border-radius: 50%;
  background: #667eea;
  color: white;
  cursor: pointer;
  align-self: center;
  margin-top: 40px;
  
  &:hover {
    background: #5a67d8;
    transform: rotate(180deg);
  }
  
  transition: all 0.3s ease;
`;

const TranslateButton = styled.button`
  width: 100%;
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 16px;
  
  &:hover {
    background: #5a67d8;
  }
  
  &:disabled {
    background: #a0aec0;
    cursor: not-allowed;
  }
`;

const CopyButton = styled.button`
  padding: 8px 12px;
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  align-self: flex-end;
  margin-top: 8px;
  
  &:hover {
    background: #38a169;
  }
`;

const ErrorMessage = styled.div`
  color: #e53e3e;
  background: #fed7d7;
  padding: 12px;
  border-radius: 6px;
  margin-top: 12px;
`;

interface TranslationToolProps {
  languages: { [key: string]: Language };
}

const TranslationTool: React.FC<TranslationToolProps> = ({ languages }) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [sourceLanguage, setSourceLanguage] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('');
  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleTranslate = async () => {
    console.log('Translation Debug - User:', user);
    console.log('Translation Debug - Token:', localStorage.getItem('authToken'));
    
    if (!user) {
      setError('Please sign in to use the translation feature.');
      return;
    }

    if (!sourceText.trim() || !sourceLanguage || !targetLanguage) {
      setError('Please fill in all fields.');
      return;
    }

    if (sourceLanguage === targetLanguage) {
      setError('Source and target languages must be different.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      console.log('Translation Debug - Making API call with:', {
        text: sourceText,
        source_language: sourceLanguage,
        target_language: targetLanguage,
      });

      const response = await languageApi.translateText({
        text: sourceText,
        source_language: sourceLanguage,
        target_language: targetLanguage,
      });

      console.log('Translation Debug - API response:', response);
      setTranslatedText(response.translated_text);
    } catch (error: any) {
      console.error('Translation failed - Full error:', error);
      console.error('Translation failed - Response:', error.response);
      console.error('Translation failed - Status:', error.response?.status);
      console.error('Translation failed - Data:', error.response?.data);
      
      if (error.response?.status === 401) {
        setError('Session expired. Please sign in again.');
      } else if (error.response?.status === 403) {
        setError('Access denied. Please sign in again.');
      } else if (error.response?.status === 500) {
        setError('Translation service error. Please try again later.');
      } else {
        setError(`Translation failed: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwapLanguages = () => {
    const tempLang = sourceLanguage;
    setSourceLanguage(targetLanguage);
    setTargetLanguage(tempLang);
    
    const tempText = sourceText;
    setSourceText(translatedText);
    setTranslatedText(tempText);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <TranslationContainer>
      <Title>{t('translate.title')}</Title>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '16px', marginBottom: '20px' }}>
        <LanguageSelector
          languages={languages}
          selectedLanguage={sourceLanguage}
          onLanguageChange={setSourceLanguage}
          label={t('translate.sourceLanguage')}
        />
        
        <SwapButton onClick={handleSwapLanguages} disabled={!sourceLanguage || !targetLanguage}>
          <FaExchangeAlt />
        </SwapButton>
        
        <LanguageSelector
          languages={languages}
          selectedLanguage={targetLanguage}
          onLanguageChange={setTargetLanguage}
          label={t('translate.targetLanguage')}
        />
      </div>

      <TranslationArea>
        <TextSection>
          <TextArea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            placeholder={t('translate.enterText')}
          />
        </TextSection>

        <div></div>

        <TextSection>
          <TextArea
            value={translatedText}
            readOnly
            placeholder={t('translate.translation')}
          />
          {translatedText && (
            <CopyButton onClick={() => copyToClipboard(translatedText)}>
              <FaCopy /> {t('common.save')}
            </CopyButton>
          )}
        </TextSection>
      </TranslationArea>

      <TranslateButton
        onClick={handleTranslate}
        disabled={isLoading || !sourceText.trim() || !sourceLanguage || !targetLanguage}
      >
        {isLoading ? t('translate.translating') : t('translate.translate')}
      </TranslateButton>

      {error && <ErrorMessage>{error}</ErrorMessage>}
    </TranslationContainer>
  );
};

export default TranslationTool;
