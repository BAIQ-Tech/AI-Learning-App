import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaHome, FaComments, FaLanguage, FaBook, FaMicrophone, FaGamepad, FaNewspaper, FaSignInAlt, FaBars, FaTimes } from 'react-icons/fa';
import { useTranslation } from 'react-i18next';
import { Language } from './types';
import { languageApi } from './services/api';
import LanguageSelector from './components/LanguageSelector';
import ChatInterface from './components/ChatInterface';
import TranslationTool from './components/TranslationTool';
import LessonViewer from './components/LessonViewer';
import VoiceConversation from './components/VoiceConversation';
import LanguageGames from './components/LanguageGames';
import LanguageSwitcher from './components/LanguageSwitcher';
import PrivacyPolicy from './pages/PrivacyPolicy';
import News from './components/News';
import Login from './components/Login';
import UserProfile from './components/UserProfile';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './i18n';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const HeaderContainer = styled.header`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 16px 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 100;
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;

  @media (max-width: 768px) {
    padding: 0 16px;
  }

  @media (max-width: 480px) {
    padding: 0 12px;
  }
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 200px;
  justify-content: flex-end;

  @media (max-width: 768px) {
    min-width: auto;
    gap: 12px;
  }
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: #4a5568;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  }

  @media (max-width: 768px) {
    display: block;
  }
`;

const LoginButton = styled.button`
  display: flex !important;
  align-items: center;
  gap: 8px;
  background: #4299e1 !important;
  color: white !important;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
  margin-left: 12px;
  z-index: 999;
  position: relative;
  min-width: 120px;
  height: 44px;

  &:hover {
    background: #3182ce !important;
    transform: translateY(-1px);
  }

  @media (max-width: 768px) {
    padding: 10px 20px;
    font-size: 13px;
    min-width: 100px;
    height: 40px;
    margin-left: 8px;
  }

  @media (max-width: 480px) {
    padding: 8px 16px;
    font-size: 12px;
    min-width: 90px;
    height: 36px;
    margin-left: 4px;
  }
`;

const AppTitle = styled.h1`
  color: #667eea;
  font-size: 28px;
  font-weight: 700;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 24px;
  }

  @media (max-width: 480px) {
    font-size: 20px;
  }
`;

const Navigation = styled.nav<{ isOpen?: boolean }>`
  display: flex;
  gap: 8px;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 16px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);

  @media (max-width: 768px) {
    flex-direction: column;
    position: fixed;
    top: 100px;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    transform: ${({ isOpen }) => isOpen ? 'translateY(0)' : 'translateY(-100%)'};
    opacity: ${({ isOpen }) => isOpen ? '1' : '0'};
    visibility: ${({ isOpen }) => isOpen ? 'visible' : 'hidden'};
    transition: all 0.3s ease-in-out;
    z-index: 999;
    padding: 20px;
    gap: 12px;
    box-shadow: 0 5px 25px rgba(0, 0, 0, 0.15);
  }
`;

