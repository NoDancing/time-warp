# Docker on AWS Deployment Plan (Free Tier / Minimal Cost)

## Overview

This document outlines a **cost-optimized** deployment strategy for Time Warp using Docker containers on AWS. The goal is to keep costs at **$0/month for the first year** (using AWS free tier) and **~$8-10/month** thereafter.

---

## Architecture Decisions

### Current State
- Django REST Framework API
- SQLite database (development only)
- Simple client-server architecture
- No background jobs or workers
- Static file serving (minimal)

### Production Requirements (Free Tier Optimized)
- **Database**: PostgreSQL in Docker container (not RDS - saves $15-20/month)
- **Application Server**: Docker container with Gunicorn
- **Web Server**: Nginx (reverse proxy) in Docker container
- **Hosting**: Single EC2 t2.micro/t3.micro (AWS free tier eligible)
- **Static Files**: Served by Django/Nginx (or S3 free tier if needed)
- **SSL**: Let's Encrypt (free) via Certbot
- **DNS/CDN**: CloudFlare (free) or direct IP access
- **Monitoring**: CloudWatch free tier (10 custom metrics, 5GB logs)

---

## Deployment Options

### Option 1: Single EC2 with Docker Compose - **RECOMMENDED FOR FREE TIER**
**Best for**: Minimal cost, simple architecture

**Pros:**
- **$0/month for first year** (AWS free tier: 750 hours/month of t2.micro)
- **~$8-10/month after free tier** (t2.micro on-demand)
- Full control over environment
- Simple deployment with docker-compose
- PostgreSQL runs in container (no RDS costs)
- No load balancer needed (saves $16/month)

**Cons:**
- Single point of failure (no high availability)
- Manual scaling (but fine for MVP)
- Need to manage EC2 instance
- No automatic backups (need to set up manually)

**Architecture:**
```
Internet → CloudFlare (free) → EC2 t2.micro → Docker Compose
                                        ├── Nginx (reverse proxy)
                                        ├── Django App (Gunicorn)
                                        └── PostgreSQL (container)
```

### Option 2: AWS Lightsail - **ALTERNATIVE**
**Best for**: Even simpler setup, predictable pricing

**Pros:**
- $3.50/month for smallest instance (after free tier)
- Includes DNS, static IP, basic monitoring
- Very simple setup

**Cons:**
- Less flexible than EC2
- Limited to Lightsail services

### Option 3: AWS ECS (Fargate) - **NOT RECOMMENDED FOR FREE TIER**
**Best for**: Production scale (costs ~$90-120/month)

**Pros:**
- Serverless, auto-scaling
- High availability

**Cons:**
- **No free tier**
- Minimum ~$50-70/month even for minimal usage
- Requires ALB (~$16/month)

---

## Recommended Architecture: Single EC2 with Docker Compose

### Components

1. **EC2 Instance**
   - t2.micro or t3.micro (AWS free tier eligible)
   - Ubuntu 22.04 LTS (or Amazon Linux 2023)
   - Docker and Docker Compose installed
   - Security group allowing HTTP (80) and HTTPS (443)

2. **Docker Compose Services**
   - **Nginx**: Reverse proxy, SSL termination, static file serving
   - **Django**: Gunicorn WSGI server
   - **PostgreSQL**: Database in container (persistent volume)

3. **SSL/TLS**
   - Let's Encrypt certificate via Certbot
   - Auto-renewal via cron job
   - Free SSL certificates

4. **DNS & CDN (Optional)**
   - CloudFlare (free tier) for DNS and basic CDN
   - Or direct IP access for testing
   - Or Route 53 ($0.50/month per hosted zone)

5. **Storage**
   - EBS volume (20GB free tier, then ~$2/month for 20GB)
   - Docker volumes for PostgreSQL data
   - Static files served by Nginx (or S3 free tier: 5GB)

6. **Backups**
   - Manual: `pg_dump` to S3 (free tier: 5GB storage)
   - Automated: Cron job for daily backups
   - Or use AWS Backup (free tier: 10GB)

7. **Monitoring**
   - CloudWatch free tier (10 custom metrics, 5GB logs)
   - Basic EC2 metrics included
   - Application logs via CloudWatch Logs Agent

---

## Implementation Steps

### Phase 1: Docker Setup

#### 1.1 Create Dockerfile
- Multi-stage build for optimization
- Python 3.11+ base image
- Install dependencies
- Copy application code
- Set up Gunicorn
- Non-root user for security

#### 1.2 Create docker-compose.yml (Development)
- Local PostgreSQL service
- Django app service
- Volume mounts for development
- Environment variables

