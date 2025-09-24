# 🚀 Deploy AI Learning Platform to Render

This guide will help you deploy your AI Learning Platform to Render with both backend and frontend services.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be pushed to a GitHub repository
3. **OpenAI API Key**: Get your API key from [OpenAI](https://platform.openai.com/api-keys)

## 🔧 Deployment Steps

### Step 1: Push Your Code to GitHub

Make sure all your recent changes are committed and pushed:

```bash
git add .
git commit -m "Configure for Render deployment"
git push origin main  # or your main branch name
```

### Step 2: Deploy via Render Dashboard

#### Option A: Using render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Click **"Apply"** to deploy both services

#### Option B: Manual Service Creation

If you prefer to create services manually:

**Backend Service:**
1. Click **"New"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ai-learning-backend`
   - **Environment**: `Python 3.11`
   - **Build Command**: `python -m pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

**Frontend Service:**
1. Click **"New"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ai-learning-frontend`
   - **Build Command**: `cd frontend && npm install && REACT_APP_API_URL=https://ai-learning-backend.onrender.com npm run build`
   - **Publish Directory**: `frontend/build`

### Step 3: Create PostgreSQL Database

1. In Render Dashboard, click **"New"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `ai-learning-db`
   - **Database Name**: `ai_learning`
   - **User**: `ai_learning_user`
   - **Plan**: Free (or paid for production)

### Step 4: Configure Environment Variables

#### Backend Service Environment Variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | (Auto-generated from PostgreSQL) | Connection string |
| `OPENAI_API_KEY` | Your OpenAI API key | **Required** |
| `SECRET_KEY` | (Auto-generated) | For session security |
| `JWT_SECRET_KEY` | (Auto-generated) | For JWT tokens |
| `ENVIRONMENT` | `production` | |
| `FRONTEND_URL` | `https://ai-learning-frontend.onrender.com` | |
| `PYTHONUNBUFFERED` | `1` | |

#### Frontend Service Environment Variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `REACT_APP_API_URL` | `https://ai-learning-backend.onrender.com` | Backend URL |
| `REACT_APP_ENVIRONMENT` | `production` | |

### Step 5: Set Your OpenAI API Key

⚠️ **Important**: You must set your OpenAI API key manually:

1. Go to your backend service in Render Dashboard
2. Click **"Environment"** tab
3. Add environment variable:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: Your actual OpenAI API key
4. Click **"Save Changes"**

## 🌐 Access Your Deployed Application

Once deployment is complete:

- **Frontend**: `https://ai-learning-frontend.onrender.com`
- **Backend API**: `https://ai-learning-backend.onrender.com`
- **API Documentation**: `https://ai-learning-backend.onrender.com/docs`

## 🔍 Monitoring and Troubleshooting

### Check Deployment Status

1. Go to Render Dashboard
2. Check each service for:
   - ✅ **Deploy Status**: Should show "Live"
   - 📊 **Logs**: Check for any errors
   - 🔧 **Environment**: Verify all variables are set

### Common Issues and Solutions

#### 1. Backend Build Fails
- **Issue**: Missing dependencies
- **Solution**: Check `requirements.txt` includes all packages

#### 2. Database Connection Error
- **Issue**: Database not connected
- **Solution**: Verify `DATABASE_URL` is set from PostgreSQL service

#### 3. OpenAI API Errors
- **Issue**: API key not set or invalid
- **Solution**: Set `OPENAI_API_KEY` in backend environment variables

#### 4. CORS Errors
- **Issue**: Frontend can't connect to backend
- **Solution**: Verify frontend URL is in backend CORS origins

#### 5. Frontend Build Fails
- **Issue**: Missing environment variables
- **Solution**: Ensure `REACT_APP_API_URL` is set during build

### View Logs

To debug issues:
1. Go to your service in Render Dashboard
2. Click **"Logs"** tab
3. Check for error messages

## 🚀 Features Available After Deployment

Your deployed AI Learning Platform will include:

### ✅ Working Features:
- **User Authentication**: Email, social login (Google/Apple), Web3 wallets
- **AI Chat Practice**: Conversational learning with AI tutors
- **Translation Tool**: Real-time text translation
- **Language Games**: Interactive vocabulary and pronunciation games
- **Voice Conversation**: Speech-to-text practice (requires OpenAI API)
- **Lesson Generation**: AI-generated structured lessons
- **Progress Tracking**: User learning analytics
- **Multi-language Support**: 9 languages supported
- **Responsive Design**: Works on mobile and desktop

### 🔧 Post-Deployment Setup:

1. **Test Authentication**: Try signing up/logging in
2. **Verify AI Features**: Test chat, translation, and voice features
3. **Check Database**: Ensure user data is being saved
4. **Monitor Performance**: Watch for any slow responses

## 💡 Tips for Production

1. **Upgrade Plans**: Consider paid plans for better performance
2. **Custom Domain**: Add your own domain name
3. **SSL Certificate**: Render provides free SSL
4. **Environment Separation**: Use different services for staging/production
5. **Monitoring**: Set up alerts for service health

## 🔄 Updating Your Deployment

To update your deployed application:

1. Push changes to your GitHub repository
2. Render will automatically redeploy (if auto-deploy is enabled)
3. Or manually trigger a deploy from the Render Dashboard

## 📞 Support

If you encounter issues:
- Check [Render Documentation](https://render.com/docs)
- Review service logs in Render Dashboard
- Verify all environment variables are set correctly
- Ensure your OpenAI API key has sufficient credits

---

**🎉 Congratulations!** Your AI Learning Platform is now live on Render!
