# AI Learning App

A comprehensive multilingual AI-powered language learning platform with advanced authentication, interactive features, and real-time translation capabilities.

## 🌍 Supported Languages
- **English** (English)
- **Japanese** (日本語)
- **Chinese** (中文)
- **Spanish** (Español)
- **Greek** (Ελληνικά)
- **Hebrew** (עברית)
- **German** (Deutsch)
- **French** (Français)
- **Italian** (Italiano)

## ✨ Features

### 🔐 Authentication
- **Email/Password** authentication with registration
- **Web3 Wallet** integration (MetaMask, Coinbase Wallet, Phantom)
- **Social Login** (Google OAuth, Apple Sign-In ready)
- **JWT-based** session management with 7-day expiration
- **Secure** password hashing and token validation

### 🎯 Core Learning Features
- **AI Chat** - Conversational practice with GPT-powered responses
- **Voice Practice** - Speech recognition and pronunciation feedback
- **Translation Tool** - Real-time text translation between all supported languages
- **Language Games** - Interactive learning exercises
- **Lessons** - Structured learning content
- **News** - Language learning through current events

### 🛠 Technical Features
- **Multilingual UI** - Complete translations for all 9 languages
- **Responsive Design** - Modern, mobile-friendly interface
- **Real-time API** - Fast backend responses with proper error handling
- **Session Persistence** - Automatic login state management
- **Protected Routes** - Secure access to authenticated features

## 🚀 Tech Stack

### Frontend
- **React 18** with TypeScript
- **React Router** for navigation
- **Styled Components** for styling
- **React i18next** for internationalization
- **Axios** for API communication
- **Web3** wallet integration

### Backend
- **FastAPI** with Python 3.9+
- **SQLite** database with SQLAlchemy
- **JWT** authentication with PyJWT
- **OpenAI GPT-3.5-turbo** for AI responses
- **CORS** middleware for cross-origin requests
- **Uvicorn** ASGI server

## 📋 Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.9+
- **OpenAI API Key** (for AI features)

## 🛠 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AI-Learning
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
echo "JWT_SECRET_KEY=your_jwt_secret_key_here" >> .env

# Start the backend server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start the frontend development server
npm start
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🏗 Project Structure
```
AI-Learning/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts (Auth, Language)
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service layer
│   │   └── locales/        # Translation files
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── backend/                 # FastAPI Python backend
│   ├── main.py            # Main application file
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example      # Environment variables template
│   └── *.db              # SQLite database files
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── start.sh             # Quick start script
```

## 🔧 Environment Variables

### Backend (.env)
```bash
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
```

## 🚀 Quick Start Script
```bash
# Make the start script executable
chmod +x start.sh

# Run both frontend and backend
./start.sh
```

## 📱 Usage

1. **Sign Up/Login** - Create an account or sign in with email, wallet, or social auth
2. **Select Language** - Choose your target learning language from 9 options
3. **Start Learning** - Access chat, voice practice, translation, games, and lessons
4. **Track Progress** - Monitor your learning journey and achievements

## 🔒 Security Features

- **JWT Authentication** with secure token management
- **Password Hashing** using industry-standard algorithms
- **Protected API Endpoints** requiring valid authentication
- **CORS Configuration** for secure cross-origin requests
- **Environment Variable Protection** for sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, email support@ai-learning.com or create an issue in the GitHub repository.

---

**Built with ❤️ using React, FastAPI, and OpenAI**
