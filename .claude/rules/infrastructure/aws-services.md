---
paths: "infra/**/*.ts,cdk/**/*.ts"
---
# AWS Services Reference

> 📖 **Complete AWS Guide**: Comprehensive AWS service patterns with Clean Architecture
> Quick reference for DynamoDB, S3, SQS, Lambda adapter patterns

## Quick Start (30 seconds)

### Most Common Stack (80% of Projects)
```typescript
// Standard serverless stack
Lambda      → Compute (serverless functions)
DynamoDB    → Database (NoSQL, serverless)
S3          → Storage (files, static assets)
API Gateway → HTTP API (REST endpoints)
CloudWatch  → Logging (JSON logs)
Secrets Mgr → Secrets (API keys, credentials)
```

### Decision Tree
```
Need compute?   → Lambda (serverless) or ECS (containers)
Need database?  → DynamoDB (NoSQL) or RDS Aurora (SQL)
Need storage?   → S3 (files) or EFS (filesystem)
Need queue?     → SQS (jobs) or EventBridge (events)
Need auth?      → Cognito (users) or IAM (services)
```

### Quick Check
- [ ] All AWS SDK calls in `modules/adapters/` layer only
- [ ] Domains never import AWS SDK directly
- [ ] Using AWS SDK v3 (modular), not v2 (monolithic)
- [ ] Adapters implement domain-defined interfaces
- [ ] Error handling includes retries (exponential backoff)
- [ ] LocalStack configured for local development
- [ ] CDK infrastructure defined (not manual console)

---

## Core Pattern: AWS Service Adapter

**Golden Rule**: Domains define interfaces, Adapters implement with AWS SDK

```typescript
// Step 1: Domain defines interface (NO AWS)
// 01_domains/user/types.ts
export interface UserRepository {
  get(id: UserId): Promise<User | null>;
  put(user: User): Promise<void>;
}

// Step 2: Adapter implements with AWS SDK
// 02_modules/users/adapters/dynamoUserAdapter.ts
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand } from '@aws-sdk/lib-dynamodb';

export class DynamoUserAdapter implements UserRepository {
  async get(id: UserId): Promise<User | null> {
    const result = await docClient.send(
      new GetCommand({ TableName: TABLE_NAME, Key: { id } })
    );
    return result.Item ? this.mapToUser(result.Item) : null;
  }
}

// Step 3: Use in Lambda
// lambda/getUserHandler.ts
const userRepo = new DynamoUserAdapter();
const user = await userRepo.get(userId);
```

**Why this pattern?**
- ✅ Business logic doesn't depend on AWS
- ✅ Can swap AWS for other cloud providers
- ✅ Easy to test with mocks
- ✅ Type-safe with TypeScript

---

## AWS Service Patterns (Detailed Reference)

### AWS SDK v3 Installation

```bash
# Install only the services you use (tree-shakeable)
npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb
npm install @aws-sdk/client-s3
npm install @aws-sdk/client-sqs
npm install @aws-sdk/client-lambda
```

```typescript
// ✅ CORRECT: Import specific clients (SDK v3)
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';

// ❌ WRONG: Don't use AWS SDK v2
import AWS from 'aws-sdk'; // Old, monolithic
```

---

## DynamoDB Adapter Pattern

### Domain Types (No AWS)

```typescript
// 01_domains/user/types.ts
import { UserId } from '@/00_kernel/types/user';

export interface User {
  readonly id: UserId;
  readonly name: string;
  readonly email: string;
  readonly createdAt: string;
}

export interface UserRepository {
  get(id: UserId): Promise<User | null>;
  put(user: User): Promise<void>;
  query(email: string): Promise<User[]>;
}
```

### DynamoDB Adapter (AWS-specific)

