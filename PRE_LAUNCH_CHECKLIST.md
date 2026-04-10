# 📋 CAPABL Track B - Deployment Checklist

## Pre-Deployment

### Environment Setup
- [ ] `.env` file created with all required variables
- [ ] Database password generated and stored securely
- [ ] JWT secret key generated: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Encryption master key generated: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- [ ] All credentials in `.env`, not in code

### Prerequisites
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Python 3.11+ installed
- [ ] Git configured
- [ ] Port 3000, 8000-8004, 5432 available

---

## Local Development (Docker Compose)

### Start Services
```bash
docker-compose up -d                    # Start all services
docker-compose ps                       # Verify all running
```
- [ ] API Gateway healthy (port 8000)
- [ ] Market Data Service healthy (8001)
- [ ] Portfolio Service healthy (8002)
- [ ] Analytics Service healthy (8003)
- [ ] Monitoring Service healthy (8004)
- [ ] Frontend running (port 3000)
- [ ] PostgreSQL running (port 5432)

### Verification
```bash
curl http://localhost:8000/health       # API Gateway health
curl http://localhost:8001/health       # Market Data health
curl http://localhost:8002/health       # Portfolio health
curl http://localhost:8003/health       # Analytics health
curl http://localhost:8004/health       # Monitoring health
```
- [ ] All health checks return 200 OK
- [ ] Frontend accessible at http://localhost:3000
- [ ] API docs at http://localhost:8000/docs

### Database
```bash
docker exec capabl_postgres psql -U capabl -d capabl_finance -c "\dt"
```
- [ ] Database tables created
- [ ] Indexes in place
- [ ] Schema applied successfully

---

## Testing & Validation

### API Testing
- [ ] Authentication endpoint working: `POST /auth/token`
- [ ] Quote endpoint working: `GET /api/v1/market/quotes/RELIANCE.NS`
- [ ] Portfolio endpoint working: `GET /api/v1/portfolio/positions`
- [ ] Analytics endpoint working: `GET /api/v1/analytics/sentiment/RELIANCE.NS`
- [ ] Rate limiting active (test >100 req/min)

### Demo Scenarios
- [ ] All 5 scenarios generate without errors
- [ ] Scenario 1: Portfolio tracking data present
- [ ] Scenario 2: Stock comparison data present
- [ ] Scenario 3: Optimization results valid
- [ ] Scenario 4: Market overview data present
- [ ] Scenario 5: Trading alert workflow executable
- [ ] Run: `python run_demo.py --script`

### Security
- [ ] JWT tokens validating correctly
- [ ] Rate limiting enforced
- [ ] Encryption working on PII data
- [ ] Audit logs being created
- [ ] CORS headers present in responses
- [ ] No secrets in logs

---

## Production Deployment (Kubernetes)

### Prerequisites
- [ ] Kubernetes cluster ready (kubectl configured)
- [ ] Docker images pushed to registry
- [ ] Environment secrets created
- [ ] Persistent volume provisioner available
- [ ] Load balancer service available

### Deployment Steps
```bash
# 1. Create namespace and secrets
kubectl create namespace capabl
kubectl create secret generic db-secrets \
  --from-literal=username=capabl \
  --from-literal=password=<strong_password> \
  -n capabl

# 2. Apply manifests
kubectl apply -f k8s-deployment.yaml

# 3. Verify deployment
kubectl get pods -n capabl
kubectl get services -n capabl
```

- [ ] All pods running (6+ replicas for API Gateway)
- [ ] Services exposed correctly
- [ ] LoadBalancer service has external IP
- [ ] Database pod has persistent volume
- [ ] Health checks pass

### Monitoring & Logging
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards accessible
- [ ] ELK stack receiving logs
- [ ] Alerts configured
- [ ] HPA scaling policies active

---

## Security Hardening

### Network Security
- [ ] Firewall rules: Allow 80, 443, deny others
- [ ] Ingress TLS certificates installed
- [ ] Network policies restricting pod communication
- [ ] No direct database access from internet

### Data Security
- [ ] Database encryption at rest enabled
- [ ] Backups encrypted
- [ ] Secrets rotated monthly
- [ ] API keys not in logs
- [ ] PII data encrypted

### Application Security
- [ ] SQL injection prevention active
- [ ] CSRF tokens implemented
- [ ] XSS protection enabled
- [ ] CORS properly configured
- [ ] Rate limiting enforced

---

## Performance Verification

### Response Times
- [ ] p50 latency < 100ms
- [ ] p99 latency < 300ms
- [ ] API Gateway < 50ms
- [ ] Service latencies acceptable

