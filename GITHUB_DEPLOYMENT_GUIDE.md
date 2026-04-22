# GitHub & Render Deployment Guide

## Step 1: Create GitHub Repository

### 1.1 Create Repository on GitHub
1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Repository name: `aaditya-store`
4. Description: `Complete e-commerce platform with AI features`
5. Make it **Public** (Render free tier requires public repos)
6. Don't initialize with README (we already have code)
7. Click "Create repository"

### 1.2 Push to GitHub
```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/aaditya-store.git

# Push to GitHub
git push -u origin master
```

## Step 2: Deploy to Render

### 2.1 Sign Up for Render
1. Go to [Render](https://render.com)
2. Click "Sign Up"
3. Choose "Continue with GitHub"
4. Authorize Render to access your GitHub account

### 2.2 Create Web Service
1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub account
4. Select the `aaditya-store` repository
5. Configure settings:
   - **Name**: `aaditya-store`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `master`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn ecommerce.wsgi:application`

### 2.3 Environment Variables
Render will automatically read from `render.yaml`, but verify these:
```
PYTHON_VERSION=3.11
DJANGO_SETTINGS_MODULE=ecommerce.settings
SECRET_KEY=auto-generated
DEBUG=false
DATABASE_URL=auto-generated
ALLOWED_HOSTS=aaditya-store.onrender.com,localhost,127.0.0.1
USE_POSTGRESQL=true
```

### 2.4 Create Database
1. Click "New +" again
2. Select "PostgreSQL"
3. **Name**: `aaditya-store-db`
4. **Region**: Same as your web service
5. **Database Name**: `aaditya_store_db`
6. **User**: `postgres`
7. Click "Create Database"

### 2.5 Connect Database to Web Service
1. Go back to your web service
2. Scroll down to "Environment Variables"
3. Find `DATABASE_URL` variable
4. Click "Connect Database"
5. Select your `aaditya-store-db` database

## Step 3: Deploy and Test

### 3.1 Automatic Deployment
- Render will automatically deploy when you push to GitHub
- Wait for the build to complete (usually 2-5 minutes)
- Check the deployment logs for any errors

### 3.2 Run Migrations
After deployment, you need to run database migrations:
1. Go to your web service on Render
2. Click "Shell" tab
3. Run: `python manage.py migrate`
4. Run: `python manage.py createsuperuser` (create admin user)

### 3.3 Test Your Live Site
Your site will be available at: `https://aaditya-store.onrender.com`

Test these features:
- [ ] Homepage loads correctly
- [ ] Product catalog works
- [ ] User registration/login
- [ ] Shopping cart functionality
- [ ] About us page (with your image)
- [ ] Mobile responsiveness

## Step 4: Post-Deployment Setup

### 4.1 Configure Email (Optional)
Add these environment variables on Render:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4.2 Configure Payment (Optional)
Add payment keys:
```
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 4.3 Custom Domain (Optional)
1. Go to your web service settings
2. Click "Custom Domains"
3. Add your domain name
4. Update DNS settings as instructed

## Troubleshooting

### Common Issues:

#### 1. Build Fails
- Check requirements.txt for correct dependencies
- Verify Python version compatibility
- Check the build logs for specific errors

#### 2. Database Connection Error
- Ensure DATABASE_URL is correctly set
- Verify database is running
- Run migrations manually in shell

#### 3. Static Files Not Loading
- Run `python manage.py collectstatic` in shell
- Check STATIC_URL and STATIC_ROOT settings
- Verify Whitenoise middleware is properly configured

#### 4. 500 Internal Server Error
- Check Render logs for error details
- Ensure all environment variables are set
- Verify Django settings are correct for production

### Getting Help:
- Render docs: https://render.com/docs
- Django deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/
- Contact Render support: https://render.com/support

## Final Steps

Once deployed:
1. **Test thoroughly** - Check all features work
2. **Monitor performance** - Check Render dashboard
3. **Set up monitoring** - Enable error notifications
4. **Backup data** - Regular database backups
5. **Update regularly** - Keep dependencies updated

Your **Aaditya Store** will be live at: `https://aaditya-store.onrender.com`!
