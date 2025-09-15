# Render Deployment Guide for Newsletter Generation App

## 📋 Prerequisites

Before deploying to Render, ensure you have:

1. ✅ A GitHub account
2. ✅ A Render account (sign up at https://render.com)
3. ✅ Your repository pushed to GitHub
4. ✅ API keys ready (EXA_API_KEY and GOOGLE_API_KEY)

## 🚀 Step-by-Step Deployment Process

### Step 1: Prepare Your Repository

1. **Commit all changes to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

### Step 2: Create a New Web Service on Render

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Click "New +" button
   - Select "Web Service"

2. **Connect GitHub Repository:**
   - Click "Connect" next to your GitHub account
   - Find and select your `NewsLetterGenerationUsingCrewAI` repository
   - Click "Connect"

### Step 3: Configure Service Settings

**Basic Settings:**
- **Name:** `newsletter-gen` (or your preferred name)
- **Environment:** `Python 3`
- **Region:** Choose closest to your users
- **Branch:** `main`

**Build & Deploy Settings:**
- **Build Command:** `poetry install`
- **Start Command:** `poetry run streamlit run src/gui/app.py --server.port $PORT --server.address 0.0.0.0`

**Advanced Settings:**
- **Auto-Deploy:** `Yes` (recommended)

### Step 4: Set Environment Variables

In the Render dashboard, add these environment variables:

1. **EXA_API_KEY**
   - Value: `67c8e473-3062-48e1-810e-ab2987b6137a`

2. **GOOGLE_API_KEY**
   - Value: `AIzaSyDJhsySR_JqrVNns8dbY7vZVUNK-4EEVL0`

3. **GROQ_API_KEY** (optional, for backup)
   - Value: Your Groq API key if you have one

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically start building and deploying your app
3. The process typically takes 5-10 minutes

## 📁 Required Files (Already Present)

Your repository already contains the necessary files:

- ✅ `render.yaml` - Render configuration
- ✅ `pyproject.toml` - Poetry dependencies
- ✅ `poetry.lock` - Locked dependencies
- ✅ `.env` - Environment variables (for local development)
- ✅ Application code in `src/`

## 🔧 Troubleshooting

### Common Issues and Solutions:

1. **Build Fails:**
   - Check that `pyproject.toml` has correct Python version
   - Ensure all dependencies are properly specified

2. **App Doesn't Start:**
   - Verify the start command includes proper Streamlit parameters
   - Check environment variables are set correctly

3. **Port Issues:**
   - Render automatically provides the `$PORT` environment variable
   - Streamlit must bind to `0.0.0.0:$PORT`

4. **API Key Issues:**
   - Double-check environment variable names match your code
   - Ensure API keys are valid and have proper permissions

### Monitoring Deployment:

1. **View Logs:**
   - Go to your service dashboard
   - Click on "Logs" tab to see real-time deployment logs

2. **Check Service Status:**
   - Green dot = Running successfully
   - Yellow = Building/Deploying
   - Red = Failed (check logs)

## 🌐 Post-Deployment

Once deployed successfully:

1. **Test Your App:**
   - Click on your service URL (e.g., `https://newsletter-gen.onrender.com`)
   - Try generating a newsletter to ensure everything works

2. **Share Your App:**
   - Your app will have a public URL
   - You can share this with users or embed it in your website

## 🔄 Updates and Maintenance

**Automatic Deployments:**
- Any push to your `main` branch will trigger automatic redeployment
- Render will rebuild and deploy your changes automatically

**Manual Deployment:**
- You can also manually trigger deployments from the Render dashboard

## 💡 Performance Tips

1. **Resource Allocation:**
   - Free tier has limitations (750 hours/month)
   - Consider upgrading for production use

2. **Cold Starts:**
   - Free tier services may experience cold starts
   - First request after inactivity may be slower

3. **Monitoring:**
   - Use Render's built-in monitoring
   - Set up alerts for service failures

## 🔐 Security Best Practices

1. **Environment Variables:**
   - Never commit API keys to your repository
   - Use Render's environment variable settings

2. **HTTPS:**
   - Render provides HTTPS by default
   - Your app will be accessible via secure connection

## 📞 Support

If you encounter issues:
- Check Render's documentation: https://render.com/docs
- Visit Render's community: https://community.render.com
- Check the application logs in Render dashboard

---

**Your app should be live at:** `https://newsletter-gen.onrender.com` (or your chosen name)

Good luck with your deployment! 🚀
