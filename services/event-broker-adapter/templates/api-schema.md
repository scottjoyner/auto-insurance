# Event Broker Configuration Schema (Phase P1.3)

## Base Configuration Required Fields:

### Kafka Configuration:
- `KAFKA_BROKERS` - Comma-separated broker addresses (e.g., "localhost:9092")
- `KAFKA_CLIENT_ID` - Client identifier for Kafka connections
- `KAFKA_TOPIC` - Topic name for portfolio events

### AWS SNS Configuration:
- `SNS_REGION` - AWS region for SNS endpoint (default: "us-east-1")
- `SNS_TOPIC_ARN` - ARN of SNS topic for portfolio events

### Google Pub/Sub Configuration:
- `PUBSUB_PROJECT_ID` - Google Cloud project ID
- `PUBSUB_TOPIC_NAME` - Full topic name including project path

---

## API Schema Documentation:

### POST /api/events/publish

Publishes an event to all configured brokers. Your request body should include:

**Required Fields:**
- `event_type` (string) - Event type identifier (e.g., "quote_submitted", "policy_bound")
- `payload` (object) - Event payload with business data

**Optional Fields:**
- `correlation_id` (string) - Traceability correlation ID
- `source` (string) - Origin service name

### POST /api/events/batch

Publishes multiple events in batch. Your request body:

```json
{
  "events": [
    {
      "event_type": "quote_submitted",
      "payload": {"..."}
    },
    {
      "event_type": "policy_bound", 
      "payload": {"..."}
    }
  ]
}
```

### GET /api/events/:eventId/status

Checks publication status for specific event. Returns status across all brokers.

---

## Dead-Letter Queue Handling:

Failed messages are automatically tracked and moved to DLQ after max retries (default: 3). DLQ includes retry history, failure reasons, and metadata for manual reprocessing if needed.

---

## Summary

Phase P1.3 creates a multi-broker event adapter supporting Kafka, AWS SNS, and Google PubSub with dead-letter queue handling for production reliability. All routes, services, utilities, and documentation are complete.

**Status**: ✅ Phase P1.3 Complete (Ready for Production)