const NavLink = styled(Link)<{ active?: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-radius: 12px;
  text-decoration: none;
  color: ${props => props.active ? '#ffffff' : '#4a5568'};
  background: ${props => props.active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'rgba(255, 255, 255, 0.8)'};
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
  border: 2px solid ${props => props.active ? 'transparent' : 'rgba(102, 126, 234, 0.2)'};
  box-shadow: ${props => props.active ? '0 8px 25px rgba(102, 126, 234, 0.3)' : '0 4px 15px rgba(0, 0, 0, 0.1)'};
  transform: ${props => props.active ? 'translateY(-2px)' : 'translateY(0)'};
  min-width: 140px;
  justify-content: center;
  
  svg {
    font-size: 20px;
  }
  
  &:hover {
    background: ${props => props.active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
    color: #ffffff;
    transform: translateY(-4px);
    box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    border-color: transparent;
  }
  
  @media (max-width: 768px) {
    padding: 12px 16px;
    min-width: 120px;
    font-size: 14px;
    
    svg {
      font-size: 18px;
    }
  }
  
  @media (max-width: 480px) {
    padding: 10px 12px;
    min-width: 100px;
    font-size: 12px;
    gap: 8px;
    
    svg {
      font-size: 16px;
    }
  }
`;

const MainContent = styled.main`
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;

  @media (max-width: 768px) {
    padding: 30px 16px;
  }

  @media (max-width: 480px) {
    padding: 20px 12px;
  }
`;

const WelcomeSection = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const WelcomeTitle = styled.h2`
  color: white;
  font-size: 48px;
  margin-bottom: 24px;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  font-weight: 700;

  @media (max-width: 768px) {
    font-size: 36px;
    margin-bottom: 20px;
  }

  @media (max-width: 480px) {
    font-size: 28px;
    margin-bottom: 16px;
  }
`;

const WelcomeSubtitle = styled.p`
  color: rgba(255, 255, 255, 0.95);
  font-size: 22px;
  max-width: 700px;
  margin: 0 auto 32px;
  line-height: 1.7;
  font-weight: 400;

  @media (max-width: 768px) {
    font-size: 18px;
    margin-bottom: 24px;
  }

  @media (max-width: 480px) {
    font-size: 16px;
    margin-bottom: 20px;
    max-width: 100%;
  }
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin: 48px 0;
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;

  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 32px 0;
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 16px;
    margin: 24px 0;
  }
`;

const FeatureCard = styled.div`
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.4);
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);

    &::before {
      opacity: 1;
    }
  }

  @media (max-width: 768px) {
    padding: 24px 20px;
    border-radius: 16px;
  }

  @media (max-width: 480px) {
    padding: 20px 16px;
    border-radius: 12px;
    min-height: 120px;
  }
`;

const FeatureIcon = styled.div`
  font-size: 48px;
  color: white;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;

  @media (max-width: 768px) {
    font-size: 40px;
    margin-bottom: 16px;
  }

  @media (max-width: 480px) {
    font-size: 32px;
    margin-bottom: 12px;
  }
`;

const FeatureTitle = styled.h3`
  color: white;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;

  @media (max-width: 768px) {
    font-size: 20px;
    margin-bottom: 10px;
  }

  @media (max-width: 480px) {
    font-size: 18px;
    margin-bottom: 8px;
  }
`;

const FeatureDescription = styled.p`
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  line-height: 1.6;
  position: relative;
  z-index: 1;

  @media (max-width: 480px) {
    font-size: 14px;
    line-height: 1.5;
  }
`;

const LanguageGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 32px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin: 24px 0;
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 12px;
    margin: 20px 0;
  }
`;

const LanguageCard = styled.div<{ selected?: boolean }>`
  background: ${props => props.selected ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)'};
  backdrop-filter: blur(10px);
  border: 2px solid ${props => props.selected ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)'};
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
    transform: translateY(-2px);
  }

  @media (max-width: 768px) {
    padding: 16px;
    border-radius: 10px;
  }

  @media (max-width: 480px) {
    padding: 14px;
    border-radius: 8px;
    min-height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
`;

const LanguageName = styled.div`
  color: white;
  font-weight: 600;
  margin-bottom: 4px;
`;

const LanguageNative = styled.div`
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
`;

const PageContainer = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

  @media (max-width: 768px) {
    padding: 24px;
    border-radius: 12px;
  }

  @media (max-width: 480px) {
    padding: 16px;
    border-radius: 8px;
  }
`;

const PageTitle = styled.h2`
  color: #2d3748;
  margin-bottom: 24px;
  text-align: center;
  font-size: 28px;

  @media (max-width: 768px) {
    font-size: 24px;
    margin-bottom: 20px;
  }

  @media (max-width: 480px) {
    font-size: 20px;
    margin-bottom: 16px;
  }
