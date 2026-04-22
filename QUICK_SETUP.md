# Quick GitHub Repository Setup

## Step 1: Create GitHub Repository (2 minutes)

1. **Go to GitHub**: https://github.com/Aaditya3333
2. **Click "New repository"** (green button on the right)
3. **Repository settings**:
   - Repository name: `aaditya-store`
   - Description: `Complete e-commerce platform with AI features`
   - Choose **Public** (required for Render free tier)
   - Don't initialize with README, license, or .gitignore
4. **Click "Create repository"**

## Step 2: Push Your Code (30 seconds)

Once the repository is created, run these commands:

```bash
git remote add origin https://github.com/Aaditya3333/aaditya-store.git
git push -u origin master
```

## Step 3: Deploy to Render (5 minutes)

1. **Go to Render**: https://render.com
2. **Click "Sign Up"** and choose "Continue with GitHub"
3. **Authorize** Render to access your GitHub account
4. **Click "New +"** then select "Web Service"
5. **Connect your repository**: Select `aaditya-store`
6. **Configure settings**:
   - Name: `aaditya-store`
   - Region: Oregon (or closest to you)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn ecommerce.wsgi:application`
7. **Click "Create Web Service"**

## Step 4: Create Database (2 minutes)

1. **Click "New +"** again
2. **Select "PostgreSQL"**
3. **Settings**:
   - Name: `aaditya-store-db`
   - Region: Same as your web service
   - Database Name: `aaditya_store_db`
   - User: `postgres`
4. **Click "Create Database"**

## Step 5: Connect Database (1 minute)

1. **Go back to your web service**
2. **Scroll down to "Environment Variables"**
3. **Find DATABASE_URL** and click "Connect Database"
4. **Select your `aaditya-store-db` database**

## Step 6: Final Setup (2 minutes)

After deployment, run migrations:
1. **Go to your web service on Render**
2. **Click "Shell" tab**
3. **Run**: `python manage.py migrate`
4. **Run**: `python manage.py createsuperuser`

## Your Live Site!

Your site will be available at: **https://aaditya-store.onrender.com**

## Total Time: ~12 minutes

That's it! Your complete e-commerce platform will be live!
