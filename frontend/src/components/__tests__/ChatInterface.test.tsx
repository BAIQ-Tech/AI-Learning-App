import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../../i18n';
import ChatInterface from '../ChatInterface';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock the auth context
const mockAuthContext = {
  user: {
    id: '1',
    email: 'test@example.com',
    name: 'Test User',
    authMethod: 'email' as const
  },
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
  isLoading: false
};

// Mock the useAuth hook
jest.mock('../../contexts/AuthContext', () => ({
  ...jest.requireActual('../../contexts/AuthContext'),
  useAuth: () => mockAuthContext
}));

// Mock the API service
jest.mock('../../services/api', () => ({
  languageApi: {
    sendMessage: jest.fn().mockResolvedValue({
      ai_response: '¡Hola! ¿Cómo puedo ayudarte hoy?'
    })
  }
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <I18nextProvider i18n={i18n}>
        <AuthProvider>
          {component}
        </AuthProvider>
      </I18nextProvider>
    </BrowserRouter>
  );
};

describe('ChatInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders chat interface correctly', () => {
    renderWithProviders(
      <ChatInterface selectedLanguage="es" userId={1} />
    );

    expect(screen.getByPlaceholderText(/chat.placeholder/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /voice.startRecording/i })).toBeInTheDocument();
  });

  it('displays welcome message when no messages', () => {
    renderWithProviders(
      <ChatInterface selectedLanguage="es" userId={1} />
    );

    expect(screen.getByText(/chat.welcome/i)).toBeInTheDocument();
  });

  it('sends message when form is submitted', async () => {
    const { languageApi } = require('../../services/api');
    
    renderWithProviders(
      <ChatInterface selectedLanguage="es" userId={1} />
    );

    const input = screen.getByPlaceholderText(/chat.placeholder/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(languageApi.sendMessage).toHaveBeenCalledWith('Hello', 'es', 1);
    });

    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('sends message when Enter key is pressed', async () => {
    const { languageApi } = require('../../services/api');
    
    renderWithProviders(
      <ChatInterface selectedLanguage="es" userId={1} />
    );

    const input = screen.getByPlaceholderText(/chat.placeholder/i);

    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(languageApi.sendMessage).toHaveBeenCalledWith('Hello', 'es', 1);
    });
  });

  it('does not send empty messages', () => {
    const { languageApi } = require('../../services/api');
    
    renderWithProviders(
      <ChatInterface selectedLanguage="es" userId={1} />
    );

    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    expect(languageApi.sendMessage).not.toHaveBeenCalled();
  });

  it('displays loading state while sending message', async () => {
    const { languageApi } = require('../../services/api');
    languageApi.sendMessage.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    renderWithProviders(
      <ChatInterface selectedLanguage="es" userId={1} />
    );

    const input = screen.getByPlaceholderText(/chat.placeholder/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);

    expect(screen.getByText(/common.loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText(/common.loading/i)).not.toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    const { languageApi } = require('../../services/api');
    languageApi.sendMessage.mockRejectedValue(new Error('API Error'));

    renderWithProviders(
      <ChatInterface selectedLanguage="es" userId={1} />
    );

    const input = screen.getByPlaceholderText(/chat.placeholder/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/common.error/i)).toBeInTheDocument();
    });
  });

  it('disables input when no language is selected', () => {
    renderWithProviders(
      <ChatInterface selectedLanguage="" userId={1} />
    );

    const input = screen.getByPlaceholderText(/chat.placeholder/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });
});
