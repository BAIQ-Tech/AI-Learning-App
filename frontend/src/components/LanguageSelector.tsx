import React from 'react';
import styled from 'styled-components';
import { Language } from '../types';

const SelectorContainer = styled.div`
  margin: 20px 0;
`;

const Select = styled.select`
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  cursor: pointer;
  min-width: 200px;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2d3748;
`;

interface LanguageSelectorProps {
  languages: { [key: string]: Language };
  selectedLanguage: string;
  onLanguageChange: (languageCode: string) => void;
  label: string;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  languages,
  selectedLanguage,
  onLanguageChange,
  label,
}) => {
  return (
    <SelectorContainer>
      <Label>{label}</Label>
      <Select
        value={selectedLanguage}
        onChange={(e) => onLanguageChange(e.target.value)}
      >
        <option value="">Select a language</option>
        {Object.entries(languages).map(([code, language]) => (
          <option key={code} value={code}>
            {language.name} ({language.native})
          </option>
        ))}
      </Select>
    </SelectorContainer>
  );
};

export default LanguageSelector;
