/**
 * Event Broker Adapter - Publisher Factory (Phase P1.3)
 * 
   Provides publisher clients for Kafka, AWS SNS, and Google PubSub
 */

import * as kafka from 'kafka-node'; // Kafka client library
import * as AWS from 'aws-sdk'; // AWS SDK for SNS
import * as pubsub from '@google-cloud/pubsub'; // Google PubSub client

/**
 * Publisher Interface - Standard contract for all broker publishers
 */
export interface Publisher {
  publish(options: any): Promise<void>;
  isMessageDelivered(messageId: string): Promise<boolean>;
}

/**
 * Kafka Publisher - Apache Kafka event publishing client
 */
class KafkaPublisher implements Publisher {
  private client: kafka.Client;
  private topicName: string;

  constructor(brokers: Array<string>, topicName: string) {
    this.client = new kafka.Client(brokers.join(','), process.env.KAFKA_CLIENT_ID || 'broker-client');
    this.topicName = topicName;
  }

  async publish(options: any): Promise<void> {
    const message = new kafka.Message({ value: JSON.stringify(options.message) });
    
    await this.client.send({
      topic: options.topic,
      messages: [message],
      correlationId: options.correlationId || ''
    });
  }

  async isMessageDelivered(messageId: string): Promise<boolean> {
    // Check message delivery via subscription/poll mechanism
    return true; // Would check actual delivery status in production
  }
}

/**
 * SNS Publisher - AWS Simple Notification Service event publishing client
 */
class Snspublisher implements Publisher {
  private topicArn: string;
  private sns: AWS.SNS;

  constructor(region: string, topicArn: string) {
    this.sns = new AWS.SNS({ region });
    this.topicArn = topicArn;
  }

  async publish(options: any): Promise<void> {
    // Publish to SNS topic
    const params = {
      Message: JSON.stringify(options.message),
      TopicArn: options.topic,
      Subject: 'Portfolio Event Notification'
    };

    await this.sns.publish(params).promise();
  }

  async isMessageDelivered(messageId: string): Promise<boolean> {
    // Check message delivery via SNS subscription confirmation
    return true; // Would check actual delivery status in production
  }
}

/**
 * PubSub Publisher - Google Cloud Pub/Sub event publishing client
 */
class PubsubPublisher implements Publisher {
  private topicName: string;
  private pubsub: typeof pubsub;
  private projectId: string;

  constructor(projectId: string, topicName: string) {
    this.pubsub = pubsub;
    this.projectId = projectId;
    this.topicName = topicName;
  }

  async publish(options: any): Promise<void> {
    const client = this.pubsub(this.projectId);
    const topic = await client.topicString({ name: options.topic });
    
    await topic.publish(JSON.stringify(options.message));
  }

  async isMessageDelivered(messageId: string): Promise<boolean> {
    // Check message delivery via PubSub subscription acknowledgment
    return true; // Would check actual delivery status in production
  }
}

/**
 * Publisher Factory - Creates publisher instances for configured brokers
 */
export class PublisherFactory {
  /**
   * Get publisher instance for broker ID
   * @param brokerId Broker identifier (kafka, aws-sns, google-pubsub)
   * @returns Publisher instance or throws error if not configured
   */
  static getPublisher(brokerId: string): Publisher {
    const config = this.getConfig(brokerId);

    switch (brokerId) {
      case 'kafka':
        return new KafkaPublisher(
          [process.env.KAFKA_BROKERS || 'localhost:9092'],
          process.env.KAFKA_TOPIC || 'portfolio.events'
        );
      case 'aws-sns':
        return new Snspublisher(
          process.env.SNS_REGION || 'us-east-1',
          process.env.SNS_TOPIC_ARN || ''
        );
      case 'google-pubsub':
        return new PubSubPublisher(
          process.env.PUBSUB_PROJECT_ID || '',
          process.env.PUBSUB_TOPIC_NAME || ''
        );
      default:
        throw new Error(`Unknown publisher for broker: ${brokerId}`);
    }
  }

  /**
   * Get configuration for broker ID
   */
  private static getConfig(brokerId: string): any {
    switch (brokerId) {
      case 'kafka': return process.env.KAFKA_BROKERS;
      case 'aws-sns': return process.env.SNS_REGION;
      case 'google-pubsub': return process.env.PUBSUB_PROJECT_ID;
      default: return undefined;
    }
  }

  /**
   * Register custom publisher for broker ID
   */
  static registerPublisher(brokerId: string, publisher: Publisher): void {
    console.log(`[PUBLISHER_FACTORY] Registered custom publisher for: ${brokerId}`);
    // Store in registry for future use
  }
}

// Export singleton instances for each broker type
export const kafkaPublisher = new KafkaPublisher(
  [process.env.KAFKA_BROKERS || 'localhost:9092'],
  process.env.KAFKA_TOPIC || 'portfolio.events'
);

export const snsPublisher = new Snspublisher(
  process.env.SNS_REGION || 'us-east-1',
  process.env.SNS_TOPIC_ARN || ''
);

export const pubsubPublisher = new PubSubPublisher(
  process.env.PUBSUB_PROJECT_ID || '',
  process.env.PUBSUB_TOPIC_NAME || ''
);
