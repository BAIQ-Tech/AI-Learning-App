import { setupServer } from 'msw/node';
import { rest } from 'msw';

// Mock API responses
export const handlers = [
  // Health check
  rest.get('/health', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        database: 'connected',
        version: '1.0.0'
      })
    );
  }),

  // Authentication endpoints
  rest.post('/api/auth/register', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        token: 'mock-jwt-token',
        user: {
          id: 1,
          email: 'test@example.com',
          name: 'Test User',
          auth_method: 'email'
        }
      })
    );
  }),

  rest.post('/api/auth/email', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        token: 'mock-jwt-token',
        user: {
          id: 1,
          email: 'test@example.com',
          name: 'Test User',
          auth_method: 'email'
        }
      })
    );
  }),

  rest.get('/api/auth/me', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Authentication required' })
      );
    }

    return res(
      ctx.status(200),
      ctx.json({
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        auth_method: 'email'
      })
    );
  }),

  // Language endpoints
  rest.get('/api/languages', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        en: { code: 'en', name: 'English', native: 'English', nativeName: 'English' },
        ja: { code: 'ja', name: 'Japanese', native: '日本語', nativeName: '日本語' },
        zh: { code: 'zh', name: 'Chinese', native: '中文', nativeName: '中文' },
        es: { code: 'es', name: 'Spanish', native: 'Español', nativeName: 'Español' }
      })
    );
  }),

  // Translation endpoint
  rest.post('/api/translate', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Authentication required' })
      );
    }

    return res(
      ctx.status(200),
      ctx.json({
        original_text: 'Hello',
        translated_text: 'Hola',
        source_language: 'en',
        target_language: 'es'
      })
    );
  }),

  // Conversation endpoint
  rest.post('/api/conversation', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Authentication required' })
      );
    }

    return res(
      ctx.status(200),
      ctx.json({
        user_message: 'Hello',
        ai_response: '¡Hola! ¿Cómo puedo ayudarte hoy?',
        language_code: 'es'
      })
    );
  }),

  // Voice conversation endpoint
  rest.post('/api/voice-conversation', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Authentication required' })
      );
    }

    return res(
      ctx.status(200),
      ctx.json({
        user_text: 'Hello',
        ai_response: '¡Hola! ¿Cómo estás?',
        ai_audio: 'base64-encoded-audio-data',
        language_code: 'es'
      })
    );
  }),

  // Stories endpoints
  rest.get('/api/stories', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
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
      ])
    );
  }),

  rest.post('/api/stories', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 2,
        media_url: null
      })
    );
  }),

  rest.post('/api/stories/:id/like', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        story_id: 1,
        status: 'liked',
        likes: 6
      })
    );
  }),

  // Games endpoint
  rest.post('/games/generate', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
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
      })
    );
  })
];

export const server = setupServer(...handlers);
