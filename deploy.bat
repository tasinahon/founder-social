@echo off
REM Quick Deploy Script for Founder Socials AI Agent (Windows)

echo 🚀 Founder Socials AI Agent - Quick Deploy
echo ==========================================

REM Check if git is initialized
if not exist ".git" (
    echo 📝 Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit"
)

echo.
echo 🎯 Choose your deployment platform:
echo 1. Railway (Recommended - Easy with database)
echo 2. Render (Free tier available)  
echo 3. Vercel (Serverless)
echo 4. Manual Docker deployment
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🚂 Railway Deployment Selected
    echo ===============================
    echo.
    echo 📋 Next steps:
    echo 1. Push your code to GitHub:
    echo    git remote add origin https://github.com/yourusername/founder-socials
    echo    git push -u origin main
    echo.
    echo 2. Go to https://railway.app
    echo 3. Click 'Deploy from GitHub repo'
    echo 4. Select your repository
    echo 5. Set environment variables in Railway dashboard:
    echo    - OPENAI_API_KEY=your_key
    echo    - AZURE_OPENAI_API_KEY=your_key
    echo    - AZURE_OPENAI_ENDPOINT=your_endpoint
    echo    - PORT=8000
    echo.
    echo ✅ Railway will automatically detect the Dockerfile and deploy!
) else if "%choice%"=="2" (
    echo.
    echo 🎨 Render Deployment Selected
    echo =============================
    echo.
    echo 📋 Next steps:
    echo 1. Push your code to GitHub
    echo 2. Go to https://render.com
    echo 3. Create new 'Web Service'
    echo 4. Connect your GitHub repo
    echo 5. Use these settings:
    echo    Build Command: pip install -r requirements.txt
    echo    Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
    echo.
    echo ✅ Render will build and deploy your app!
) else if "%choice%"=="3" (
    echo.
    echo ⚡ Vercel Deployment Selected
    echo ============================
    echo.
    echo 📋 Next steps:
    echo 1. Install Vercel CLI: npm i -g vercel
    echo 2. Run: vercel
    echo 3. Follow the prompts
    echo.
    echo ⚠️  Note: Vercel has execution time limits for serverless functions
) else if "%choice%"=="4" (
    echo.
    echo 🐳 Docker Deployment Selected
    echo =============================
    echo.
    echo Building Docker image...
    docker build -t founder-socials .
    
    if %errorlevel%==0 (
        echo ✅ Docker image built successfully!
        echo.
        echo 📋 To run the container:
        echo docker run -p 8000:8000 --env-file .env founder-socials
        echo.
        echo 📋 To push to a registry:
        echo docker tag founder-socials your-registry/founder-socials
        echo docker push your-registry/founder-socials
    ) else (
        echo ❌ Docker build failed. Check the Dockerfile and try again.
    )
) else (
    echo ❌ Invalid choice. Please run the script again.
    exit /b 1
)

echo.
echo 📚 For detailed instructions, see DEPLOYMENT.md
echo 🆘 Need help? Check the troubleshooting section in DEPLOYMENT.md
echo.
echo 🎉 Happy deploying!

pause