```typescript
// 02_modules/users/adapters/dynamoUserAdapter.ts
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
  QueryCommand,
} from '@aws-sdk/lib-dynamodb';
import { User, UserRepository } from '@/01_domains/user/types';
import { UserId, createUserId } from '@/00_kernel/types/user';

const client = new DynamoDBClient({
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.DYNAMODB_ENDPOINT, // LocalStack support
});

const docClient = DynamoDBDocumentClient.from(client);

const TABLE_NAME = process.env.USERS_TABLE || 'users-dev';

export class DynamoUserAdapter implements UserRepository {
  async get(id: UserId): Promise<User | null> {
    try {
      const result = await docClient.send(
        new GetCommand({
          TableName: TABLE_NAME,
          Key: { id },
        })
      );

      if (!result.Item) {
        return null;
      }

      // Map DynamoDB item to domain type
      return {
        id: createUserId(result.Item.id),
        name: result.Item.name,
        email: result.Item.email,
        createdAt: result.Item.createdAt,
      };
    } catch (error) {
      console.error('DynamoDB get error:', error);
      throw new Error(`Failed to get user ${id}`);
    }
  }

  async put(user: User): Promise<void> {
    try {
      await docClient.send(
        new PutCommand({
          TableName: TABLE_NAME,
          Item: {
            id: user.id,
            name: user.name,
            email: user.email,
            createdAt: user.createdAt,
          },
        })
      );
    } catch (error) {
      console.error('DynamoDB put error:', error);
      throw new Error(`Failed to save user ${user.id}`);
    }
  }

  async query(email: string): Promise<User[]> {
    try {
      const result = await docClient.send(
        new QueryCommand({
          TableName: TABLE_NAME,
          IndexName: 'email-index',
          KeyConditionExpression: 'email = :email',
          ExpressionAttributeValues: {
            ':email': email,
          },
        })
      );

      return (result.Items || []).map((item) => ({
        id: createUserId(item.id),
        name: item.name,
        email: item.email,
        createdAt: item.createdAt,
      }));
    } catch (error) {
      console.error('DynamoDB query error:', error);
      throw new Error(`Failed to query users by email ${email}`);
    }
  }
}
```

### Usage in Lambda

```typescript
// 02_modules/users/lambda/getUserHandler.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DynamoUserAdapter } from '../adapters/dynamoUserAdapter.js';
import { createUserId } from '@/00_kernel/types/user';

const userRepo = new DynamoUserAdapter();

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const userId = createUserId(event.pathParameters?.id || '');

  const user = await userRepo.get(userId);

  if (!user) {
    return {
      statusCode: 404,
      body: JSON.stringify({ error: 'User not found' }),
    };
  }

  return {
    statusCode: 200,
    body: JSON.stringify(user),
  };
};
```

---

## S3 Adapter Pattern

### Domain Types

```typescript
// 01_domains/file/types.ts
export type FileId = string & { readonly __brand: 'FileId' };

export interface FileMetadata {
  readonly id: FileId;
  readonly filename: string;
  readonly contentType: string;
  readonly size: number;
  readonly uploadedAt: string;
}

export interface FileStorage {
  upload(file: Buffer, metadata: FileMetadata): Promise<string>;
  download(id: FileId): Promise<Buffer>;
  getSignedUrl(id: FileId, expiresIn: number): Promise<string>;
  delete(id: FileId): Promise<void>;
}
```

### S3 Adapter

