# Session Memory Log

## Session Date: 2026-07-01

### What was done
1. **Fixed GitHub branch issue**: When cloning on ECS, the default branch was `main` but our repo had `master` as primary. Fixed by force-pushing `master` to `main` on origin.
2. **Deployed Qwen Council on Alibaba ECS**: Ran `sudo bash deploy.sh` on instance `iZt4ngvwxej9256iz88jsqZ` (Singapore, 2 vCPU, 4 GiB, Ubuntu 22.04).
3. **Security Group configuration**: User created/configured Security Group `sg-20260630` in VPC `vpc-t4n1sjwj32log17ahg71v` (Singapore/ap-southeast-1), adding inbound rule for TCP 80/80 from 0.0.0.0/0.

### Deployment status
- **Public IP**: 47.84.227.185
- **Frontend**: http://47.84.227.185 (HTTP 200 confirmed)
- **API Health**: http://47.84.227.185/api/health (returns {"status":"ok","version":"1.0.0","db_connected":true})
- **API Docs**: http://47.84.227.185/docs (accessible)
- All 3 Docker services (frontend, backend, db) running and healthy.

### Next steps remaining
- Record YouTube video (<3 min)
- Create architecture diagram (`docs/architecture.md`)
- Optional: Add blog post for $500 bonus prize
- Optional: Add comparison demo "with council vs without council"
- Deadline: Jul 9, 2026 (2:00 pm PT)

### Key decisions
- Use `main` branch for GitHub (not `master`)
- Security group name: `sg-20260630`
- ECS region: Singapore (ap-southeast-1)
