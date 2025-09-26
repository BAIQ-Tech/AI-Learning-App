import React, { useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { FaGoogle, FaApple, FaEye, FaEyeSlash, FaTimes } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

const LoginOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
`;

const LoginModal = styled.div`
  background: white;
  border-radius: 20px;
  padding: 40px;
  width: 90%;
  max-width: 450px;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease-out;

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @media (max-width: 768px) {
    padding: 30px 25px;
    border-radius: 16px;
    max-width: 90vw;
    margin: 20px;
  }

  @media (max-width: 480px) {
    padding: 24px 20px;
    border-radius: 12px;
    max-width: 95vw;
    margin: 10px;
  }
`;

const CloseButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 24px;
  color: #718096;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.2s;

  &:hover {
    background: #f7fafc;
    color: #2d3748;
  }

  @media (max-width: 768px) {
    top: 16px;
    right: 16px;
    padding: 8px;
  }

  @media (max-width: 480px) {
    top: 12px;
    right: 12px;
    padding: 10px;
    font-size: 20px;
  }
`;

const LoginTitle = styled.h2`
  text-align: center;
  color: #2d3748;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;

  @media (max-width: 768px) {
    font-size: 24px;
    margin-bottom: 24px;
  }

  @media (max-width: 480px) {
    font-size: 20px;
    margin-bottom: 20px;
  }
`;

const LoginForm = styled.form`
  margin-bottom: 30px;
`;

const InputGroup = styled.div`
  margin-bottom: 20px;
  position: relative;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  color: #4a5568;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.2s;
  box-sizing: border-box;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #a0aec0;
  }

  @media (max-width: 480px) {
    padding: 14px 16px;
    font-size: 16px; /* Prevent zoom on iOS */
  }
`;

const PasswordInput = styled.div`
  position: relative;
`;

const PasswordToggle = styled.button`
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 4px;

  &:hover {
    color: #4a5568;
  }
`;

const LoginButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 20px;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  @media (max-width: 480px) {
    padding: 16px;
    font-size: 16px;
    min-height: 48px; /* Better touch target */
  }
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  margin: 30px 0;
  
  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #e2e8f0;
  }
  
  span {
    margin: 0 20px;
    color: #718096;
    font-size: 14px;
  }