#### 1.3 Create .dockerignore
- Exclude unnecessary files
- Reduce build context size

### Phase 2: Application Configuration

#### 2.1 Environment-Based Settings
- Split `settings.py` into base, development, production
- Use environment variables for:
  - `SECRET_KEY`
  - `DEBUG`
  - `ALLOWED_HOSTS`
  - Database connection
  - Static files configuration

#### 2.2 Database Migration
- Update settings to use PostgreSQL
- Install `psycopg2-binary` or `psycopg2`
- Test migrations locally with PostgreSQL

#### 2.3 Static Files
- Configure `STATIC_ROOT` for production
- Set up `STATIC_URL` and `STATICFILES_STORAGE`
- For MVP: Use Django's static file serving
- For production: Configure S3 + CloudFront

#### 2.4 Health Check Endpoint
- Add `/health/` endpoint for ALB health checks
- Return 200 OK when database is accessible

### Phase 3: Infrastructure as Code

#### 3.1 Choose IaC Tool
- **Option A**: AWS CDK (Python/TypeScript)
- **Option B**: Terraform
- **Option C**: CloudFormation

**Recommendation**: AWS CDK (Python) for consistency with Django

#### 3.2 Infrastructure Components
- EC2 instance (t2.micro/t3.micro)
- Security Group (HTTP, HTTPS, SSH)
- Elastic IP (optional, free if attached to running instance)
- EBS volume for persistent storage
- IAM role for S3 backup access (if using S3)
- CloudWatch Log Group (free tier)

### Phase 4: CI/CD Pipeline

#### 4.1 Source Control
- GitHub Actions (free for public repos)
- Build Docker image on push
- Push to Docker Hub (free) or ECR (500MB free tier)

#### 4.2 Deployment Pipeline
1. Run tests
2. Build Docker image
3. Push to registry (Docker Hub or ECR)
4. SSH to EC2 instance
5. Pull new image
6. Run `docker-compose up -d` (rolling update)
7. Run database migrations
8. Health check verification

**Alternative**: Use GitHub Actions to deploy directly to EC2 via SSH

### Phase 5: Security Hardening

#### 5.1 Secrets Management
- Store `SECRET_KEY` in environment file (`.env`) on EC2
- Store database credentials in `.env` file
- Use IAM role for EC2 (for S3 backup access)
- Restrict file permissions (chmod 600 .env)

