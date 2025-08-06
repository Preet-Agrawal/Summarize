# Deploy Story Quiz to Render 🚀

## Prerequisites
- GitHub account with your code pushed
- MongoDB Atlas account (free tier works)
- Groq API key (get from https://console.groq.com)

## Quick Deploy Steps

### 1. Test Build Locally
```bash
# Test the build process locally
npm run build

# If successful, you'll see:
# ✅ Build complete for Render deployment
# ✅ All dependencies installed successfully
```

### 2. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 3. Deploy to Render

#### Create Render Account
1. Go to https://render.com
2. Sign up (free tier available)
3. Connect your GitHub account

#### Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Render will auto-detect settings from `render.yaml`

#### Environment Variables (Required)
Set these in Render Dashboard → Environment:

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/storyquiz` |
| `GROQ_API_KEY` | Groq API key for AI features | `gsk_xxxxxxxxxxxxx` |
| `SECRET_KEY` | Flask secret (auto-generated) | Let Render generate this |

#### Optional Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Set to production on Render |
| `MAIL_SERVER` | `smtp.gmail.com` | Email server for contact form |
| `MAIL_USERNAME` | None | Your email address |
| `MAIL_PASSWORD` | None | App-specific password |
| `MAIL_DEFAULT_SENDER` | None | From address for emails |
| `ADMIN_EMAIL` | None | Where to receive contact forms |

### 4. Deploy
- Click **"Create Web Service"**
- Render will automatically build and deploy
- Monitor deploy logs for progress
- Your app will be live at: `https://your-app-name.onrender.com`

## Deployment Configuration Files

| File | Purpose | Status |
|------|---------|--------|
| `render.yaml` | Render service configuration | ✅ Configured |
| `requirements.txt` | Python dependencies (11 packages) | ✅ Optimized |
| `render-build.sh` | Custom build script with verification | ✅ Ready |
| `package.json` | npm scripts for building | ✅ Configured |
| `runtime.txt` | Python version specification | ✅ Python 3.11 |
| `Procfile` | Process configuration | ✅ Gunicorn ready |
| `.env.example` | Environment variables template | ✅ Documented |

## npm Commands for Deployment

```bash
# Build for production
npm run build

# Check if build was successful
npm run build:check

# Run production server locally
npm run start:production
```

## Local Testing with Production Settings

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Test with Gunicorn
gunicorn app:app --bind 0.0.0.0:5000

# Or use npm
npm run start:production
```

## MongoDB Atlas Setup

### Quick Setup
1. Go to https://cloud.mongodb.com
2. Create free account & cluster
3. **Database Access**: Create user with password
4. **Network Access**: Add IP `0.0.0.0/0` (allows all IPs)
5. **Connect**: Get connection string
6. Replace `<password>` with your password
7. Add `/storyquiz` at the end for database name

## Troubleshooting

### Build Failed
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Run `npm run build` locally to test

### App Crashes
- Check runtime logs
- Verify MongoDB connection string
- Ensure all environment variables are set
- Check Groq API key is valid

### 502 Bad Gateway
- App may be starting up (wait 30 seconds)
- Check start command uses `$PORT`
- Verify Gunicorn is installed

## Important Notes

- **Free Tier**: Services sleep after 15 minutes of inactivity
- **First Request**: May take ~30 seconds after sleep
- **MongoDB**: Ensure connection string includes database name
- **API Keys**: Keep them secret, never commit to Git
- **Logs**: Available in Render dashboard for debugging

## Support

- Render Docs: https://render.com/docs
- Project Issues: GitHub repository
- MongoDB Atlas: https://docs.atlas.mongodb.com