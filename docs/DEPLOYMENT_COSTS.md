# Deployment Cost Breakdown

## Free Tier Deployment Strategy

This document breaks down the costs for deploying Time Warp using AWS free tier and cost-optimized services.

---

## Cost Comparison

### Original Plan (ECS Fargate + RDS)
- **Monthly Cost**: ~$90-120/month
- **Components**: ECS Fargate, RDS PostgreSQL, ALB, NAT Gateway

### Free Tier Plan (EC2 + Docker Compose)
- **First 12 months**: **$0/month** ✅
- **After free tier**: **~$10-15/month**
- **Components**: EC2 t2.micro, Docker Compose, PostgreSQL in container

**Savings: ~$90-120/month (first year), ~$75-110/month (after)**

---

## Detailed Cost Breakdown

### First 12 Months (AWS Free Tier) - $0/month

| Service | Free Tier Allowance | Usage | Cost |
|---------|-------------------|-------|------|
| **EC2 t2.micro** | 750 hours/month | Full month | $0 |
| **EBS Storage** | 20GB | ~10-15GB | $0 |
| **Data Transfer Out** | 1GB/month | <1GB | $0 |
| **CloudWatch Logs** | 5GB/month | <5GB | $0 |
| **CloudWatch Metrics** | 10 custom | 5-8 metrics | $0 |
| **ECR Storage** | 500MB | <500MB | $0 |
| **S3 Storage** | 5GB | ~1-2GB (backups) | $0 |
| **S3 Requests** | 20K GET, 2K PUT | Minimal | $0 |
| **Let's Encrypt SSL** | Unlimited | 1 certificate | $0 |
| **CloudFlare DNS/CDN** | Free tier | Full features | $0 |

**Total: $0/month** ✅

### After Free Tier Expires - ~$10-15/month

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **EC2 t2.micro (on-demand)** | 730 hours | ~$8-10 |
| **EBS Storage (20GB)** | 20GB | ~$2 |
| **Data Transfer Out** | 1-5GB | ~$0-0.50 |
| **CloudWatch Logs** | <5GB | $0-0.50 |
| **S3 Storage (backups)** | 1-2GB | ~$0.05 |
| **ECR Storage** | <500MB | $0 |
| **Let's Encrypt SSL** | 1 certificate | $0 |
| **CloudFlare DNS/CDN** | Free tier | $0 |

**Total: ~$10-15/month**

### Cost Optimization Options

#### Option 1: Reserved Instance (1-year commitment)
- **EC2 t2.micro Reserved**: ~$5-6/month
- **Total**: ~$7-8/month
- **Savings**: 40% vs on-demand

#### Option 2: Spot Instance (can be interrupted)
- **EC2 t2.micro Spot**: ~$2-3/month
- **Total**: ~$4-5/month
- **Savings**: 70-90% vs on-demand
- **Risk**: Instance can be terminated with 2-minute notice

#### Option 3: Lightsail (Alternative)
- **Lightsail $3.50 plan**: ~$3.50/month
- Includes: 512MB RAM, 1 vCPU, 20GB SSD, 1TB transfer
- **Total**: ~$3.50/month
- **Note**: Less flexible than EC2, but simpler

---

## What You Get for Free (First Year)

### AWS Free Tier Includes:
1. **EC2**: 750 hours/month of t2.micro or t3.micro
2. **EBS**: 20GB of General Purpose SSD storage
3. **Data Transfer**: 1GB out to internet per month
4. **CloudWatch**: 5GB log ingestion, 10 custom metrics
5. **ECR**: 500MB container image storage
6. **S3**: 5GB storage, 20K GET requests, 2K PUT requests

### Additional Free Services:
1. **Let's Encrypt**: Free SSL certificates (unlimited)
2. **CloudFlare**: Free DNS, CDN, DDoS protection
3. **GitHub Actions**: Free for public repositories
4. **Docker Hub**: Free public container repositories

---

## What's NOT Included (But We Don't Need)

### Services We Avoid to Keep Costs Low:

1. **RDS PostgreSQL** - $15-20/month
   - **Alternative**: PostgreSQL in Docker container (free)

2. **Application Load Balancer (ALB)** - $16/month
   - **Alternative**: Nginx reverse proxy in Docker (free)

3. **NAT Gateway** - $32/month
   - **Alternative**: Not needed (EC2 in public subnet)

4. **Route 53** - $0.50/month per hosted zone
   - **Alternative**: CloudFlare DNS (free)

5. **ACM Certificate** - Free, but requires ALB
   - **Alternative**: Let's Encrypt (free, works with Nginx)

6. **Secrets Manager** - $0.40/secret/month
   - **Alternative**: `.env` file with proper permissions (free)

---

## Scaling Costs (If Needed Later)

If traffic grows significantly, here are incremental costs:

### Low Traffic (<1000 requests/day)
- Current setup sufficient
- **Cost**: $0-15/month

### Medium Traffic (10K-100K requests/day)
- May need t3.small instance: +$15/month
- More data transfer: +$5-10/month
- **Total**: ~$30-40/month

### High Traffic (100K+ requests/day)
- Consider ECS Fargate: ~$50-100/month
- RDS PostgreSQL: +$15-30/month
- ALB: +$16/month
- **Total**: ~$100-150/month**

---

## Cost Monitoring

### Set Up Billing Alerts:
1. Go to AWS Billing Dashboard
2. Create budget alert at $5/month (for after free tier)
3. Get email notifications if costs exceed threshold

### Track Free Tier Usage:
1. AWS Free Tier Dashboard shows remaining credits
2. Monitor EC2 hours used (750/month limit)
3. Monitor EBS storage (20GB limit)
4. Monitor data transfer (1GB/month limit)

---

## Summary

| Scenario | Monthly Cost | Notes |
|----------|--------------|-------|
| **First 12 months** | **$0** | AWS Free Tier covers everything |
| **After free tier (on-demand)** | **~$10-15** | Standard pricing |
| **After free tier (reserved)** | **~$7-8** | 1-year commitment |
| **After free tier (spot)** | **~$4-5** | Can be interrupted |
| **Lightsail alternative** | **~$3.50** | Less flexible |

**Recommendation**: Start with free tier, then move to Reserved Instance after 12 months for best balance of cost and reliability.

