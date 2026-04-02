---
category: "infrastructure"
title: "Cdk Watch Testing"
description: "CDK watch mode"
tags: [typescript, aws, cdk]
profiles: [nextjs-aws]
paths: ['**/*.{ts,tsx}']
version: "1.0.0"
last_updated: "2026-03-27"
---

---
paths: "infra/**/*.ts,cdk/**/*.ts"
---
# CDK Watch for Rapid Testing

> 📖 **CDK Docs**: https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-watch
> Hot-reload Lambda code changes in ~5 seconds for rapid iteration

## Quick Check (30 seconds)
- [ ] `cdk watch` running during Lambda development
- [ ] Lambda changes deploy in < 10 seconds (hot-swap)
- [ ] CloudWatch logs tailing in separate terminal
- [ ] `.cdk.watch` excludes configured (tests, docs, node_modules)
- [ ] Using `--hotswap-fallback` flag for safety
- [ ] Testing with real AWS services (not LocalStack)

## Core Pattern: CDK Watch Workflow

**Golden Rule**: Test Lambda locally first, then use CDK Watch for AWS integration testing.

```bash
# Terminal 1: Start watch mode
cd infra
cdk watch --hotswap-fallback --profile dev

# Output:
# ✨ Deployment time: 3.2s
# ✨ Watching for file changes...

# Terminal 2: Tail logs
aws logs tail /aws/lambda/my-function --follow --profile dev

# Terminal 3: Test changes
# Edit lambda code → Auto-deploys in ~5 seconds
```

**Development Flow**:
```
1. Pure Node Testing (5 min)
   → Test business logic locally with Node.js
   → Fast feedback, no AWS dependencies

2. CDK Watch Testing (15 min)
   → Test AWS integrations (S3, DynamoDB, etc.)
   → Real AWS environment, fast hot-swap

3. CDK Deploy (production)
   → Final deployment with full synthesis
   → Validates infrastructure consistency
```

---

## Quick Start

### 1. Configure Exclusions (.cdk.watch)

```json
{
  "exclude": [
    "**/*.test.ts",
    "**/*.md",
    "**/node_modules/**",
    "**/dist/**",
    "**/.git/**"
  ]
}
```

### 2. Start Watch Mode

```bash
# With hot-swap for fast Lambda updates
cdk watch --hotswap-fallback --profile dev

# What it does:
# - Watches for file changes
# - Hot-swaps Lambda code (3-5 sec)
# - Falls back to full deploy if needed
```

### 3. Test Lambda Changes

```typescript
// Edit lambda/getUserHandler.ts
export const handler = async (event) => {
  console.log('New version!');  // Change code
  return { statusCode: 200 };
};

// Save → Auto-deploys in ~5 seconds
// Check Terminal 2 for new logs
```

---

## Hot-Swap vs Full Deploy

| Change Type | Hot-Swap? | Deploy Time | Command |
|-------------|-----------|-------------|---------|
| Lambda code only | ✅ Yes | 3-5 sec | Auto |
| Lambda env vars | ✅ Yes | 3-5 sec | Auto |
| Lambda IAM roles | ❌ No | 30-60 sec | Full deploy |
| Infrastructure (S3, DynamoDB) | ❌ No | 30-60 sec | Full deploy |
| Lambda in VPC | ❌ No | 30-60 sec | Full deploy |

---

## Common Issues

### Issue 1: Hot-Swap Not Working

```bash
# Check if Lambda is eligible
cdk watch --verbose --profile dev

# Common reasons:
# - Lambda is in VPC (slower deployment)
# - IAM changes detected
# - Runtime not supported (use Node.js 18+)
```

**Fix**: Use `--hotswap-fallback` to auto-switch to full deploy when needed.

### Issue 2: Slow Deployments

```bash
# Reduce files watched
# Add to .cdk.watch:
{
  "exclude": [
    "**/*.test.ts",
    "**/coverage/**",
    "**/*.md"
  ]
}
```

### Issue 3: Logs Not Showing

```bash
# Verify log group exists
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/ \
  --profile dev

# Tail specific function
aws logs tail /aws/lambda/my-function \
  --since 5m \
  --follow \
  --profile dev
```

---

## Related Rules

- **[cdk-deploy.md](./cdk-deploy.md)** - Full CDK deployment workflow
- **[lambda-typescript-esm.md](./lambda-typescript-esm.md)** - Lambda code patterns
- **[lambda-quick-reference.md](./lambda-quick-reference.md)** - Lambda troubleshooting

---

**Version**: 1.1
**Last Updated**: 2026-02-05
**Changes**: Simplified to quick reference from detailed guide
