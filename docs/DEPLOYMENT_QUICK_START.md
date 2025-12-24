# Deployment Quick Start Guide (Free Tier)

## TL;DR - Recommended Approach

**Deploy Time Warp to a single EC2 t2.micro instance with Docker Compose**

**Cost: $0/month (first year), ~$10/month after**

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  CloudFlare   │ (Free DNS/CDN)
                    │  (Optional)   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  EC2 t2.micro │ (Free tier: $0/month)
                    │  Ubuntu 22.04 │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Docker Compose│
                    └───────┬───────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                         │
        ▼                                         ▼
┌───────────────┐                        ┌───────────────┐
│    Nginx      │                        │   Django      │
│  (Reverse     │                        │  (Gunicorn)   │
│   Proxy)      │                        │               │
│  SSL:443      │                        │               │
└───────┬───────┘                        └───────┬───────┘
        │                                         │
        └───────────────────┬───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  PostgreSQL   │
                    │  (Container)  │
                    │  (Volume)     │
                    └───────────────┘
```

## Key Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Hosting** | EC2 t2.micro | Free tier eligible ($0/month first year) |
| **Container Platform** | Docker Compose | Simple, free, runs on single EC2 instance |
| **Database** | PostgreSQL (Docker) | Free, no RDS costs ($15-20/month saved) |
| **Web Server** | Nginx (Docker) | Free, handles SSL termination |
| **SSL** | Let's Encrypt | Free SSL certificates via Certbot |
| **DNS/CDN** | CloudFlare | Free tier includes DNS and CDN |
| **CI/CD** | GitHub Actions | Free for public repos, deploy via SSH |
| **Container Registry** | Docker Hub | Free public repos (or ECR 500MB free tier) |
| **Secrets** | .env file | Simple, secure with proper permissions |
| **Monitoring** | CloudWatch Free Tier | 10 metrics, 5GB logs included |
| **Backups** | S3 (pg_dump) | 5GB free tier for backups |

## Implementation Order

1. **Day 1-2: Docker Setup**
   - Create Dockerfile
   - Create docker-compose.yml for local dev
   - Create docker-compose.prod.yml for production
   - Test locally with PostgreSQL

2. **Day 3-4: Application Configuration**
   - Split Django settings (base/dev/prod)
   - Add environment variable support
   - Implement health check endpoint
   - Test PostgreSQL migrations
   - Configure Nginx

3. **Day 5-6: EC2 Setup**
   - Launch EC2 t2.micro instance
   - Install Docker and Docker Compose
   - Configure security group
   - Set up SSH access

4. **Day 7: Deployment**
   - Push Docker image to Docker Hub or ECR
   - Deploy docker-compose to EC2
   - Set up Let's Encrypt SSL
   - Configure domain (CloudFlare or direct IP)
   - Test application

5. **Day 8: Automation & Monitoring**
   - Set up GitHub Actions for CI/CD
   - Configure database backups (S3)
   - Set up CloudWatch logging
   - Configure auto-updates

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

### Build and Push to Docker Hub (Free)
```bash
# Login to Docker Hub
docker login

# Build image
docker build -t yourusername/time-warp:latest .

# Push to Docker Hub
docker push yourusername/time-warp:latest
```

### Deploy to EC2
```bash
# SSH to EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Pull latest image
docker-compose -f docker-compose.prod.yml pull

# Restart services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Set Up Let's Encrypt SSL
```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Get certificate (if using Nginx)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
# Test renewal: sudo certbot renew --dry-run
```

## Cost Optimization Tips

1. **Use AWS Free Tier** - First 12 months: $0/month
2. **Reserved Instances** - After free tier: ~$5-6/month (save 40% vs on-demand)
3. **Spot Instances** - For non-critical: ~$2-3/month (save 70-90%)
4. **Docker Hub** - Free public repos (vs ECR which charges after 500MB)
5. **CloudWatch Logs retention** - Set to 7 days (free tier: 5GB)
6. **S3 Intelligent-Tiering** - Automatic cost optimization for backups
7. **CloudFlare Free Tier** - Includes CDN, DDoS protection, DNS
8. **Let's Encrypt** - Free SSL certificates (vs ACM which requires ALB)

## Security Checklist

- [ ] Security group restricts SSH to your IP only
- [ ] PostgreSQL only accessible from localhost (Docker network)
- [ ] `.env` file has restricted permissions (chmod 600)
- [ ] HTTPS enforced (redirect HTTP to HTTPS via Nginx)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] Database backups enabled (daily pg_dump to S3)
- [ ] Regular security updates (`sudo apt update && sudo apt upgrade`)
- [ ] Firewall configured (ufw or iptables)
- [ ] Fail2ban installed (prevent brute force attacks)
- [ ] Let's Encrypt auto-renewal configured

## Monitoring Essentials (Free Tier)

1. **EC2 Instance Metrics** (Included)
   - CPU utilization
   - Memory utilization
   - Network in/out
   - Disk read/write

2. **Custom Application Metrics** (10 free)
   - Request count
   - Response time
   - Error rate (5xx)
   - Database connection pool

3. **CloudWatch Logs** (5GB free)
   - Django error logs
   - Gunicorn access logs
   - Nginx access/error logs
   - Application-specific logs

4. **Basic Alarms** (Optional - may incur small costs)
   - High CPU (>80%)
   - Low disk space (<20%)
   - Application errors

## Troubleshooting

### Container won't start
- Check logs: `docker-compose logs web`
- Verify environment variables in `.env` file
- Check Docker is running: `sudo systemctl status docker`
- Verify disk space: `df -h`

### Database connection issues
- Check PostgreSQL container is running: `docker-compose ps`
- Verify database credentials in `.env` file
- Check database logs: `docker-compose logs db`
- Test connection: `docker-compose exec web python manage.py dbshell`

### SSL certificate issues
- Check Certbot logs: `sudo certbot certificates`
- Verify domain DNS points to EC2 IP
- Test renewal: `sudo certbot renew --dry-run`
- Check Nginx config: `sudo nginx -t`

### Application not accessible
- Check security group allows HTTP (80) and HTTPS (443)
- Verify Nginx is running: `docker-compose ps nginx`
- Check Nginx logs: `docker-compose logs nginx`
- Test locally on EC2: `curl http://localhost`

## Next Steps After Deployment

1. Set up domain name (CloudFlare free tier)
2. Configure SSL certificate (Let's Encrypt via Certbot)
3. Set up automated database backups (cron job + S3)
4. Configure CloudWatch logging
5. Set up basic monitoring alarms
6. Configure auto-updates for security patches
7. Set up GitHub Actions for automated deployments
8. (Optional) Add application performance monitoring

## Cost Summary

| Period | Cost | Breakdown |
|--------|------|-----------|
| **First 12 months** | **$0/month** | AWS Free Tier covers everything |
| **After free tier** | **~$10-15/month** | EC2 t2.micro + EBS + minimal data transfer |
| **With Reserved Instance** | **~$7-8/month** | 1-year commitment saves 40% |
| **With Spot Instance** | **~$2-3/month** | For non-critical workloads (can be interrupted) |