`;


const NavigationBar: React.FC<{ isOpen: boolean }> = ({ isOpen }) => {
  const location = useLocation();
  const currentPath = location.pathname;
  const { t } = useTranslation();

  return (
    <Navigation isOpen={isOpen}>
      <NavLink to="/" active={currentPath === '/'}>
        <FaHome /> {t('navigation.home')}
      </NavLink>
      <NavLink to="/chat" active={currentPath === '/chat'}>
        <FaComments /> {t('navigation.chat')}
      </NavLink>
      <NavLink to="/voice" active={currentPath === '/voice'}>
        <FaMicrophone /> {t('navigation.voice')}
      </NavLink>
      <NavLink to="/games" active={currentPath === '/games'}>
        <FaGamepad /> {t('navigation.games')}
      </NavLink>
      <NavLink to="/translate" active={currentPath === '/translate'}>
        <FaLanguage /> {t('navigation.translate')}
      </NavLink>
      <NavLink to="/lessons" active={currentPath === '/lessons'}>
        <FaBook /> {t('navigation.lessons')}
      </NavLink>
      <NavLink to="/news" active={currentPath === '/news'}>
        <FaNewspaper /> {t('navigation.news')}
      </NavLink>
    </Navigation>
  );
};

const HeaderComponent: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [showLogin, setShowLogin] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  console.log('Header Debug:', { user, showLogin });

  return (
    <>
      <HeaderContainer>
        <HeaderContent>
          <AppTitle>{t('app.title')}</AppTitle>
          <HeaderRight>
            <LanguageSwitcher />
            {user ? (
              <UserProfile />
            ) : (
              <LoginButton onClick={() => setShowLogin(true)}>
                <FaSignInAlt />
                {t('auth.signIn')}
              </LoginButton>
            )}
            <MobileMenuButton onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
              {isMobileMenuOpen ? <FaTimes /> : <FaBars />}
            </MobileMenuButton>
          </HeaderRight>
        </HeaderContent>
      </HeaderContainer>
      <NavigationBar isOpen={isMobileMenuOpen} />
      {showLogin && <Login isOpen={showLogin} onClose={() => setShowLogin(false)} />}
    </>
  );
};

const HomePage: React.FC<{
  languages: { [key: string]: Language };
  selectedLanguage: string;
  onLanguageSelect: (code: string) => void;
}> = ({ languages, selectedLanguage, onLanguageSelect }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const features = [
    {
      icon: <FaComments />,
      title: t('navigation.chat'),
      description: t('features.chat.description'),
      path: '/chat'
    },
    {
      icon: <FaMicrophone />,
      title: t('navigation.voice'),
      description: t('features.voice.description'),
      path: '/voice'
    },
    {
      icon: <FaGamepad />,
      title: t('navigation.games'),
      description: t('features.games.description'),
      path: '/games'
    },
    {
      icon: <FaLanguage />,
      title: t('navigation.translate'),
      description: t('features.translate.description'),
      path: '/translate'
    },
    {
      icon: <FaBook />,
      title: t('navigation.lessons'),
      description: t('features.lessons.description'),
      path: '/lessons'
    },
    {
      icon: <FaNewspaper />,
      title: t('navigation.news'),
      description: t('features.news.description'),
      path: '/news'
    }
  ];

  return (
    <div>
      <WelcomeSection>
        <WelcomeTitle>{t('app.welcome')}</WelcomeTitle>
        <WelcomeSubtitle>
          {t('app.subtitle')}
        </WelcomeSubtitle>
        
        <FeatureGrid>
          {features.map((feature, index) => (
            <FeatureCard key={index} onClick={() => navigate(feature.path)}>
              <FeatureIcon>{feature.icon}</FeatureIcon>
              <FeatureTitle>{feature.title}</FeatureTitle>
              <FeatureDescription>{feature.description}</FeatureDescription>
            </FeatureCard>
          ))}
        </FeatureGrid>
      </WelcomeSection>

      <LanguageGrid>
        {Object.entries(languages).map(([code, language]) => (
          <LanguageCard
            key={code}
            selected={selectedLanguage === code}
            onClick={() => onLanguageSelect(code)}
          >
            <LanguageName>{language.name}</LanguageName>
            <LanguageNative>{language.nativeName}</LanguageNative>
          </LanguageCard>
        ))}
      </LanguageGrid>

      {selectedLanguage && (
        <PageContainer>
          <PageTitle>
            {t('home.readyToLearn', { language: languages[selectedLanguage]?.name })}
          </PageTitle>
          <p style={{ textAlign: 'center', color: '#718096', marginBottom: '24px' }}>
            {t('home.description')}
          </p>
        </PageContainer>
      )}
    </div>
  );
};

const ChatPage: React.FC<{
  selectedLanguage: string;
  languages: { [key: string]: Language };
  onLanguageSelect: (code: string) => void;
}> = ({ selectedLanguage, languages, onLanguageSelect }) => {
  const { t } = useTranslation();
  const { user } = useAuth();

  return (
    <PageContainer>
      <PageTitle>{t('chat.title')}</PageTitle>
      {!selectedLanguage ? (
        <div>
          <p style={{ textAlign: 'center', marginBottom: '24px', color: '#718096' }}>
            {t('chat.selectLanguage')}
          </p>
          <LanguageSelector
            languages={languages}
            selectedLanguage={selectedLanguage}
            onLanguageChange={onLanguageSelect}
            label={t('common.selectLanguage')}
          />
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: '20px', textAlign: 'center' }}>
            <p style={{ color: '#718096' }}>
              {t('chat.practice', { language: languages[selectedLanguage]?.name })}
            </p>
          </div>
          <ChatInterface selectedLanguage={selectedLanguage} userId={user?.id ? parseInt(user.id) : undefined} />
        </div>
      )}
    </PageContainer>
  );
};

const VoicePage: React.FC<{
  selectedLanguage: string;
  languages: { [key: string]: Language };
  onLanguageSelect: (code: string) => void;
}> = ({ selectedLanguage, languages, onLanguageSelect }) => {
  const { t } = useTranslation();

  return (
    <div>
      {!selectedLanguage ? (
        <PageContainer>
          <PageTitle>{t('voice.title')}</PageTitle>
          <p style={{ textAlign: 'center', marginBottom: '24px', color: '#718096' }}>
            {t('voice.selectLanguage')}
          </p>
          <LanguageSelector
            languages={languages}
            selectedLanguage={selectedLanguage}
            onLanguageChange={onLanguageSelect}
            label={t('common.selectLanguage')}
          />
        </PageContainer>
      ) : (
        <VoiceConversation selectedLanguage={selectedLanguage} />
      )}
    </div>
  );
};

const GamesPage: React.FC<{
  selectedLanguage: string;
  languages: { [key: string]: Language };
  onLanguageSelect: (code: string) => void;
}> = ({ selectedLanguage, languages, onLanguageSelect }) => {
  const { t } = useTranslation();

  return (
    <div>
      {!selectedLanguage ? (
        <PageContainer>
          <PageTitle>{t('games.title')}</PageTitle>
          <p style={{ textAlign: 'center', marginBottom: '24px', color: '#718096' }}>
            {t('games.selectLanguage')}
          </p>
          <LanguageSelector
            languages={languages}
            selectedLanguage={selectedLanguage}
            onLanguageChange={onLanguageSelect}
            label={t('common.selectLanguage')}
          />
        </PageContainer>
      ) : (
        <LanguageGames selectedLanguage={selectedLanguage} />
      )}
    </div>
  );
};

const LessonsPage: React.FC<{
  selectedLanguage: string;
  languages: { [key: string]: Language };
  onLanguageSelect: (code: string) => void;
}> = ({ selectedLanguage, languages, onLanguageSelect }) => {
  const { t } = useTranslation();

  return (
    <PageContainer>
      <PageTitle>{t('lessons.title')}</PageTitle>
      {!selectedLanguage ? (
        <div>
          <p style={{ textAlign: 'center', marginBottom: '24px', color: '#718096' }}>
            {t('lessons.selectLanguage')}
          </p>
          <LanguageSelector
            languages={languages}
            selectedLanguage={selectedLanguage}
            onLanguageChange={onLanguageSelect}
            label={t('common.selectLanguage')}
          />
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: '20px', textAlign: 'center' }}>
            <p style={{ color: '#718096' }}>
              {t('lessons.learn', { language: languages[selectedLanguage]?.name })}
            </p>
          </div>
          <LessonViewer selectedLanguage={selectedLanguage} />
        </div>
      )}
    </PageContainer>
  );
};

const NewsPage: React.FC = () => (
  <News />
);

const AppContent: React.FC = () => {
  const { t } = useTranslation();
  const [languages, setLanguages] = useState<{ [key: string]: Language }>({});
  const [selectedLanguage, setSelectedLanguage] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const languageData = await languageApi.getSupportedLanguages();
        setLanguages(languageData);
        
        // Set fallback languages if API fails
        if (Object.keys(languageData).length === 0) {
          const fallbackLanguages = {
            'en': { code: 'en', name: 'English', native: 'English', nativeName: 'English' },
            'ja': { code: 'ja', name: 'Japanese', native: '日本語', nativeName: '日本語' },
            'zh': { code: 'zh', name: 'Chinese', native: '中文', nativeName: '中文' },
            'es': { code: 'es', name: 'Spanish', native: 'Español', nativeName: 'Español' },
            'el': { code: 'el', name: 'Greek', native: 'Ελληνικά', nativeName: 'Ελληνικά' },
            'he': { code: 'he', name: 'Hebrew', native: 'עברית', nativeName: 'עברית' },
            'de': { code: 'de', name: 'German', native: 'Deutsch', nativeName: 'Deutsch' },
            'fr': { code: 'fr', name: 'French', native: 'Français', nativeName: 'Français' },
            'it': { code: 'it', name: 'Italian', native: 'Italiano', nativeName: 'Italiano' }
          };
          setLanguages(fallbackLanguages);
        }
      } catch (error) {
        console.error('Error loading languages:', error);
        // Set fallback languages on error
        const fallbackLanguages = {
          'en': { code: 'en', name: 'English', native: 'English', nativeName: 'English' },
          'ja': { code: 'ja', name: 'Japanese', native: '日本語', nativeName: '日本語' },
          'zh': { code: 'zh', name: 'Chinese', native: '中文', nativeName: '中文' },
          'es': { code: 'es', name: 'Spanish', native: 'Español', nativeName: 'Español' },
          'el': { code: 'el', name: 'Greek', native: 'Ελληνικά', nativeName: 'Ελληνικά' },
          'he': { code: 'he', name: 'Hebrew', native: 'עברית', nativeName: 'עברית' },
          'de': { code: 'de', name: 'German', native: 'Deutsch', nativeName: 'Deutsch' },
          'fr': { code: 'fr', name: 'French', native: 'Français', nativeName: 'Français' },
          'it': { code: 'it', name: 'Italian', native: 'Italiano', nativeName: 'Italiano' }
        };
        setLanguages(fallbackLanguages);
      } finally {
        setLoading(false);
      }
    };

    loadLanguages();
  }, []);

  if (loading) {
    return (
      <AppContainer>
        <HeaderComponent />
        <MainContent>
          <div style={{ textAlign: 'center', padding: '50px', color: 'white' }}>
            {t('common.loading')}
          </div>
        </MainContent>
      </AppContainer>
    );
  }

  return (
    <AppContainer>
      <HeaderComponent />
      <MainContent>
        <Routes>
          <Route
            path="/"
            element={
              <HomePage
                languages={languages}
                selectedLanguage={selectedLanguage}
                onLanguageSelect={setSelectedLanguage}
              />
            }
          />
          <Route
            path="/chat"
            element={
              <ProtectedRoute onOpenLogin={() => setIsLoginOpen(true)}>
                <ChatPage
                  selectedLanguage={selectedLanguage}
                  languages={languages}
                  onLanguageSelect={setSelectedLanguage}
                />
              </ProtectedRoute>
            }
          />
          <Route
            path="/translate"
            element={
              <ProtectedRoute onOpenLogin={() => setIsLoginOpen(true)}>
                <TranslationTool languages={languages} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/voice"
            element={
              <ProtectedRoute onOpenLogin={() => setIsLoginOpen(true)}>
                <VoicePage
                  selectedLanguage={selectedLanguage}
                  languages={languages}
                  onLanguageSelect={setSelectedLanguage}
                />
              </ProtectedRoute>
            }
          />
          <Route
            path="/games"
            element={
              <ProtectedRoute onOpenLogin={() => setIsLoginOpen(true)}>
                <GamesPage
                  selectedLanguage={selectedLanguage}
                  languages={languages}
                  onLanguageSelect={setSelectedLanguage}
                />
              </ProtectedRoute>
            }
          />
          <Route
            path="/lessons"
            element={
              <ProtectedRoute onOpenLogin={() => setIsLoginOpen(true)}>
                <LessonsPage
                  selectedLanguage={selectedLanguage}
                  languages={languages}
                  onLanguageSelect={setSelectedLanguage}
                />
              </ProtectedRoute>
            }
          />
          <Route
            path="/news"
            element={
              <ProtectedRoute onOpenLogin={() => setIsLoginOpen(true)}>
                <NewsPage />
              </ProtectedRoute>
            }
          />
          <Route path="/privacy" element={<PrivacyPolicy />} />
        </Routes>
        <Login isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} />
      </MainContent>
    </AppContainer>
  );
};

const App: React.FC = () => (
  <AuthProvider>
    <Router>
      <AppContent />
    </Router>
  </AuthProvider>
);

export default App;
