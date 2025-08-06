# Deploy to Render

## Steps to Deploy

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create a Render account**
   - Go to https://render.com and sign up

3. **Create a new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the configuration from `render.yaml`

4. **Set Environment Variables**
   In the Render dashboard, add these environment variables:
   - `MONGO_URI`: Your MongoDB connection string
   - `HUGGINGFACE_API_KEY`: Your Hugging Face API key (optional)
   - `SECRET_KEY`: Will be auto-generated if using render.yaml

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

## Files Configured for Deployment

- ✅ `requirements.txt` - Python dependencies
- ✅ `render.yaml` - Render configuration
- ✅ `build.sh` - Build script
- ✅ `app.py` - Updated to use environment variables
- ✅ `.env.example` - Environment variables template
- ✅ `gunicorn` - Production WSGI server (in requirements.txt)

## Local Testing

To test locally with production settings:
```bash
pip install -r requirements.txt
gunicorn app:app --bind 0.0.0.0:5000
```

## Important Notes

- The app uses MongoDB, so ensure your `MONGO_URI` is set correctly
- The SECRET_KEY will be auto-generated on Render for security
- Free tier on Render spins down after inactivity, first request may be slow