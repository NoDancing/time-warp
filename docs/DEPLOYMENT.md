# Docker on AWS Deployment Plan

## Overview

This document outlines the deployment strategy for Time Warp using Docker containers on AWS. The application is a Django REST Framework API that currently uses SQLite and needs to be containerized and deployed to a production-ready environment.

---

## Architecture Decisions

### Current State
- Django REST Framework API
- SQLite database (development only)
- Simple client-server architecture
- No background jobs or workers
- Static file serving (minimal)

### Production Requirements
- **Database**: Migrate from SQLite to PostgreSQL (RDS)
- **Application Server**: Docker container with Gunicorn
- **Web Server**: Nginx (reverse proxy) or ALB (Application Load Balancer)
- **Static Files**: AWS S3 + CloudFront (or served by Django in MVP)
- **Secrets Management**: AWS Secrets Manager or Parameter Store
- **Monitoring**: CloudWatch Logs and Metrics

---

## Deployment Options

### Option 1: AWS ECS (Fargate) - **RECOMMENDED**
**Best for**: Simple container orchestration without managing servers

**Pros:**
- Serverless container platform (no EC2 management)
- Auto-scaling built-in
- Integrated with ALB
- Cost-effective for small to medium traffic
- Easy CI/CD integration

**Cons:**
- Less control over underlying infrastructure
- Cold starts can occur

**Architecture:**
```
Internet → ALB → ECS Fargate Service → Django App (Gunicorn)
                    ↓
                RDS PostgreSQL
```

### Option 2: AWS App Runner
**Best for**: Simplest deployment with minimal configuration

**Pros:**
- Very simple setup
- Automatic scaling
- Built-in load balancing
- Good for MVP/prototypes

**Cons:**
- Less flexibility
- Limited customization
- Higher cost at scale

### Option 3: AWS ECS (EC2)
**Best for**: More control and cost optimization

**Pros:**
- Full control over EC2 instances
- Can be more cost-effective at scale
- Better for predictable workloads

**Cons:**
- Requires EC2 management
- More complex setup

### Option 4: AWS Elastic Beanstalk
**Best for**: Traditional PaaS approach

**Pros:**
- Easy deployment
- Built-in monitoring
- Handles infrastructure automatically

**Cons:**
- Less modern than ECS
- Less flexibility for container-specific features

---

## Recommended Architecture: ECS Fargate

### Components

1. **Application Container**
   - Django app running with Gunicorn
   - Environment-based configuration
   - Health check endpoint

2. **Database**
   - Amazon RDS PostgreSQL (Multi-AZ for production)
   - Automated backups enabled
   - Security groups restricting access

3. **Load Balancer**
   - Application Load Balancer (ALB)
   - HTTPS termination (ACM certificate)
   - Health checks

4. **Networking**
   - VPC with public and private subnets
   - ECS tasks in private subnets
   - NAT Gateway for outbound internet access

5. **Storage**
   - S3 bucket for static files (optional for MVP)
   - CloudFront distribution (optional for MVP)

6. **Secrets & Configuration**
   - AWS Secrets Manager for database credentials
   - Systems Manager Parameter Store for app config
   - Environment variables in ECS task definition

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
- VPC with public/private subnets
- RDS PostgreSQL instance
- ECS Cluster
- ECS Task Definition
- ECS Service
- Application Load Balancer
- Security Groups
- IAM Roles and Policies
- Secrets Manager resources

### Phase 4: CI/CD Pipeline

#### 4.1 Source Control
- GitHub Actions or AWS CodePipeline
- Build Docker image on push
- Push to Amazon ECR (Elastic Container Registry)

#### 4.2 Deployment Pipeline
1. Run tests
2. Build Docker image
3. Push to ECR
4. Update ECS service with new image
5. Run database migrations (as separate task or init container)
6. Health check verification

### Phase 5: Security Hardening

#### 5.1 Secrets Management
- Store `SECRET_KEY` in Secrets Manager
- Store database credentials in Secrets Manager
- Use IAM roles for ECS tasks (no hardcoded credentials)

#### 5.2 Network Security
- ECS tasks in private subnets
- Security groups with least privilege
- RDS in private subnet, no public access
- ALB in public subnet

#### 5.3 Application Security
- `DEBUG=False` in production
- Proper `ALLOWED_HOSTS` configuration
- HTTPS only (redirect HTTP to HTTPS)
- Security headers (via middleware or ALB)

### Phase 6: Monitoring & Logging

#### 6.1 CloudWatch Logs
- ECS task logs to CloudWatch
- Log group with retention policy
- Structured logging in Django

#### 6.2 CloudWatch Metrics
- ECS service metrics (CPU, memory)
- ALB metrics (request count, latency)
- RDS metrics (connections, CPU)
- Custom application metrics (optional)

#### 6.3 Alarms
- High CPU/memory usage
- Failed health checks
- Database connection errors
- 5xx error rate

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
│   ├── cdk/                 # AWS CDK code
│   │   ├── app.py
│   │   ├── stack.py
│   │   └── requirements.txt
│   └── terraform/           # Alternative: Terraform
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
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

### Small Scale (MVP)
- **ECS Fargate**: ~$15-30 (0.5 vCPU, 1GB RAM, minimal traffic)
- **RDS PostgreSQL (db.t3.micro)**: ~$15-20
- **ALB**: ~$16 (base cost)
- **NAT Gateway**: ~$32 (if needed)
- **Data Transfer**: ~$5-10
- **CloudWatch**: ~$5
- **ECR Storage**: ~$1

**Total**: ~$90-120/month

### Medium Scale
- **ECS Fargate**: ~$50-100
- **RDS PostgreSQL (db.t3.small)**: ~$30-40
- **ALB**: ~$16
- **NAT Gateway**: ~$32
- **Data Transfer**: ~$20-30
- **CloudWatch**: ~$10-15

**Total**: ~$160-230/month

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
- [ ] VPC and networking configured
- [ ] RDS PostgreSQL instance created
- [ ] Security groups configured
- [ ] ECR repository created
- [ ] ECS cluster created
- [ ] ECS task definition created
- [ ] ECS service configured
- [ ] ALB created and configured
- [ ] SSL certificate (ACM) configured
- [ ] Secrets Manager configured
- [ ] IAM roles and policies created

### Application
- [ ] Docker image builds successfully
- [ ] Image pushed to ECR
- [ ] Environment variables configured in ECS
- [ ] Database migrations run
- [ ] Static files collected (if applicable)
- [ ] Health checks passing

### Post-Deployment
- [ ] Application accessible via domain
- [ ] HTTPS working correctly
- [ ] Database connectivity verified
- [ ] Logs flowing to CloudWatch
- [ ] Monitoring alarms configured
- [ ] Backup strategy implemented
- [ ] Documentation updated

---

## Rollback Strategy

1. **ECS Rollback**: Revert to previous task definition revision
2. **Database Rollback**: Keep database migrations reversible
3. **Infrastructure Rollback**: Use IaC to revert infrastructure changes
4. **Blue/Green Deployment**: Deploy new version alongside old, switch traffic

---

## Next Steps

1. **Immediate**: Create Dockerfile and docker-compose.yml for local development
2. **Short-term**: Set up environment-based Django settings
3. **Medium-term**: Create infrastructure code (CDK/Terraform)
4. **Long-term**: Set up CI/CD pipeline and monitoring

---

## References

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html)
- [Dockerizing Django](https://docs.docker.com/samples/django/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [RDS PostgreSQL on AWS](https://aws.amazon.com/rds/postgresql/)

