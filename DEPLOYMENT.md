# Deployment Guide - Render.io

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`

### 3. Configure Environment Variables

The following environment variables will be created automatically from `render.yaml`:

- `GEMINI_API_KEY` - **You must set this manually** in the Render dashboard
- `DEFAULT_AI_PROVIDER` - Set to `gemini` (auto-configured)
- `DATABASE_URL` - Auto-populated from PostgreSQL database
- `PYTHON_VERSION` - Set to `3.10.0`

**To set GEMINI_API_KEY:**
1. Go to your service in Render Dashboard
2. Click **"Environment"**
3. Add `GEMINI_API_KEY` with your API key

### 4. Deploy

Render will automatically:
1. Create a PostgreSQL database
2. Install dependencies from `requirements.txt`
3. Run `build.sh` (migrations)
4. Start the web service with `uvicorn`

Your API will be available at: `https://your-service-name.onrender.com`

## Health Check

Test your deployment:

```bash
curl https://your-service-name.onrender.com/
```

## Database Access

View your PostgreSQL database:
1. Go to Render Dashboard
2. Click on your database (`ai-fitness-db`)
3. Use the connection string to connect via `psql` or GUI tools

## Continuous Deployment

Every push to `main` branch will automatically trigger a new deployment.

## Cost

- **Web Service**: Free tier (sleeps after inactivity)
- **PostgreSQL**: Free tier (90 days, then $7/month)

## Troubleshooting

### Build Fails
- Check build logs in Render Dashboard
- Verify all dependencies are in `requirements.txt`

### Service Crashes
- Check service logs in Render Dashboard
- Verify `GEMINI_API_KEY` is set correctly

### Database Connection Issues
- Ensure `DATABASE_URL` is properly linked in `render.yaml`
- Check database is running in Render Dashboard
