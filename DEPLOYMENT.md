# Deployment Guide - Aaditya E-Commerce Store

## 🚀 Deployment Files Created

I've prepared your application for deployment with the following files:

### 1. `netlify.toml` - Netlify Configuration
- Build commands configured
- Static files handling
- Redirect rules
- Environment variables setup

### 2. `.gitignore` - Git Ignore File
- Python/Django specific ignores
- Environment files
- Database files
- Static/Media files

### 3. `runtime.txt` - Python Version
- Python 3.11.9 specified

### 4. Updated `ecommerce/settings.py`
- Environment variable support for SECRET_KEY
- Dynamic DEBUG and ALLOWED_HOSTS settings
- Production-ready configuration

## 📋 Prerequisites for Manual Deployment

### Option 1: Deploy to Netlify (Recommended)

1. **Create a Netlify account** at https://app.netlify.com
2. **Install Netlify CLI** (optional but recommended):
   ```bash
   npm install netlify-cli -g
   ```
3. **Login to Netlify**:
   ```bash
   netlify login
   ```
4. **Initialize and deploy**:
   ```bash
   netlify init
   netlify deploy --prod
   ```

### Option 2: Deploy to Render/Railway/Heroku

These platforms support Django natively:

1. **Create account** on your chosen platform
2. **Connect your GitHub/GitLab repository**
3. **Set environment variables**:
   - `SECRET_KEY` - Generate a new secure key
   - `DEBUG` - Set to `False`
   - `DATABASE_URL` - Your database connection string
   - `ALLOWED_HOSTS` - Your domain names

### Option 3: Manual Server Deployment

1. **Get a VPS** (DigitalOcean, AWS, Linode)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```
4. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```
5. **Use Gunicorn** as the web server:
   ```bash
   gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000
   ```

## 🔐 Environment Variables Required

Create a `.env` file (don't commit this!):

```
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=your-database-url
```

To generate a new SECRET_KEY:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 📊 Current Deployment Status

Your project includes:
- ✅ Professional admin dashboard with analytics
- ✅ Email notification system
- ✅ Product import/export functionality
- ✅ Real-time notifications
- ✅ SEO features (sitemap)
- ✅ Voice search & commands
- ✅ AI chatbot
- ✅ Payment integration (Stripe/PayPal)
- ✅ User dashboard & address book
- ✅ Order tracking system

## 🌐 Local Testing

Before deploying, test locally:
```bash
python manage.py runserver
```

Access at: http://127.0.0.1:8000/

## 📞 Need Help?

If deployment fails:
1. Check the Netlify/Render dashboard for build logs
2. Ensure all environment variables are set
3. Verify `requirements.txt` has all dependencies
4. Check that `netlify.toml` is properly configured

## 🔗 Useful Links

- Netlify: https://docs.netlify.com/
- Django Deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/
- Gunicorn: https://gunicorn.org/
- Whitenoise (static files): https://whitenoise.readthedocs.io/
