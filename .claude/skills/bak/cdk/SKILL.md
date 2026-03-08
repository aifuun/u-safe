---
name: cdk
description: |
  AWS CDK deployment automation - synthesize, deploy, destroy stacks.
  Infrastructure as code management.
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(npm *), Bash(aws *), Read
context: fork
agent: general-purpose
---

# CDK Deployer

Manage AWS infrastructure with CDK.

## Task

Automate AWS deployments:
1. **Synth** - Generate CloudFormation
2. **Diff** - Show what will change
3. **Deploy** - Apply infrastructure changes
4. **Destroy** - Tear down stacks (careful!)
5. **Status** - Check current state

## Commands

```
/cdk synth               # Generate CloudFormation
/cdk diff                # Show changes
/cdk deploy              # Deploy to AWS
/cdk destroy             # Destroy stack (requires approval)
/cdk status              # Check stack status
```

## Workflow

```
1. cdk synth
   ↓ (generates CloudFormation)
2. cdk diff
   ↓ (review changes)
3. cdk deploy
   ↓ (prompts: continue? AWS credentials OK? etc.)
4. ✅ Stack updated
```

## Safety

- Requires AWS credentials
- `cdk deploy` shows diff before deploying
- `cdk destroy` requires explicit confirmation
- Automatic rollback on failure

---

Manages:
- Infrastructure as code
- AWS resource creation
- Deployment automation
- Stack cleanup
