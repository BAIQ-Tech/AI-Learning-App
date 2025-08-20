import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const AuthRequiredContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px 20px;
  text-align: center;
`;

const AuthRequiredTitle = styled.h2`
  color: #2d3748;
  margin-bottom: 16px;
  font-size: 24px;
`;

const AuthRequiredMessage = styled.p`
  color: #4a5568;
  margin-bottom: 32px;
  font-size: 16px;
  max-width: 400px;
`;

const SignInButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
`;

interface ProtectedRouteProps {
  children: React.ReactNode;
  onOpenLogin: () => void;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, onOpenLogin }) => {
  const { user } = useAuth();
  const { t } = useTranslation();

  if (!user) {
    return (
      <AuthRequiredContainer>
        <AuthRequiredTitle>{t('auth.authRequired')}</AuthRequiredTitle>
        <AuthRequiredMessage>
          {t('auth.authRequired')}
        </AuthRequiredMessage>
        <SignInButton onClick={onOpenLogin}>
          {t('auth.signIn')}
        </SignInButton>
      </AuthRequiredContainer>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
