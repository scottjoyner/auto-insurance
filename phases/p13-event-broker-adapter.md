# Phase P1.3 Event Broker Adapter - Kafka/SNS/PubSub Integration

## ✅ Phase Status: Ready to Implement

This phase creates a comprehensive Event Broker Adapter (services/event-broker-adapter) with support for multiple messaging brokers including Apache Kafka, AWS SNS, and Google Pub/Sub, plus dead-letter queue handling.

---

## 🎯 Features

### Supported Brokers:
- ✅ Apache Kafka - High-throughput event streaming
- ✅ AWS SNS - Pub/sub notification service
- ✅ Google Cloud Pub/Sub - Enterprise pub/sub platform

### Core Capabilities:
- ✅ Event publishing to multiple brokers simultaneously
- ✅ Dead-letter queue (DLQ) with automatic retry
- ✅ Message acknowledgment and tracking
- ✅ Schema validation before publication
- ✅ Broker failover and health monitoring

---

## 📁 Service Architecture

```
services/event-broker-adapter/
├── routes/
│   ├── events/           - Event publishing endpoints
│   └── brokers/          - Broker management endpoints
├── services/
│   ├── brokerService.ts  - Multi-broker orchestration
│   └── dlqService.ts     - Dead-letter queue handling
├── schemas/
│   ├── events-schema.ts  - Event message schema definitions
│   └── broker-config.ts  - Broker configuration schemas
└── utils/
    ├── publishers/       - Kafka/SNS/PubSub publisher clients
    └── retryHandler.ts   - Retry logic and backoff strategies
```

---

## 🚀 Quick Start Commands

### Installation:
```bash
cd services/event-broker-adapter
npm install kafka-node aws-sdk google-cloud-pubsub
```

### Configure Environment:
```bash
# Kafka Configuration
export KAFKA_BROKERS="localhost:9092"
export KAFKA_TOPIC="portfolio.events"

# AWS SNS Configuration  
export SNS_REGION="us-east-1"
export SNS_TOPIC_ARN="arn:aws:sns:us-east-1:123456789:portfolio-events"

# Google Pub/Sub Configuration
export PUBSUB_PROJECT_ID="your-project-id"
export PUBSUB_TOPIC_NAME="projects/YOUR_PROJECT/topics/portfolio_events"
```

### Run Development Server:
```bash
npm start
# Service available at http://localhost:3003
```

---

## 📖 API Documentation Quick Reference

### Event Publishing:
- `POST /api/events/publish` - Publish event to configured brokers
- `POST /api/events/batch` - Batch publish multiple events
- `GET /api/events/:eventId/status` - Check publication status

### Broker Management:
- `GET /api/brokers/health` - Health check for all brokers
- `GET /api/brokers/config` - Get current broker configuration
- `POST /api/brokers/update` - Update broker configuration
- `DELETE /api/brokers/disable/:brokerId` - Disable broker temporarily

### Dead-Letter Queue:
- `GET /api/dlq/messages` - List DLQ messages
- `POST /api/dlq/retry/:messageId` - Retry failed message
- `POST /api/dlq/purge/:ageInHours` - Purge old DLQ messages

---

## 🔄 Dead-Letter Queue Flow

### Automatic DLQ Behavior:
1. Event published to broker
2. If acknowledgment fails after max retries (default: 3)
3. Message moved to dead-letter queue with failure reason
4. DLQ message includes retry count and error details

### Manual DLQ Operations:
- **Retry**: Re-attempt failed message to original broker
- **Reprocess**: Reprocess with modified payload
- **Discard**: Permanently remove from DLQ (requires auth)

---

## 📊 Event Schema Definition

All published events follow this schema:

```json
{
  "event_id": "evt-xxx",
  "event_type": "quote_submitted" | "policy_bound" | etc.,
  "payload": { ... },
  "metadata": {
    "source": "api-service",
    "timestamp": "2024-06-15T10:30:00Z",
    "correlation_id": "corr-xxx"
  }
}
```

---

## 🔐 Broker Health Monitoring

### Health Check Response:
```json
{
  "brokers": [
    {
      "id": "kafka",
      "status": "healthy",
      "latency_ms": 15,
      "last_heartbeat": "2024-06-15T10:30:00Z"
    },
    {
      "id": "aws-sns",
      "status": "degraded",
      "latency_ms": 250,
      "last_heartbeat": "2024-06-15T10:28:00Z"
    }
  ]
}
```

---

## 📚 Summary

Phase P1.3 creates a robust event broker adapter supporting Kafka, SNS, and Pub/Sub with comprehensive dead-letter queue handling for production reliability.

**Status**: ✅ Phase P1.3 Ready to Implement
