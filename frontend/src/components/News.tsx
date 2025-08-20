import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { FaNewspaper, FaExternalLinkAlt, FaClock, FaSyncAlt } from 'react-icons/fa';

const NewsContainer = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const NewsHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
`;

const NewsTitle = styled.h2`
  color: #2d3748;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
`;

const RefreshButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  transition: all 0.2s;

  &:hover {
    background: #5a67d8;
    transform: translateY(-1px);
  }

  &:disabled {
    background: #a0aec0;
    cursor: not-allowed;
    transform: none;
  }
`;

const NewsGrid = styled.div`
  display: grid;
  gap: 20px;
`;

const NewsCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e1e5e9;
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    border-color: #667eea;
  }
`;

const NewsCardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const NewsSource = styled.span`
  background: #667eea;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
`;

const NewsTime = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: #718096;
  font-size: 12px;
`;

const NewsTitle2 = styled.h3`
  color: #2d3748;
  margin: 0 0 8px 0;
  font-size: 18px;
  line-height: 1.4;
`;

const NewsDescription = styled.p`
  color: #4a5568;
  margin: 0 0 12px 0;
  line-height: 1.5;
  font-size: 14px;
`;

const NewsLink = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  color: #667eea;
  font-size: 14px;
  font-weight: 500;
`;

const LoadingState = styled.div`
  text-align: center;
  padding: 40px;
  color: #718096;
`;

const ErrorState = styled.div`
  text-align: center;
  padding: 40px;
  color: #e53e3e;
  background: #fed7d7;
  border-radius: 8px;
  margin: 20px 0;
`;

interface NewsArticle {
  title: string;
  description: string;
  url: string;
  source: string;
  publishedAt: string;
  urlToImage?: string;
}

const News: React.FC = () => {
  const { t } = useTranslation();
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchNews = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Using NewsAPI.org - you'll need to get a free API key
      const API_KEY = 'cae6d7a7a65448c0990d9efdff85e6d7'; // Replace with actual API key
      const response = await fetch(
        `https://newsapi.org/v2/top-headlines?country=us&pageSize=10&apiKey=${API_KEY}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch news');
      }
      
      const data = await response.json();
      
      if (data.status === 'ok') {
        setNews(data.articles.map((article: any) => ({
          title: article.title,
          description: article.description,
          url: article.url,
          source: article.source.name,
          publishedAt: article.publishedAt,
          urlToImage: article.urlToImage
        })));
      } else {
        throw new Error(data.message || 'Failed to fetch news');
      }
    } catch (error) {
      console.error('Error fetching news:', error);
      // Fallback to mock data for demo purposes
      setNews([
        {
          title: "AI Technology Advances in Language Learning",
          description: "New developments in artificial intelligence are revolutionizing how people learn languages worldwide.",
          url: "#",
          source: "Tech News",
          publishedAt: new Date().toISOString()
        },
        {
          title: "Global Education Trends 2024",
          description: "Educational institutions worldwide are adopting new technologies to enhance learning experiences.",
          url: "#",
          source: "Education Today",
          publishedAt: new Date(Date.now() - 3600000).toISOString()
        },
        {
          title: "Multilingual Communication in Business",
          description: "Companies are investing in language training programs to improve international communication.",
          url: "#",
          source: "Business Weekly",
          publishedAt: new Date(Date.now() - 7200000).toISOString()
        },
        {
          title: "Digital Learning Platforms Growth",
          description: "Online learning platforms see unprecedented growth as more people embrace digital education.",
          url: "#",
          source: "Digital Trends",
          publishedAt: new Date(Date.now() - 10800000).toISOString()
        },
        {
          title: "Language Exchange Programs Expand",
          description: "International language exchange programs are helping students connect across cultures.",
          url: "#",
          source: "Cultural Exchange",
          publishedAt: new Date(Date.now() - 14400000).toISOString()
        }
      ]);
      setError('Using demo news data. To get real news, please configure NewsAPI key.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return t('news.justNow');
    } else if (diffInHours < 24) {
      return t('news.hoursAgo', { hours: diffInHours });
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return t('news.daysAgo', { days: diffInDays });
    }
  };

  const handleNewsClick = (url: string) => {
    if (url !== '#') {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <NewsContainer>
      <NewsHeader>
        <NewsTitle>
          <FaNewspaper />
          {t('news.title')}
        </NewsTitle>
        <RefreshButton onClick={fetchNews} disabled={loading}>
          <FaSyncAlt />
          {t('news.refresh')}
        </RefreshButton>
      </NewsHeader>

      {error && (
        <ErrorState>
          {error}
        </ErrorState>
      )}

      {loading ? (
        <LoadingState>
          {t('common.loading')}
        </LoadingState>
      ) : (
        <NewsGrid>
          {news.map((article, index) => (
            <NewsCard key={index} onClick={() => handleNewsClick(article.url)}>
              <NewsCardHeader>
                <NewsSource>{article.source}</NewsSource>
                <NewsTime>
                  <FaClock />
                  {formatTime(article.publishedAt)}
                </NewsTime>
              </NewsCardHeader>
              <NewsTitle2>{article.title}</NewsTitle2>
              {article.description && (
                <NewsDescription>{article.description}</NewsDescription>
              )}
              <NewsLink>
                {t('news.readMore')}
                <FaExternalLinkAlt />
              </NewsLink>
            </NewsCard>
          ))}
        </NewsGrid>
      )}
    </NewsContainer>
  );
};

export default News;