### Throughput
- [ ] ≥100 requests/second
- [ ] Cache hit rate ≥70%
- [ ] Error rate <1%
- [ ] No timeout failures

### Resources
- [ ] CPU usage <70%
- [ ] Memory usage <80%
- [ ] Database connections <20 active
- [ ] No connection pool exhaustion

---

## Backup & Recovery

### Database Backups
- [ ] Daily automated backups scheduled
- [ ] Backup location verified
- [ ] Backup encryption verified
- [ ] Retention policy: 30 days
- [ ] Test restore procedure successful

### Disaster Recovery
- [ ] Failover tested
- [ ] RTO: <5 minutes
- [ ] RPO: <1 hour
- [ ] Runbook created
- [ ] Team trained

---

## Documentation

### Public Documentation
- [ ] README.md complete and accurate
- [ ] API_DOCUMENTATION.md complete
- [ ] TRACK_B_README.md reviewed
- [ ] DEPLOYMENT_GUIDE.md verified
- [ ] DEMO_SCENARIOS.py executable

### Internal Documentation
- [ ] Architecture diagrams created
- [ ] Security audit completed
- [ ] Performance benchmarks documented
- [ ] Operational runbooks created
- [ ] Troubleshooting guide written

---

## Team & Knowledge Transfer

### Developer Team
- [ ] All developers can deploy locally
- [ ] All developers understand architecture
- [ ] Git workflow documented
- [ ] Code review process established
- [ ] Documentation accessible

### Operations Team
- [ ] Ops can deploy to Kubernetes
- [ ] Monitoring dashboards configured
- [ ] Alert escalation procedures defined
- [ ] On-call rotation established
- [ ] Incident response plan ready

### Security Team
- [ ] Security audit completed
- [ ] Penetration testing scheduled
- [ ] Vulnerability scanning enabled
- [ ] Compliance checklist verified
- [ ] Data privacy policy written

---

## Final Verification

### Pre-Launch Checklist
- [ ] All services passing health checks
- [ ] API response times acceptable
- [ ] Demo scenarios working perfectly
- [ ] Security audit passed
- [ ] Database backups verified
- [ ] Team trained and ready
- [ ] Documentation complete
- [ ] Monitoring alerts configured

### Launch Day Tasks
- [ ] Announce deployment
- [ ] Monitor error rates closely
- [ ] Watch performance metrics
- [ ] Be available for incidents
- [ ] Verify all features working
- [ ] Gather user feedback

---

## Post-Launch Monitoring

### First 24 Hours
- [ ] Error rate < 0.5%
- [ ] No incidents requiring rollback
- [ ] Performance stable
- [ ] Users report positive experience
- [ ] All metrics nominal

### First Week
- [ ] Monitor utilization trends
- [ ] Check for memory leaks
- [ ] Verify backup processes
- [ ] Review security logs
- [ ] Gather operational insights

### Ongoing
- [ ] Daily health checks
- [ ] Weekly performance reviews
- [ ] Monthly security updates
- [ ] Quarterly disaster recovery drill
- [ ] Continuous improvement

---

## Quick Reference Commands

```bash
# Docker Compose
docker-compose up -d                    # Start
docker-compose down                     # Stop
docker-compose logs -f <service>        # View logs
docker-compose ps                       # Status

# Health Checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health

# Database
docker exec capabl_postgres psql -U capabl -d capabl_finance

# Kubernetes
kubectl get pods -n capabl              # View pods
kubectl logs -f pod/name -n capabl      # View logs
kubectl describe pod/name -n capabl     # Debug
kubectl apply -f k8s-deployment.yaml    # Deploy
kubectl delete namespace capabl         # Remove

# Demo
python run_demo.py --script             # Full demo
python run_demo.py --scenario 1         # Scenario 1
python run_demo.py --architecture       # Architecture
```

---

## Support Contacts

- **Technical Lead**: [Your Name]
- **DevOps Lead**: [Your Name]
- **Security Lead**: [Your Name]
- **Product Manager**: [Your Name]

---

## Sign-Off

- [ ] Project Manager: _____________ Date: _______
- [ ] Technical Lead: _____________ Date: _______
- [ ] DevOps Engineer: _____________ Date: _______
- [ ] Security Officer: _____________ Date: _______

---

**Status**: 🟢 READY FOR PRODUCTION

All checklist items must be completed before launch.

**Last Updated**: April 10, 2026  
**Version**: 1.0.0