```typescript
// 02_modules/files/adapters/s3FileAdapter.ts
import { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { FileId, FileMetadata, FileStorage } from '@/01_domains/file/types';

const client = new S3Client({
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.S3_ENDPOINT, // LocalStack support
  forcePathStyle: !!process.env.S3_ENDPOINT, // Required for LocalStack
});

const BUCKET_NAME = process.env.FILES_BUCKET || 'files-dev';

export class S3FileAdapter implements FileStorage {
  async upload(file: Buffer, metadata: FileMetadata): Promise<string> {
    const key = `uploads/${metadata.id}/${metadata.filename}`;

    try {
      await client.send(
        new PutObjectCommand({
          Bucket: BUCKET_NAME,
          Key: key,
          Body: file,
          ContentType: metadata.contentType,
          Metadata: {
            fileId: metadata.id,
            uploadedAt: metadata.uploadedAt,
          },
        })
      );

      return `s3://${BUCKET_NAME}/${key}`;
    } catch (error) {
      console.error('S3 upload error:', error);
      throw new Error(`Failed to upload file ${metadata.id}`);
    }
  }

  async download(id: FileId): Promise<Buffer> {
    try {
      const result = await client.send(
        new GetObjectCommand({
          Bucket: BUCKET_NAME,
          Key: `uploads/${id}`,
        })
      );

      if (!result.Body) {
        throw new Error('Empty file body');
      }

      return Buffer.from(await result.Body.transformToByteArray());
    } catch (error) {
      console.error('S3 download error:', error);
      throw new Error(`Failed to download file ${id}`);
    }
  }

  async getSignedUrl(id: FileId, expiresIn: number = 3600): Promise<string> {
    const command = new GetObjectCommand({
      Bucket: BUCKET_NAME,
      Key: `uploads/${id}`,
    });

    return await getSignedUrl(client, command, { expiresIn });
  }

  async delete(id: FileId): Promise<void> {
    try {
      await client.send(
        new DeleteObjectCommand({
          Bucket: BUCKET_NAME,
          Key: `uploads/${id}`,
        })
      );
    } catch (error) {
      console.error('S3 delete error:', error);
      throw new Error(`Failed to delete file ${id}`);
    }
  }
}
```

---

## SQS Adapter Pattern

### Domain Types

```typescript
// 01_domains/events/types.ts
export type EventId = string & { readonly __brand: 'EventId' };

export interface Event<T = unknown> {
  readonly id: EventId;
  readonly type: string;
  readonly payload: T;
  readonly timestamp: string;
}

export interface EventQueue {
  publish<T>(event: Event<T>): Promise<void>;
  subscribe<T>(queueName: string, handler: (event: Event<T>) => Promise<void>): Promise<void>;
}
```

### SQS Adapter

```typescript
// 02_modules/events/adapters/sqsEventAdapter.ts
import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';
import { Event, EventQueue } from '@/01_domains/events/types';

const client = new SQSClient({
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.SQS_ENDPOINT, // LocalStack support
});

export class SqsEventAdapter implements EventQueue {
  async publish<T>(event: Event<T>): Promise<void> {
    const queueUrl = process.env.EVENTS_QUEUE_URL || '';

    try {
      await client.send(
        new SendMessageCommand({
          QueueUrl: queueUrl,
          MessageBody: JSON.stringify(event),
          MessageAttributes: {
            eventType: {
              DataType: 'String',
              StringValue: event.type,
            },
          },
        })
      );
    } catch (error) {
      console.error('SQS publish error:', error);
      throw new Error(`Failed to publish event ${event.id}`);
    }
  }

  async subscribe<T>(
    queueName: string,
    handler: (event: Event<T>) => Promise<void>
  ): Promise<void> {
    const queueUrl = process.env[`${queueName}_QUEUE_URL`] || '';

    // Poll for messages (in Lambda, use SQS event source instead)
    while (true) {
      try {
        const result = await client.send(
          new ReceiveMessageCommand({
            QueueUrl: queueUrl,
            MaxNumberOfMessages: 10,
            WaitTimeSeconds: 20, // Long polling
          })
        );

        if (!result.Messages || result.Messages.length === 0) {
          continue;
        }

        for (const message of result.Messages) {
          const event = JSON.parse(message.Body || '{}') as Event<T>;

          try {
            await handler(event);

            // Delete message after successful processing
            await client.send(
              new DeleteMessageCommand({
                QueueUrl: queueUrl,
                ReceiptHandle: message.ReceiptHandle,
              })
            );
          } catch (error) {
            console.error('Event handler error:', error);
            // Message will be retried or go to DLQ
          }
        }
      } catch (error) {
        console.error('SQS poll error:', error);
        await new Promise((resolve) => setTimeout(resolve, 5000));
      }
    }
  }
}
```

---

## Error Handling and Retries

### Exponential Backoff Utility

```typescript
// 00_kernel/utils/retry.ts

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
  } = {}
): Promise<T> {
  const { maxRetries = 3, baseDelay = 100, maxDelay = 5000 } = options;

  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === maxRetries) {
        break;
      }

      // Exponential backoff with jitter
      const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
      const jitter = Math.random() * 0.3 * delay;

      await new Promise((resolve) => setTimeout(resolve, delay + jitter));
    }
  }

  throw lastError;
}
```

### Usage in Adapters

```typescript
// 02_modules/users/adapters/dynamoUserAdapter.ts

