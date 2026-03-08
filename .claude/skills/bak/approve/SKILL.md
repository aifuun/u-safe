---
name: approve
description: |
  Approve and execute critical operations (deploy, release, database migrations).
  Gating mechanism for high-risk changes with verification.
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(git *), Bash(npm *), Bash(aws *)
context: fork
agent: general-purpose
---

# Operation Approver

Gate critical operations with verification steps.

## Task

Safely approve and execute:
1. **CloudFormation/CDK Deploy** - Infrastructure changes
2. **Database Migrations** - Schema changes
3. **Production Release** - Deploy to production
4. **Permission Changes** - Auth/security updates

## Approval Process

For each operation:
1. **Verify** - Show exactly what will change
2. **Review** - Checklist of safety checks
3. **Confirm** - Manual approval required
4. **Execute** - Run the operation
5. **Verify** - Confirm success

## Example: CDK Deploy

```
⚠️ CDK deployment requires approval

Changes:
- New Lambda function: PaymentProcessor
- DynamoDB table: orders (10 GB)
- API Gateway endpoint: /payments

Safety Checks:
✅ Tests passing
✅ Code reviewed
✅ Staging deployment successful
❓ Database backup ready? Y/N
❓ Rollback plan documented? Y/N

All checks passed.
Continue? (yes/no)
```

---

Prevents:
- Accidental deployments
- Unreviewed infrastructure changes
- Database corruption
- Breaking production
