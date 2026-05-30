/**
 * Document Service - Event Broker Adapter (Phase P1.3)
 * 
   Provides multi-broker event publishing with dead-letter queue handling
 */

import { PublisherFactory } from '../utils/publishers';
import retryHandler from '../utils/retryHandler';

/**
 * Event Broker Service - Multi-Broker Orchestration Layer
 * 
   Handles all operations related to event publishing including:
   - Route events to configured brokers (Kafka, SNS, PubSub)
   - Track publication status across multiple brokers
   - Manage dead-letter queue for failed publications
 */
class BrokerService {
  /**
   * PUBLISH EVENT - Send event to all configured brokers
   * @param eventData Event data to publish
   * @returns Publication result with status and broker breakdown
   */
  async publishEvent(eventData: any): Promise<any> {
    const eventId = `evt-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Get active brokers from configuration
    const brokers = this.getActiveBrokers();

    // Publish to each broker
    const results: Array<{ 
      broker: string; 
      status: 'published' | 'failed'; 
      error?: string; 
    }> = [];

    for (const broker of brokers) {
      try {
        const publisher = PublisherFactory.getPublisher(broker.id);
        
        // Publish event to broker
        await publisher.publish({
          topic: broker.topic,
          message: eventData,
          correlationId: eventId
        });

        results.push({ 
          broker: broker.id, 
          status: 'published' 
        });
      } catch (error: any) {
        console.error(`[BROKER_SERVICE] Failed to publish to ${broker.id}:`, error.message);
        
        // Track failed publication for DLQ
        await retryHandler.trackFailure({
          eventId,
          brokerId: broker.id,
          error: error.message
        });

        results.push({ 
          broker: broker.id, 
          status: 'failed', 
          error: error.message 
        });
      }
    }

    // Determine overall status
    const allSucceeded = results.every(r => r.status === 'published');

    return {
      id: eventId,
      event_type: eventData.event_type,
      status: allSucceeded ? 'published' : 'partial_failure',
      timestamp: new Date().toISOString(),
      results: results
    };
  }

  /**
   * BATCH PUBLISH - Publish multiple events in a single operation
   * @param events Array of event data to publish
   * @returns Batch publication results
   */
  async batchPublish(events: Array<any>): Promise<any> {
    const results: Array<{ 
      eventId: string; 
      status: 'published' | 'failed'; 
    }> = [];

    // Publish each event in sequence (for better error tracking)
    for (const eventData of events) {
      try {
        const result = await this.publishEvent(eventData);
        results.push({
          eventId: result.id,
          status: result.status === 'published' ? 'published' : 'failed'
        });
      } catch (error: any) {
        results.push({
          eventId: `evt-${Date.now()}`,
          status: 'failed',
          error: error.message
        });
      }
    }

    return {
      success: true,
      count: events.length,
      results: results
    };
  }

  /**
   * GET PUBLICATION STATUS - Check status of published event across brokers
   * @param eventId Event identifier to check
   */
  async getPublicationStatus(eventId: string): Promise<any> {
    const brokers = this.getActiveBrokers();

    // Check status for each broker
    const statuses: Array<{ 
      broker: string; 
      published: boolean; 
      delivered?: Date;
      error?: string; 
    }> = [];

    for (const broker of brokers) {
      try {
        const publisher = PublisherFactory.getPublisher(broker.id);
        
        // Check publication status via subscription/poll mechanism
        const isPublished = await publisher.isMessageDelivered(eventId);

        statuses.push({
          broker: broker.id,
          published: isPublished
        });
      } catch (error: any) {
        statuses.push({
          broker: broker.id,
          published: false,
          error: error.message
        });
      }
    }

    return {
      eventId,
      status: statuses.every(s => s.published) ? 'completed' : 'incomplete',
      results: statuses
    };
  }

  /**
   * GET ACTIVE BROKERS - List all configured and active brokers
   */
  getActiveBrokers(): Array<any> {
    return [
      { id: 'kafka', topic: 'portfolio.events', enabled: true },
      { id: 'aws-sns', topic: 'portfolio-events', enabled: true },
      { id: 'google-pubsub', topic: 'portfolio-events', enabled: true }
    ];
  }

  /**
   * ENABLE BROKER - Activate previously disabled broker
   */
  async enableBroker(brokerId: string): Promise<void> {
    console.log(`[BROKER_SERVICE] Enabling broker: ${brokerId}`);
    // Update configuration to enable broker
  }

  /**
   * DISABLE BROKER - Temporarily disable broker for maintenance
   */
  async disableBroker(brokerId: string): Promise<void> {
    console.log(`[BROKER_SERVICE] Disabling broker: ${brokerId}`);
    // Update configuration to disable broker
  }

  /**
   * REROUTE EVENT - Re-published failed event to specified broker
   * @param eventId Event identifier that failed
   * @param brokerIds Array of broker IDs to attempt re-publication
   */
  async rerouteEvent(eventId: string, brokerIds?: Array<string>): Promise<any> {
    // Get configured brokers or use provided ones
    const targets = brokerIds || this.getActiveBrokers().map(b => b.id);

    console.log(`[BROKER_SERVICE] Rerouting event ${eventId} to brokers: ${targets.join(', ')}`);

    // Re-publish to target brokers
    return await this.publishEvent({ eventId });
  }
}

// Export singleton instance of BrokerService
const brokerService = new BrokerService();

export default brokerService;
