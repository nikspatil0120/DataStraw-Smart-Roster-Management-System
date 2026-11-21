# 🚀 DataStraw Deployment Guide

## Quick Deployment Options

### Option 1: Railway (Recommended - 5 minutes)

**Advantages**:
- ✅ One-click deployment from GitHub
- ✅ Free tier available ($5/month credit)
- ✅ Automatic SSL/HTTPS
- ✅ Database included (PostgreSQL)
- ✅ Auto-deployments on git push

**Steps**:

1. **Visit Railway.app**:
   - Go to https://railway.app
   - Click "Start New Project"
   - Select "GitHub Repo"
   - Connect your GitHub account

2. **Select Your Repository**:
   - Choose: `nikspatil0120/DataStraw-Smart-Roster-Management-System`
   - Click "Deploy Now"

3. **Configure Environment**:
   Railway will auto-detect services. Add these variables in Project Settings:

   **Backend Service**:
   ```
   DATABASE_URL=postgresql://[user]:[password]@[host]:5432/datastraw
   SECRET_KEY=your-production-secret-key
   ENVIRONMENT=production
   DEBUG=false
   ALLOWED_ORIGINS=https://your-app.railway.app,https://your-frontend-domain.com
   ```

   **Frontend Service**:
   ```
   VITE_API_URL=https://your-api-domain.railway.app
   VITE_APP_NAME=DataStraw Smart Roster
   ```

4. **Database Setup**:
   - Railway auto-creates PostgreSQL
   - Run migrations automatically or manually via SSH
   - Seed data with: `python scripts/seed_data.py`

5. **Deploy**:
   - Click "Deploy"
   - Wait for all services (usually 2-5 minutes)
   - Get your public URL

6. **Access Your App**:
   ```
   Frontend: https://your-app.railway.app
   API: https://api.your-app.railway.app
   Docs: https://api.your-app.railway.app/docs
   ```

---

### Option 2: Render (5-10 minutes)

**Advantages**:
- ✅ Free tier with 750 hours/month
- ✅ GitHub integration
- ✅ Automatic deployments
- ✅ PostgreSQL database included

**Steps**:

1. **Visit Render.com**:
   - Go to https://render.com
   - Click "New +"
   - Select "Web Service"

2. **Connect Repository**:
   - Connect GitHub account
   - Select: `DataStraw-Smart-Roster-Management-System`
   - Choose branch: `main`

3. **Configure Service**:
   ```
   Name: datastraw-backend
   Environment: Docker
   Region: Choose closest to you
   Plan: Free
   ```

4. **Add Environment Variables**:
   ```
   DATABASE_URL=postgresql://[user]:[password]@[host]:5432/datastraw
   SECRET_KEY=your-production-key
   ENVIRONMENT=production
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment
   - Get your public URL

---

### Option 3: Heroku (Deprecated but still works)

**Note**: Heroku free tier ended in Nov 2022. Paid option only.

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create datastraw-roster

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main

# Seed database
heroku run python scripts/seed_data.py
```

---

### Option 4: AWS (EC2 + RDS)

**Advantages**:
- ✅ Most control and customization
- ✅ AWS free tier available (12 months)
- ✅ Professional infrastructure

**Steps**:

1. **Create EC2 Instance**:
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.micro (free tier)
   - Security groups: Allow ports 80, 443, 22, 5432

2. **Install Docker**:
   ```bash
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

3. **Clone Repository**:
   ```bash
   git clone https://github.com/nikspatil0120/DataStraw-Smart-Roster-Management-System.git
   cd DataStraw
   ```

4. **Create RDS PostgreSQL**:
   - Create DB instance: postgres:15
   - Multi-AZ: No (for cost)
   - Public accessibility: Yes
   - Save connection string

5. **Update docker-compose.yml**:
   ```yaml
   environment:
     DATABASE_URL: postgresql://[user]:[pass]@[rds-endpoint]:5432/datastraw
   ```

6. **Deploy**:
   ```bash
   docker-compose up -d
   docker-compose exec backend python scripts/seed_data.py
   ```

7. **Setup SSL with Let's Encrypt**:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot certonly --standalone -d your-domain.com
   ```

---

### Option 5: DigitalOcean (App Platform)

**Advantages**:
- ✅ Simple GitHub deployment
- ✅ Affordable ($12/month)
- ✅ Good documentation
- ✅ Built-in database

**Steps**:

1. **Create DigitalOcean Account**
2. **Go to App Platform**
3. **Select GitHub Repository**
4. **Choose App Spec**:
   - Detect: Docker
   - Services: Backend + Frontend + Database

5. **Deploy**:
   ```
   www.your-app.ondigitalocean.app
   api.your-app.ondigitalocean.app
   ```

---

## Production Checklist

Before deploying to production:

