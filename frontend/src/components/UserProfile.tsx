import React, { useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { FaUser, FaSignOutAlt, FaChevronDown } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

const ProfileContainer = styled.div`
  position: relative;
`;

const ProfileButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 8px 16px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
  }
`;

const Avatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
`;

const UserName = styled.span`
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const Dropdown = styled.div<{ isOpen: boolean }>`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  opacity: ${props => props.isOpen ? 1 : 0};
  visibility: ${props => props.isOpen ? 'visible' : 'hidden'};
  transform: ${props => props.isOpen ? 'translateY(0)' : 'translateY(-10px)'};
  transition: all 0.2s ease;
  z-index: 1000;
`;

const DropdownItem = styled.button`
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: none;
  border: none;
  color: #4a5568;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;

  &:first-child {
    border-radius: 12px 12px 0 0;
  }

  &:last-child {
    border-radius: 0 0 12px 12px;
  }

  &:hover {
    background: #f7fafc;
  }
`;

const UserInfo = styled.div`
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
`;

const UserEmail = styled.div`
  font-size: 12px;
  color: #718096;
  margin-top: 4px;
`;

const AuthMethod = styled.div`
  font-size: 11px;
  color: #a0aec0;
  margin-top: 2px;
  text-transform: uppercase;
`;

const UserProfile: React.FC = () => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  if (!user) return null;

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleLogout = () => {
    logout();
    setIsDropdownOpen(false);
  };

  return (
    <ProfileContainer>
      <ProfileButton
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
      >
        <Avatar>
          {user.avatar ? (
            <img 
              src={user.avatar} 
              alt={user.name}
              style={{ width: '100%', height: '100%', borderRadius: '50%' }}
            />
          ) : (
            getInitials(user.name)
          )}
        </Avatar>
        <UserName>{user.name}</UserName>
        <FaChevronDown 
          style={{ 
            transform: isDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s'
          }} 
        />
      </ProfileButton>

      <Dropdown isOpen={isDropdownOpen}>
        <UserInfo>
          <div style={{ fontWeight: 600, color: '#2d3748' }}>{user.name}</div>
          {user.email && <UserEmail>{user.email}</UserEmail>}
          {user.walletAddress && (
            <UserEmail>
              {user.walletAddress.slice(0, 6)}...{user.walletAddress.slice(-4)}
            </UserEmail>
          )}
          <AuthMethod>{user.authMethod}</AuthMethod>
        </UserInfo>
        
        <DropdownItem onClick={() => setIsDropdownOpen(false)}>
          <FaUser />
          {t('auth.profile')}
        </DropdownItem>
        
        <DropdownItem onClick={handleLogout}>
          <FaSignOutAlt />
          {t('auth.signOut')}
        </DropdownItem>
      </Dropdown>
    </ProfileContainer>
  );
};

export default UserProfile;
