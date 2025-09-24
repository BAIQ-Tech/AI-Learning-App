import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// Mock API responses
export const handlers = [
  // Health check
  http.get('/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: 'connected',
      version: '1.0.0'
    });
  }),

  // Authentication endpoints
  http.post('/api/auth/register', () => {
    return HttpResponse.json({
      token: 'mock-jwt-token',
      user: {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        auth_method: 'email'
      }
    });
  }),

  http.post('/api/auth/email', () => {
    return HttpResponse.json({
      token: 'mock-jwt-token',
      user: {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        auth_method: 'email'
      }
    });
  }),

  http.get('/api/auth/me', ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      );
    }

    return HttpResponse.json({
      id: 1,
      email: 'test@example.com',
      name: 'Test User',
      auth_method: 'email'
    });
  }),

  // Language endpoints
  http.get('/api/languages', () => {
    return HttpResponse.json({
      en: { code: 'en', name: 'English', native: 'English', nativeName: 'English' },
      ja: { code: 'ja', name: 'Japanese', native: '日本語', nativeName: '日本語' },
      zh: { code: 'zh', name: 'Chinese', native: '中文', nativeName: '中文' },
      es: { code: 'es', name: 'Spanish', native: 'Español', nativeName: 'Español' }
    });
  }),

  // Translation endpoint
  http.post('/api/translate', ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      );
    }

    return HttpResponse.json({
      original_text: 'Hello',
      translated_text: 'Hola',
      source_language: 'en',
      target_language: 'es'
    });
  }),

  // Conversation endpoint
  http.post('/api/conversation', ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      );
    }

    return HttpResponse.json({
      user_message: 'Hello',
      ai_response: '¡Hola! ¿Cómo puedo ayudarte hoy?',
      language_code: 'es'
    });
  }),

  // Voice conversation endpoint
  http.post('/api/voice-conversation', ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      );
    }

    return HttpResponse.json({
      user_text: 'Hello',
      ai_response: '¡Hola! ¿Cómo estás?',
      ai_audio: 'base64-encoded-audio-data',
      language_code: 'es'
    });
  }),

  // Stories endpoints
  http.get('/api/stories', () => {
    return HttpResponse.json([
      {
        id: 1,
        user_id: 1,
        content_type: 'text',
        text: 'My first story',
        media_url: null,
        created_at: '2024-01-01T00:00:00Z',
        likes: 5,
        liked_by_me: false
      }
    ]);
  }),

  http.post('/api/stories', () => {
    return HttpResponse.json({
      id: 2,
      media_url: null
    }, { status: 201 });
  }),

  http.post('/api/stories/:id/like', () => {
    return HttpResponse.json({
      story_id: 1,
      status: 'liked',
      likes: 6
    });
  }),

  // Games endpoint
  http.post('/games/generate', () => {
    return HttpResponse.json({
      game_type: 'vocabulary_quiz',
      title: 'Spanish Vocabulary Quiz',
      questions: [
        {
          question: 'What does "hola" mean?',
          options: ['Hello', 'Goodbye', 'Thank you', 'Please'],
          correct_answer: 0,
          explanation: 'Hola means hello in Spanish'
        }
      ]
    });
  })
];

export const server = setupServer(...handlers);