### Security
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=false`
- [ ] Configure `ALLOWED_ORIGINS` for your domain
- [ ] Use HTTPS/SSL certificates
- [ ] Set secure database password
- [ ] Configure firewall rules
- [ ] Use environment variables (not hardcoded secrets)

### Database
- [ ] Create backup strategy
- [ ] Configure automated backups
- [ ] Set up monitoring
- [ ] Test database restore procedure
- [ ] Run migrations before deploying

### Monitoring
- [ ] Enable logging
- [ ] Set up error tracking (Sentry)
- [ ] Configure performance monitoring
- [ ] Set up alerts for errors/downtime
- [ ] Monitor database performance

### Performance
- [ ] Enable caching (Redis)
- [ ] Configure CDN for frontend
- [ ] Set up load balancing if needed
- [ ] Optimize database queries
- [ ] Test under load

---

## Environment Variables

### Backend (.env for production)

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/datastraw

# Security
SECRET_KEY=your-production-secret-key-min-50-chars
DEBUG=false
ENVIRONMENT=production

# CORS
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# API
API_HOST=0.0.0.0
API_PORT=8000

# Optional - Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend (.env for production)

```env
# API
VITE_API_URL=https://api.your-domain.com
VITE_APP_NAME=DataStraw Smart Roster

# Analytics (optional)
VITE_ANALYTICS_KEY=your-analytics-key
```

---

## Deployment on Railway (Recommended)

### Step-by-Step

1. **Prepare Repository** ✅ (Already done)
   ```bash
   git push origin main
   ```

2. **Go to Railway**:
   ```
   https://railway.app
   ```

3. **Sign Up with GitHub**:
   - Click "Login with GitHub"
   - Authorize Railway to access your repos

4. **Create New Project**:
   - Click "Create New Project"
   - Select "GitHub Repo"
   - Choose your DataStraw repo

5. **Configure Services**:
   - Railway auto-detects `docker-compose.yml`
   - Creates services: postgres, backend, frontend

6. **Set Environment Variables**:
   - Go to each service
   - Add production environment variables
   - Set database connection string

7. **Deploy**:
   - Click "Deploy"
   - Monitor deployment logs
   - Wait for all services to be healthy

8. **Get Public URLs**:
   - Backend: `https://[project]-prod.railway.app`
   - Frontend: `https://[project]-frontend-prod.railway.app`

9. **Seed Database**:
   - Go to Backend service → "Deploy" → "Shell"
   ```bash
   python scripts/seed_data.py
   ```

10. **Access Your App**:
    ```
    Frontend: https://[project]-frontend-prod.railway.app
    API: https://[project]-prod.railway.app
    Docs: https://[project]-prod.railway.app/docs
    ```

---

## Post-Deployment Testing

### Test API Endpoints

```bash
# Health check
curl https://your-api.railway.app/health

# List employees
curl https://your-api.railway.app/api/employees

# List rosters
curl https://your-api.railway.app/api/rosters

# API documentation
https://your-api.railway.app/docs
```

### Test Frontend

1. Open https://your-app.railway.app
2. Navigate to Dashboard
3. Go to Roster page
4. Generate a roster
5. Check Conflicts page
6. Verify pagination works
7. Test error handling

---

## Scaling to Production

### Add Monitoring

```bash
# Sentry (Error tracking)
pip install sentry-sdk

# Add to backend main.py:
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production"
)
```

### Add Caching

```bash
# Redis for caching
docker run -d -p 6379:6379 redis:latest

# Install python redis
pip install redis
```

### Add Load Balancing

- Use Railway's built-in load balancing
- Or use Nginx with multiple backend instances

---

## Troubleshooting

### App Not Starting

```bash
# Check logs
docker-compose logs backend

# Check database connection
docker-compose exec backend python -c "from app.database import engine; print(engine.url)"

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Database Connection Error

```bash
# Verify DATABASE_URL format
postgresql://username:password@host:5432/dbname

# Test connection
psql postgresql://username:password@host:5432/dbname
```

### API Not Responding

```bash
# Check backend logs
docker-compose logs backend

# Verify port mapping
docker-compose ps

# Check health
curl http://localhost:8000/health
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Verify API URL is correct
cat frontend/.env

# Check CORS headers
curl -H "Origin: http://localhost:5173" http://localhost:8000/health
```

---

## Continuous Deployment

### Auto-Deploy on GitHub Push

1. **Railway**:
   - Automatic on every push to main
   - No additional configuration needed

2. **Render**:
   - Automatic on every push to main
   - Configure auto-deploy in settings

3. **GitHub Actions** (if using other platforms):
   ```yaml
   name: Deploy to Production
   on:
     push:
       branches: [main]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Deploy to your-platform
           run: ./deploy.sh
   ```

---

## Rollback Procedure

### Railway
```
Dashboard → Deployments → Select Previous → Redeploy
```

### Render
```
Dashboard → Deploys → Select Previous → Redeploy
```

### Manual
```bash
git revert [commit-hash]
git push origin main
```

---

## Support & Resources

- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs
- **React Docs**: https://react.dev
- **Docker Docs**: https://docs.docker.com

---

## Quick Deploy Commands

### Railway CLI

```bash
npm install -g @railway/cli

railway login
railway link  # Select your project
railway up    # Deploy
```

### Manual Docker Deploy

```bash
# Build images
docker-compose build

# Run locally
docker-compose up

# Push to registry
docker tag datastraw-backend yourusername/datastraw-backend:latest
docker push yourusername/datastraw-backend:latest
```

---

**Choose Railway for simplest deployment. Start now: https://railway.app** 🚀