import { withRetry } from '@/00_kernel/utils/retry';

export class DynamoUserAdapter implements UserRepository {
  async get(id: UserId): Promise<User | null> {
    return withRetry(
      async () => {
        const result = await docClient.send(
          new GetCommand({
            TableName: TABLE_NAME,
            Key: { id },
          })
        );

        return result.Item ? this.mapToUser(result.Item) : null;
      },
      { maxRetries: 3, baseDelay: 100 }
    );
  }
}
```

---

## LocalStack for Local Development

### docker-compose.yml

```yaml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - '4566:4566'
    environment:
      - SERVICES=dynamodb,s3,sqs,lambda
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
    volumes:
      - './localstack-data:/tmp/localstack/data'
```

### Environment Configuration

```typescript
// src/config/aws.ts

export const AWS_CONFIG = {
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.AWS_ENDPOINT || undefined, // http://localhost:4566 for LocalStack
  credentials:
    process.env.NODE_ENV === 'development'
      ? {
          accessKeyId: 'test',
          secretAccessKey: 'test',
        }
      : undefined,
};

// Use in adapters
const client = new DynamoDBClient(AWS_CONFIG);
```

### .env.local

```bash
# Local development with LocalStack
AWS_REGION=us-east-1
AWS_ENDPOINT=http://localhost:4566
DYNAMODB_ENDPOINT=http://localhost:4566
S3_ENDPOINT=http://localhost:4566
SQS_ENDPOINT=http://localhost:4566

# Table/bucket names
USERS_TABLE=users-local
FILES_BUCKET=files-local
EVENTS_QUEUE_URL=http://localhost:4566/000000000000/events-local
```

---

## CDK Infrastructure Examples

See `cdk-deploy.md` for complete CDK patterns.

```typescript
// infra/lib/stacks/backend-stack.ts
import { Stack, StackProps, Duration, RemovalPolicy } from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';

export class BackendStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // DynamoDB Table
    const usersTable = new dynamodb.Table(this, 'UsersTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
    });

    // S3 Bucket
    const filesBucket = new s3.Bucket(this, 'FilesBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    // SQS Queue with DLQ
    const dlq = new sqs.Queue(this, 'EventsDLQ', {
      retentionPeriod: Duration.days(14),
    });

    const eventsQueue = new sqs.Queue(this, 'EventsQueue', {
      visibilityTimeout: Duration.seconds(300),
      deadLetterQueue: {
        queue: dlq,
        maxReceiveCount: 3,
      },
    });
  }
}
```

---

## Related Rules

- **[cdk-deploy.md](./cdk-deploy.md)** - CDK deployment workflow
- **[lambda-typescript-esm.md](./lambda-typescript-esm.md)** - Lambda + ESM patterns
- **[clean-architecture.md](../architecture/clean-architecture.md)** - Layer separation
- **[adapters.md](../architecture/adapters.md)** - Adapter pattern
- **[query-transactions.md](../backend/query-transactions.md)** - DynamoDB transactions

---

**Version**: 1.1
**Last Updated**: 2026-02-05
**Changes**: Added Quick Start section, improved navigation
