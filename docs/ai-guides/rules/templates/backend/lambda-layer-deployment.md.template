---
category: "backend"
title: "Lambda Layer Deployment"
description: "Lambda layers"
tags: [typescript, aws, lambda]
profiles: [nextjs-aws]
paths: ['**/*.{ts,tsx}']
version: "1.0.0"
last_updated: "2026-03-27"
---

---
paths: "infra/layers/**/*,cdk/layers/**/*"
---
# Lambda Layer Deployment

> 📖 **AWS Docs**: https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html
> Lambda Layers for shared code across functions (immutable versions)

## Quick Check (30 seconds)
- [ ] Layer version created with CDK (not manual console)
- [ ] Shared dependencies in layer (not duplicated per function)
- [ ] Layer size < 50MB zipped (< 250MB unzipped)
- [ ] Layer ARN versioned and published to Parameter Store
- [ ] CDK cache cleared before layer updates (`rm -rf cdk.out`)
- [ ] Lambda functions reference latest layer version

## Core Pattern: Immutable Layer Versions

**Golden Rule**: Layer versions are immutable. Update = New version, not modify existing.

```
Lambda Layer Lifecycle:
├─ Version 1: Initial code
├─ Version 2: Bug fix (Version 1 still exists)
└─ Version N: Current code (Versions 1-N still exist)

Lambda Function references specific ARN:
└─ arn:aws:lambda:region:account:layer:name:N
```

**Key Point**: Changing layer source code ≠ Updating layer version

---

## Quick Start

### 1. Create Layer Directory

```bash
mkdir -p infra/layers/common-layer/nodejs/node_modules
cd infra/layers/common-layer/nodejs

# Install shared dependencies
npm init -y
npm install lodash date-fns zod
```

### 2. Define Layer in CDK

```typescript
// infra/lib/layers-stack.ts
import { LayerVersion, Runtime, Code } from 'aws-cdk-lib/aws-lambda';

const commonLayer = new LayerVersion(this, 'CommonLayer', {
  code: Code.fromAsset('layers/common-layer'),
  compatibleRuntimes: [Runtime.NODEJS_18_X, Runtime.NODEJS_20_X],
  description: 'Shared utilities and dependencies',
});

// Export ARN for use in other stacks
new CfnOutput(this, 'CommonLayerArn', {
  value: commonLayer.layerVersionArn,
  exportName: 'CommonLayerArn',
});
```

### 3. Use Layer in Lambda

```typescript
// infra/lib/lambda-stack.ts
import { Function, Runtime, Code } from 'aws-cdk-lib/aws-lambda';
import { Fn } from 'aws-cdk-lib';

const commonLayerArn = Fn.importValue('CommonLayerArn');

new Function(this, 'MyFunction', {
  runtime: Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: Code.fromAsset('lambda/my-function'),
  layers: [
    LayerVersion.fromLayerVersionArn(this, 'Layer', commonLayerArn)
  ],
});
```

---

## Updating Layers

### Problem: CDK Not Detecting Layer Changes

**Symptom**: Changed layer code, ran `cdk deploy`, Lambda still uses old version.

**Cause**: CDK caches asset hashes and doesn't detect file changes.

**Solution A: Clear CDK Cache** (Recommended)

```bash
# 1. Clear cache
rm -rf cdk.out

# 2. Re-synthesize (recalculates file hashes)
cdk synth

# 3. Deploy
cdk deploy --all --profile dev
```

**Solution B: Force New Version**

```bash
# Add version comment to force new hash
// layers/common-layer/nodejs/version.js
module.exports = { version: '1.0.1' }; // Increment version
```

---

## Manual Layer Publishing (Emergency)

```bash
# 1. Package layer
cd infra
zip -r /tmp/layer.zip layers/common-layer/nodejs

# 2. Publish new version
aws lambda publish-layer-version \
  --layer-name my-common-layer \
  --zip-file fileb:///tmp/layer.zip \
  --compatible-runtimes nodejs20.x \
  --profile dev

# Returns:
# {
#   "Version": 15,
#   "LayerVersionArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-common-layer:15"
# }

# 3. Update Lambda to use new version
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:us-east-1:123456789012:layer:my-common-layer:15 \
  --profile dev
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| "Layer too large" | Size > 50MB zipped | Remove dev dependencies, split into multiple layers |
| "Module not found" | Layer not attached | Verify layers array in Lambda config |
| "Wrong runtime" | Runtime mismatch | Ensure compatibleRuntimes matches function runtime |
| "Old code running" | CDK cache | `rm -rf cdk.out && cdk deploy` |

---

## Best Practices

### Layer Structure

```
layers/common-layer/
├── nodejs/
│   ├── node_modules/     # Dependencies (npm install here)
│   │   ├── lodash/
│   │   └── date-fns/
│   └── shared/           # Custom code
│       ├── utils.js
│       └── constants.js
└── package.json
```

### Lambda Import Path

```typescript
// Lambda can import directly (no path prefix needed)
import _ from 'lodash';  // From node_modules
import { formatDate } from '/opt/nodejs/shared/utils.js';  // Custom code
```

**Note**: `/opt/nodejs/` is where AWS mounts the layer.

### Size Optimization

```bash
# Production dependencies only
cd layers/common-layer/nodejs
npm install --production

# Check size
du -sh .
# Should be < 50MB zipped
```

---

## Related Rules

- **[lambda-typescript-esm.md](./lambda-typescript-esm.md)** - Lambda + ESM patterns
- **[cdk-deploy.md](./cdk-deploy.md)** - CDK deployment workflow
- **[lambda-quick-reference.md](./lambda-quick-reference.md)** - Lambda troubleshooting

---

**Version**: 1.1
**Last Updated**: 2026-02-05
**Changes**: Simplified to quick reference, added CDK cache solution
