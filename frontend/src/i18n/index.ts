import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import enTranslation from './locales/en.json';
import jaTranslation from './locales/ja.json';
import zhTranslation from './locales/zh.json';
import esTranslation from './locales/es.json';
import elTranslation from './locales/el.json';
import heTranslation from './locales/he.json';
import deTranslation from './locales/de.json';
import frTranslation from './locales/fr.json';
import itTranslation from './locales/it.json';

const resources = {
  en: {
    translation: enTranslation,
  },
  ja: {
    translation: jaTranslation,
  },
  zh: {
    translation: zhTranslation,
  },
  es: {
    translation: esTranslation,
  },
  el: {
    translation: elTranslation,
  },
  he: {
    translation: heTranslation,
  },
  de: {
    translation: deTranslation,
  },
  fr: {
    translation: frTranslation,
  },
  it: {
    translation: itTranslation,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // default language
    fallbackLng: 'en',
    supportedLngs: ['en', 'ja', 'zh', 'es', 'el', 'he', 'de', 'fr', 'it'],
    debug: false,
    
    interpolation: {
      escapeValue: false
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage']
    }
  });

export default i18n;