#### 5.2 Network Security
- Security group with least privilege:
  - SSH (22) from your IP only
  - HTTP (80) from anywhere (for Let's Encrypt)
  - HTTPS (443) from anywhere
- PostgreSQL only accessible from localhost (Docker network)
- No public database access

#### 5.3 Application Security
- `DEBUG=False` in production
- Proper `ALLOWED_HOSTS` configuration
- HTTPS only (redirect HTTP to HTTPS via Nginx)
- Security headers (via Nginx configuration)
- Regular security updates: `sudo apt update && sudo apt upgrade`

### Phase 6: Monitoring & Logging

#### 6.1 CloudWatch Logs
- Install CloudWatch Logs Agent on EC2 (free)
- Send Docker container logs to CloudWatch
- Log group with 7-day retention (free tier: 5GB)
- Structured logging in Django

#### 6.2 CloudWatch Metrics
- EC2 instance metrics (CPU, memory, network) - included
- Custom application metrics (free tier: 10 metrics)
- Disk usage monitoring
- Database connection monitoring

#### 6.3 Alarms (Optional - may incur small costs)
- High CPU usage (>80%)
- Low disk space (<20%)
- Application errors (5xx rate)
- Database connection failures

---

## File Structure

```
time-warp/
├── apps/
│   └── server/
│       ├── config/
│       │   ├── settings/
│       │   │   ├── __init__.py
│       │   │   ├── base.py
│       │   │   ├── development.py
│       │   │   └── production.py
│       │   └── ...
│       └── ...
├── infrastructure/          # New directory
│   ├── ec2-setup.sh         # EC2 initialization script
│   ├── deploy.sh            # Deployment script
│   └── backup.sh            # Database backup script
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── nginx/
│   │   └── nginx.conf
│   └── .dockerignore
├── scripts/
│   ├── deploy.sh
│   ├── migrate.sh
│   └── collectstatic.sh
├── .github/
│   └── workflows/
│       └── deploy.yml
└── requirements.txt         # Production dependencies
```

---

## Environment Variables

### Required for Production

```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<from-secrets-manager>
DEBUG=False
ALLOWED_HOSTS=timewarp.example.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=timewarp
DB_USER=<from-secrets-manager>
DB_PASSWORD=<from-secrets-manager>
DB_HOST=<rds-endpoint>
DB_PORT=5432

# Static Files (if using S3)
AWS_STORAGE_BUCKET_NAME=timewarp-static
AWS_S3_REGION_NAME=us-east-1

# Application
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=30
```

---

## Cost Estimation (Monthly)

### Free Tier (First 12 Months)
- **EC2 t2.micro**: **$0** (750 hours/month free)
- **EBS Storage (20GB)**: **$0** (20GB free tier)
- **Data Transfer (1GB out)**: **$0** (1GB free tier)
- **CloudWatch Logs (5GB)**: **$0** (5GB free tier)
- **CloudWatch Metrics (10)**: **$0** (10 custom metrics free)
- **ECR Storage (500MB)**: **$0** (500MB free tier)
- **S3 Storage (5GB)**: **$0** (5GB free tier, for backups)
- **Let's Encrypt SSL**: **$0** (free)
- **CloudFlare DNS/CDN**: **$0** (free tier)

**Total**: **$0/month** ✅

### After Free Tier Expires
- **EC2 t2.micro**: ~$8-10/month (on-demand)
- **EBS Storage (20GB)**: ~$2/month
- **Data Transfer**: ~$0.09/GB (first 1GB free, then ~$0.09/GB)
- **CloudWatch Logs**: ~$0.50/GB after 5GB free tier
- **S3 Storage**: ~$0.023/GB after 5GB free tier
- **ECR Storage**: ~$0.10/GB after 500MB free tier

**Total**: **~$10-15/month** (assuming low traffic)

### Cost Optimization Tips
1. Use **Reserved Instances** for 1-year commitment: ~$5-6/month (save 40%)
2. Use **Spot Instances** for non-critical workloads: ~$2-3/month (save 70-90%)
3. Use **Docker Hub** instead of ECR (free public repos)
4. Use **CloudFlare** for CDN (free tier includes CDN)
5. Set **CloudWatch log retention** to 7 days (reduce storage costs)
6. Use **S3 Intelligent-Tiering** for backups (automatic cost optimization)

---

## Deployment Checklist

### Pre-Deployment
- [ ] Dockerfile created and tested locally
- [ ] docker-compose.yml works for local development
- [ ] Environment-based settings configured
- [ ] Database migrations tested with PostgreSQL
- [ ] Health check endpoint implemented
- [ ] Requirements.txt includes all dependencies
- [ ] .dockerignore configured

### Infrastructure
- [ ] EC2 instance launched (t2.micro/t3.micro)
- [ ] Security group configured (SSH, HTTP, HTTPS)
- [ ] Elastic IP assigned (optional)
- [ ] Docker and Docker Compose installed on EC2
- [ ] Domain name configured (CloudFlare or Route 53)
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] IAM role created for S3 backup access (if using S3)
- [ ] CloudWatch Logs Agent installed

### Application
- [ ] Docker image builds successfully
- [ ] Image pushed to Docker Hub or ECR
- [ ] Environment variables configured in `.env` file
- [ ] docker-compose.prod.yml configured
- [ ] Nginx configuration tested
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Health checks passing
- [ ] SSL certificate auto-renewal configured

### Post-Deployment
- [ ] Application accessible via domain or IP
- [ ] HTTPS working correctly (Let's Encrypt)
- [ ] HTTP redirects to HTTPS
- [ ] Database connectivity verified
- [ ] Logs flowing to CloudWatch
- [ ] Basic monitoring configured
- [ ] Backup strategy implemented (daily pg_dump to S3)
- [ ] Auto-updates configured (security patches)
- [ ] Documentation updated

---

## Rollback Strategy

1. **Docker Rollback**: Keep previous Docker image tag, revert docker-compose.yml
2. **Database Rollback**: Keep database migrations reversible, restore from backup if needed
3. **Code Rollback**: Git revert and redeploy
4. **Backup Restore**: Use daily S3 backups to restore database if needed
5. **Quick Rollback**: `docker-compose down && docker-compose up -d` with previous image

---

## Next Steps

1. **Immediate**: Create Dockerfile and docker-compose.yml for local development
2. **Short-term**: Set up environment-based Django settings
3. **Medium-term**: Create infrastructure code (CDK/Terraform)
4. **Long-term**: Set up CI/CD pipeline and monitoring

---

## References

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [Dockerizing Django](https://docs.docker.com/samples/django/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [CloudFlare Free Tier](https://www.cloudflare.com/plans/free/)
- [EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [Docker Compose Production Guide](https://docs.docker.com/compose/production/)

