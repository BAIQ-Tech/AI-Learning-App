import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  color: #2d3748;
  line-height: 1.7;
`;

const Title = styled.h1`
  font-size: 28px;
  margin-bottom: 12px;
`;

const Subtitle = styled.p`
  color: #718096;
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 20px;
  margin-top: 20px;
  margin-bottom: 8px;
`;

const PrivacyPolicy: React.FC = () => {
  const updated = new Date().toISOString().slice(0, 10);
  return (
    <Container>
      <Title>Privacy Policy</Title>
      <Subtitle>Last updated: {updated}</Subtitle>

      <p>
        This Privacy Policy describes how the AI Learning App ("we", "our", or "us") collects, uses, and shares your
        information when you use our application and services.
      </p>

      <SectionTitle>1. Information We Collect</SectionTitle>
      <p>
        - Account information you provide (e.g., email or wallet address if you choose to sign in).
        <br />- Usage data (e.g., interactions within the app, selected languages).
        <br />- Audio data only when you use voice features (processed for transcription and pronunciation feedback).
      </p>

      <SectionTitle>2. How We Use Information</SectionTitle>
      <p>
        We use your information to provide and improve app functionality, personalize learning content, enable
        authentication, and ensure service reliability and security.
      </p>

      <SectionTitle>3. Data Sharing</SectionTitle>
      <p>
        We do not sell your personal information. We may share data with service providers strictly to operate core
        features (e.g., speech recognition) under appropriate agreements.
      </p>

      <SectionTitle>4. Your Choices</SectionTitle>
      <p>
        You can manage permissions (e.g., microphone, camera) via your device settings. You may request data deletion by
        contacting support.
      </p>

      <SectionTitle>5. Children’s Privacy</SectionTitle>
      <p>
        Our app is intended for general audiences. If you believe a child has provided us information without consent,
        please contact us to remove it.
      </p>

      <SectionTitle>6. Contact Us</SectionTitle>
      <p>
        Support Email: support@example.com
        <br />Company: AI Learning
      </p>
    </Container>
  );
};

export default PrivacyPolicy;
