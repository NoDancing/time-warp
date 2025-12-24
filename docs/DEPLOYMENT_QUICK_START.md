# Deployment Quick Start Guide

## TL;DR - Recommended Approach

**Deploy Time Warp to AWS ECS Fargate with RDS PostgreSQL**

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Route 53     │ (DNS)
                    │  (Optional)   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │      ALB      │ (Application Load Balancer)
                    │   HTTPS:443   │
                    └───────┬───────┘
                            │
                            ▼
        ┌───────────────────┴───────────────────┐
        │                                         │
        ▼                                         ▼
┌───────────────┐                        ┌───────────────┐
│  ECS Fargate  │                        │  ECS Fargate  │
│   Service 1   │                        │   Service 2    │
│               │                        │               │
│  Django App   │                        │  Django App   │
│  (Gunicorn)   │                        │  (Gunicorn)   │
└───────┬───────┘                        └───────┬───────┘
        │                                         │
        └───────────────────┬───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  RDS          │
                    │  PostgreSQL   │
                    │  (Private)    │
                    └───────────────┘
```

## Key Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Container Platform** | ECS Fargate | Serverless, no EC2 management, auto-scaling |
| **Database** | RDS PostgreSQL | Managed, automated backups, Multi-AZ support |
| **Load Balancer** | ALB | HTTPS termination, health checks, path routing |
| **IaC Tool** | AWS CDK (Python) | Type-safe, familiar language, good AWS integration |
| **CI/CD** | GitHub Actions | Simple, free for public repos, good Docker support |
| **Container Registry** | Amazon ECR | Integrated with ECS, secure, cost-effective |
| **Secrets** | AWS Secrets Manager | Secure, automatic rotation support |
| **Monitoring** | CloudWatch | Native AWS integration, no additional setup |

## Implementation Order

1. **Week 1: Docker Setup**
   - Create Dockerfile
   - Create docker-compose.yml for local dev
   - Test locally with PostgreSQL

2. **Week 2: Application Configuration**
   - Split Django settings (base/dev/prod)
   - Add environment variable support
   - Implement health check endpoint
   - Test PostgreSQL migrations

3. **Week 3: Infrastructure**
   - Set up AWS account and IAM
   - Create CDK project
   - Define VPC, RDS, ECS infrastructure
   - Deploy to staging environment

4. **Week 4: CI/CD & Production**
   - Set up GitHub Actions workflow
   - Configure ECR and image building
   - Deploy to production
   - Set up monitoring and alarms

## Quick Commands

### Local Development
```bash
# Build and run with docker-compose
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Build and Push to ECR
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t time-warp:latest .

# Tag for ECR
docker tag time-warp:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/time-warp:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/time-warp:latest
```

### Deploy to ECS
```bash
# Update ECS service (via CDK or AWS CLI)
aws ecs update-service --cluster time-warp-cluster --service time-warp-service --force-new-deployment

# Run migrations (as ECS task)
aws ecs run-task \
  --cluster time-warp-cluster \
  --task-definition time-warp-migrations \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}"
```

## Cost Optimization Tips

1. **Use Fargate Spot** for non-production environments (up to 70% savings)
2. **Reserved Capacity** for RDS if predictable workload
3. **S3 for static files** instead of EBS volumes
4. **CloudWatch Logs retention** set to 7-14 days (not indefinite)
5. **NAT Gateway** - consider NAT Instance for dev/staging (cheaper but less reliable)

## Security Checklist

- [ ] ECS tasks run in private subnets
- [ ] RDS has no public access
- [ ] Security groups follow least privilege
- [ ] Secrets stored in Secrets Manager (not environment variables)
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] Database backups enabled
- [ ] IAM roles use least privilege policies
- [ ] CloudWatch logs encrypted

## Monitoring Essentials

1. **ECS Service Metrics**
   - CPU utilization
   - Memory utilization
   - Running task count

2. **ALB Metrics**
   - Request count
   - Target response time
   - HTTP 5xx error count
   - Healthy/unhealthy target count

3. **RDS Metrics**
   - CPU utilization
   - Database connections
   - Read/Write latency
   - Free storage space

4. **Application Logs**
   - Django error logs
   - Gunicorn access logs
   - Application-specific logs

## Troubleshooting

### Container won't start
- Check CloudWatch logs for errors
- Verify environment variables are set
- Check security group allows outbound connections
- Verify task has IAM role with necessary permissions

### Database connection issues
- Verify RDS security group allows ECS security group
- Check database endpoint is correct
- Verify credentials in Secrets Manager
- Check RDS is in same VPC as ECS tasks

### Health checks failing
- Verify `/health/` endpoint exists and works
- Check health check path and port in ALB target group
- Verify security groups allow ALB to reach ECS tasks
- Check application logs for errors

## Next Steps After Deployment

1. Set up domain name and Route 53
2. Configure SSL certificate (ACM)
3. Set up CloudFront for static files (if using S3)
4. Configure automated backups
5. Set up staging environment
6. Implement blue/green deployments
7. Add application performance monitoring (optional: DataDog, New Relic)

