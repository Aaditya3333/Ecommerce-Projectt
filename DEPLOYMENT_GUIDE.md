# Render Deployment Guide for Aaditya Store

This guide will help you deploy your e-commerce website to Render.com.

## Prerequisites

1. **Render Account**: Create a free account at [render.com](https://render.com)
2. **GitHub Account**: Your code should be pushed to a GitHub repository
3. **Payment Method**: Add a payment method to Render (required for PostgreSQL)

## Step 1: Prepare Your Project

### Files Already Created:
- `render.yaml` - Render configuration file
- `requirements.txt` - Python dependencies
- `Procfile` - Process configuration
- `.env.example` - Environment variables template

### Push to GitHub:
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

## Step 2: Deploy to Render

### 1. Connect GitHub to Render
1. Go to [render.com](https://render.com)
2. Click "New" -> "Web Service"
3. Connect your GitHub account
4. Select your e-commerce repository

### 2. Configure Web Service
1. **Name**: `aaditya-store`
2. **Environment**: `Python 3`
3. **Branch**: `main`
4. **Root Directory**: Leave empty (root of repo)
5. **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
6. **Start Command**: `gunicorn ecommerce.wsgi:application`
7. **Instance Type**: `Free` (to start)

### 3. Add Environment Variables
In the "Environment" section, add these variables:

#### Required Variables:
```
SECRET_KEY=your-very-secret-key-here
DEBUG=False
ALLOWED_HOSTS=aaditya-store.onrender.com,localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=ecommerce.settings
```

#### Database Variables (Render provides automatically):
```
DATABASE_URL=postgresql://[auto-generated-by-render]
```

#### Optional Variables:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Create PostgreSQL Database
1. Click "New" -> "PostgreSQL"
2. **Name**: `aaditya-store-db`
3. **Database Name**: `aaditya_store_db`
4. **User**: `postgres`
5. **Region**: Choose closest to your users
6. **Plan**: `Free` (to start)

### 5. Connect Database to Web Service
1. Go to your web service settings
2. Scroll to "Environment"
3. Add `DATABASE_URL` variable
4. Click "Connect" next to your database
5. Select "Connection String" as the value

## Step 3: Deploy and Test

### 1. Initial Deployment
1. Click "Create Web Service"
2. Wait for build to complete (5-10 minutes)
3. Check the logs for any errors

### 2. Run Database Migrations
After deployment, you'll need to run migrations:
1. Go to your web service dashboard
2. Click "Shell" tab
3. Run these commands:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 3. Create Superuser
When prompted for superuser creation:
- Username: `admin`
- Email: `admin@example.com`
- Password: Choose a strong password

### 4. Test Your Site
1. Visit your site: `https://aaditya-store.onrender.com`
2. Go to admin: `https://aaditya-store.onrender.com/admin/`
3. Login with your superuser credentials

## Step 4: Post-Deployment Setup

### 1. Add Categories and Products
1. Go to `/admin/`
2. Add categories under "Categories"
3. Add products under "Products"

### 2. Configure Email (Optional)
Add these environment variables for email functionality:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. Set Up Payment Gateway (Optional)
For Stripe payments:
```
STRIPE_PUBLISHABLE_KEY=pk_test_your-key
STRIPE_SECRET_KEY=sk_test_your-key
```

## Troubleshooting

### Common Issues:

#### 1. Build Fails
- Check `requirements.txt` for syntax errors
- Ensure all dependencies are compatible
- Check the build logs for specific errors

#### 2. Database Connection Error
- Verify `DATABASE_URL` is set correctly
- Check if database is running
- Ensure database and web service are in same region

#### 3. Static Files Not Loading
- Run `python manage.py collectstatic --noinput` in shell
- Check `STATIC_URL` and `STATIC_ROOT` settings
- Verify file permissions

#### 4. 500 Internal Server Error
- Check application logs
- Verify `DEBUG=False` in production
- Ensure all environment variables are set

#### 5. Migration Issues
- Run `python manage.py makemigrations` first
- Then run `python manage.py migrate`
- Check for model field conflicts

### Getting Help:
1. Check Render dashboard logs
2. Use Render's shell for debugging
3. Review Django error messages
4. Check environment variables

## Advanced Configuration

### Custom Domain
1. Upgrade to paid plan
2. Add custom domain in Render dashboard
3. Update DNS records
4. Update `ALLOWED_HOSTS` in settings

### SSL Certificate
Render provides free SSL certificates automatically for all services.

### Monitoring
1. Use Render's built-in metrics
2. Set up error logging
3. Monitor database performance

### Scaling
1. Upgrade to paid plan for more resources
2. Add web service instances
3. Optimize database performance

## Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **DEBUG Mode**: Always set `DEBUG=False` in production
3. **Strong Passwords**: Use strong admin passwords
4. **Regular Updates**: Keep dependencies updated
5. **Backups**: Enable database backups in Render

## Performance Optimization

1. **Static Files**: Use CDN for static assets
2. **Database**: Add indexes for frequently queried fields
3. **Caching**: Enable Redis caching if needed
4. **Images**: Optimize images for web

## Support

- Render Documentation: [render.com/docs](https://render.com/docs)
- Django Documentation: [docs.djangoproject.com](https://docs.djangoproject.com)
- Community Forums: Render and Django communities

## Next Steps

After successful deployment:
1. Test all features thoroughly
2. Set up monitoring and alerts
3. Configure backup strategies
4. Plan for scaling as traffic grows
5. Set up CI/CD pipeline for updates

Your e-commerce site is now live on Render! Congratulations!