`;

const SocialButton = styled.button`
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  color: #4a5568;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 12px;

  &:hover {
    border-color: #cbd5e0;
    background: #f7fafc;
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  @media (max-width: 480px) {
    padding: 14px;
    min-height: 44px; /* Better touch target */
    font-size: 16px;
  }
`;

const WalletSection = styled.div`
  margin-top: 20px;
`;

const WalletTitle = styled.h3`
  color: #4a5568;
  font-size: 16px;
  margin-bottom: 15px;
  text-align: center;
`;

const WalletButton = styled(SocialButton)`
  background: white;
  color: #1a202c;
  border: 2px solid #e2e8f0;

  &:hover {
    background: #f7fafc;
    border-color: #cbd5e0;
  }
`;

const PhantomButton = styled(SocialButton)`
  background: white;
  color: #ab9ff2;
  border: 2px solid #e2e8f0;

  &:hover {
    background: #f7fafc;
    border-color: #cbd5e0;
  }
`;

const ErrorMessage = styled.div`
  background: #fed7d7;
  color: #c53030;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
  font-size: 14px;
`;

const SwitchModeButton = styled.button`
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
  margin-top: 10px;
  
  &:hover {
    color: #0056b3;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const MetaMaskIcon = () => (
  <svg width="20" height="20" viewBox="0 0 318.6 318.6">
    <path d="M274.1,35.5l-99.5,73.9L193,65.8z" fill="#e2761b"/>
    <path d="M44.4,35.5l98.7,74.6l-17.5-44.3z" fill="#e4761b"/>
    <path d="M238.3,206.8l-26.5,40.6l56.7,15.6l16.3-55.3z" fill="#e4761b"/>
    <path d="M33.9,207.7l16.2,55.3l56.7-15.6l-26.5-40.6z" fill="#e4761b"/>
    <path d="M180.3,262.3l-26.5-40.6l-26.5,40.6l26.5,19.6z" fill="#d7c1b3"/>
    <path d="M238.3,206.8l-58.0,55.5l26.5,19.6l31.5-75.1z" fill="#233447"/>
    <path d="M80.2,206.8l31.5,75.1l26.5-19.6l-58.0-55.5z" fill="#233447"/>
    <path d="M153.8,109.4l-17.5,44.3l58.0,0l-17.5-44.3z" fill="#cd6116"/>
    <path d="M274.1,35.5l-80.8,73.9l17.5,44.3l63.3-118.2z" fill="#e4751f"/>
    <path d="M44.4,35.5l63.3,118.2l17.5-44.3L44.4,35.5z" fill="#e4751f"/>
    <path d="M238.3,206.8l-31.5,75.1l-26.5-19.6l58.0-55.5z" fill="#f6851b"/>
    <path d="M80.2,206.8l58.0,55.5l-26.5,19.6l-31.5-75.1z" fill="#f6851b"/>
    <path d="M180.3,262.3l26.5,19.6l26.5-19.6l-26.5,40.6z" fill="#c0ad9e"/>
    <path d="M153.8,109.4l40.5,97.4l40.5-97.4l-40.5,0z" fill="#e2761b"/>
  </svg>
);

const PhantomIcon = () => (
  <svg width="20" height="20" viewBox="0 0 108 108">
    <defs>
      <linearGradient id="phantom-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#ab9ff2" />
        <stop offset="100%" stopColor="#551bf9" />
      </linearGradient>
    </defs>
    <path d="M54,0C83.823,0,108,24.177,108,54S83.823,108,54,108,0,83.823,0,54,24.177,0,54,0Z" fill="url(#phantom-gradient)"/>
    <path d="M81.5,36.5c-3.5-3.5-8.5-3.5-12,0L54,52,38.5,36.5c-3.5-3.5-8.5-3.5-12,0s-3.5,8.5,0,12L42,64,26.5,79.5c-3.5,3.5-3.5,8.5,0,12s8.5,3.5,12,0L54,76l15.5,15.5c3.5,3.5,8.5,3.5,12,0s3.5-8.5,0-12L66,64,81.5,48.5C85,45,85,40,81.5,36.5Z" fill="white"/>
    <circle cx="45" cy="45" r="3" fill="#551bf9"/>
    <circle cx="63" cy="45" r="3" fill="#551bf9"/>
  </svg>
);

const CoinbaseIcon = () => (
  <svg width="20" height="20" viewBox="0 0 1024 1024">
    <circle cx="512" cy="512" r="512" fill="#0052ff"/>
    <path d="M512,692c-99.4,0-180-80.6-180-180s80.6-180,180-180s180,80.6,180,180S611.4,692,512,692z M512,374c-76.1,0-138,61.9-138,138s61.9,138,138,138s138-61.9,138-138S588.1,374,512,374z" fill="white"/>
    <path d="M512,374c76.1,0,138,61.9,138,138s-61.9,138-138,138s-138-61.9-138-138S435.9,374,512,374 M512,332c-99.4,0-180,80.6-180,180s80.6,180,180,180s180-80.6,180-180S611.4,332,512,332L512,332z" fill="white"/>
  </svg>
);

interface LoginProps {
  isOpen: boolean;
  onClose: () => void;
}

const Login: React.FC<LoginProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const { login, register, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isWalletLoading, setIsWalletLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  if (!isOpen) return null;

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password) {
      setError(t('auth.emailPasswordRequired'));
      return;
    }

    if (isSignUp) {
      if (!name) {
        setError(t('auth.nameRequired'));
        return;
      }
      if (password !== confirmPassword) {
        setError(t('auth.passwordMismatch'));
        return;
      }
      if (password.length < 6) {
        setError(t('auth.passwordTooShort'));
        return;
      }
    }

    try {
      if (isSignUp) {
        await register(email, password, name);
      } else {
        await login(email, password);
      }
      onClose();
    } catch (err) {
      setError(isSignUp ? t('auth.signupFailed') : t('auth.loginFailed'));
    }
  };

  const handleSocialLogin = async (method: string) => {
    setError('');
    try {
      await login(method);
      onClose();
    } catch (error: any) {
      setError(error.message || t('auth.loginFailed'));
    }
  };

  const handleWalletLogin = async (walletType: string) => {
    setIsWalletLoading(true);
    setError('');
    try {
      await login(walletType);
      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Wallet connection failed';
      
      // Show more user-friendly error messages
      if (errorMessage.includes('not installed')) {
        if (walletType === 'coinbase') {
          setError('Coinbase Wallet is not installed. Please install it from https://wallet.coinbase.com/ and refresh the page.');
        } else if (walletType === 'metamask') {
          setError('MetaMask is not installed. Please install it from https://metamask.io/ and refresh the page.');
        } else if (walletType === 'phantom') {
          setError('Phantom Wallet is not installed. Please install it from https://phantom.app/ and refresh the page.');
        } else {
          setError(errorMessage);
        }
      } else {
        setError(errorMessage);
      }
    } finally {
      setIsWalletLoading(false);
    }
  };

  return (
    <LoginOverlay onClick={onClose}>
      <LoginModal onClick={(e) => e.stopPropagation()}>
        <CloseButton onClick={onClose}>
          <FaTimes />
        </CloseButton>
        
        <LoginTitle>{isSignUp ? t('auth.signUp') : t('auth.signIn')}</LoginTitle>

        {error && <ErrorMessage>{error}</ErrorMessage>}

        <LoginForm onSubmit={handleEmailAuth}>
          {isSignUp && (
            <InputGroup>
              <Label>{t('auth.name')}</Label>
              <Input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={t('auth.namePlaceholder')}
                disabled={isLoading}
              />
            </InputGroup>
          )}

          <InputGroup>
            <Label>{t('auth.email')}</Label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t('auth.emailPlaceholder')}
              disabled={isLoading}
            />
          </InputGroup>

          <InputGroup>
            <Label>{t('auth.password')}</Label>
            <PasswordInput>
              <Input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t('auth.passwordPlaceholder')}
                disabled={isLoading}
              />
              <PasswordToggle
                type="button"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </PasswordToggle>
            </PasswordInput>
          </InputGroup>

          {isSignUp && (
            <InputGroup>
              <Label>{t('auth.confirmPassword')}</Label>
              <PasswordInput>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder={t('auth.confirmPasswordPlaceholder')}
                  disabled={isLoading}
                />
              </PasswordInput>
            </InputGroup>
          )}

          <LoginButton type="submit" disabled={isLoading}>
            {isLoading ? t('common.loading') : (isSignUp ? t('auth.signUp') : t('auth.signInWithEmail'))}
          </LoginButton>

          <SwitchModeButton
            type="button"
            onClick={() => setIsSignUp(!isSignUp)}
            disabled={isLoading}
          >
            {isSignUp ? t('auth.alreadyHaveAccount') : t('auth.noAccount')}
          </SwitchModeButton>
        </LoginForm>

        <Divider>
          <span>{t('auth.orContinueWith')}</span>
        </Divider>

        <SocialButton
          onClick={() => handleSocialLogin('google')}
          disabled={isLoading}
        >
          <FaGoogle />
          {t('auth.continueWithGoogle')}
        </SocialButton>

        <SocialButton
          onClick={() => handleSocialLogin('apple')}
          disabled={isLoading}
        >
          <FaApple />
          {t('auth.continueWithApple')}
        </SocialButton>

        <WalletSection>
          <WalletTitle>{t('auth.web3Wallets')}</WalletTitle>
          
          <WalletButton
            onClick={() => handleWalletLogin('metamask')}
            disabled={isWalletLoading}
          >
            <MetaMaskIcon />
            {t('auth.connectMetaMask')}
          </WalletButton>

          <WalletButton
            onClick={() => handleWalletLogin('coinbase')}
            disabled={isWalletLoading}
          >
            <CoinbaseIcon />
            {t('auth.connectCoinbase')}
          </WalletButton>

          <PhantomButton
            onClick={() => handleWalletLogin('phantom')}
            disabled={isWalletLoading}
          >
            <PhantomIcon />
            {t('auth.connectPhantom')}
          </PhantomButton>
          
        </WalletSection>
      </LoginModal>
    </LoginOverlay>
  );
};

export default Login;
