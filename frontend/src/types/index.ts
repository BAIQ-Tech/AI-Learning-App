export interface Language {
  code: string;
  name: string;
  native: string;
  nativeName?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface TranslationRequest {
  text: string;
  source_language: string;
  target_language: string;
}

export interface TranslationResponse {
  original_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface Lesson {
  title: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  vocabulary: VocabularyItem[];
  examples: string[];
  grammar: GrammarPoint;
  exercises: Exercise[];
}

export interface VocabularyItem {
  word: string;
  translation: string;
  pronunciation: string;
}

export interface GrammarPoint {
  point: string;
  explanation: string;
}

export interface Exercise {
  type: 'fill-blank' | 'translate' | 'multiple-choice';
  question: string;
  answer: string;
  options?: string[];
}

export interface UserProgress {
  user_id: number;
  progress: ProgressItem[];
}

export interface ProgressItem {
  language_code: string;
  lesson_id: string;
  score: number;
  completed_at: string;
}
