/**
 * Event Broker Adapter - Retry Handler (Phase P1.3)
 * 
   Provides exponential backoff retry logic for failed messages
 */

import { EventEmitter } from 'events';

/**
 * Retry Configuration Options
 */
export interface RetryConfig {
  maxAttempts: number; // Maximum retry attempts (default: 3)
  initialDelayMs: number; // Initial delay between retries in milliseconds (default: 1000)
  maxDelayMs: number; // Maximum delay between retries in milliseconds (default: 60000)
  backoffMultiplier: number; // Multiplier for exponential backoff (default: 2)
  randomizationFactor: number; // Randomization factor for jitter (default: 0.1)
}

/**
 * Default retry configuration
 */
const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  initialDelayMs: 1000,
  maxDelayMs: 60000,
  backoffMultiplier: 2,
  randomizationFactor: 0.1
};

/**
 * Retry Handler - Exponential Backoff with Jitter for Failed Messages
 */
class RetryHandler extends EventEmitter {
  private config: RetryConfig;
  private retryCountMap: Map<string, number>; // Track retry counts per message
  private failureReasonMap: Map<string, string>; // Track failure reasons

  constructor(config?: Partial<RetryConfig>) {
    super();
    
    this.config = { ...DEFAULT_RETRY_CONFIG, ...config };
    this.retryCountMap = new Map();
    this.failureReasonMap = new Map();
  }

  /**
   * Track retry for failed message
   * @param options Retry tracking options
   */
  async trackRetry(options: {
    eventId: string;
    brokerId: string;
    retryCount?: number;
  }): Promise<RetryResult> {
    const { eventId, brokerId, retryCount = 1 } = options;

    // Increment retry count for this message+broker combination
    const key = `${eventId}-${brokerId}`;
    const currentRetryCount = (this.retryCountMap.get(key) || 0) + 1;

    // Update retry count map
    this.retryCountMap.set(key, currentRetryCount);

    // Calculate delay for next retry using exponential backoff with jitter
    const delayMs = this.calculateDelay(currentRetryCount);

    // Emit retry event for monitoring
    this.emit('retry', {
      eventId,
      brokerId,
      retryCount: currentRetryCount,
      maxAttempts: this.config.maxAttempts,
      delayMs
    });

    return {
      retry_count: currentRetryCount,
      status: currentRetryCount < this.config.maxAttempts ? 'retry_scheduled' : 'max_attempts_exceeded',
      next_retry_after_ms: currentRetryCount < this.config.maxAttempts ? delayMs : 0
    };
  }

  /**
   * Track failure from broker service
   */
  async trackFailure(options: {
    eventId: string;
    brokerId: string;
    error: string;
  }): Promise<void> {
    const { eventId, brokerId, error } = options;

    // Store failure reason for this message+broker combination
    const key = `${eventId}-${brokerId}`;
    this.failureReasonMap.set(key, error);

    console.log(`[RETRY_HANDLER] Tracking failure for ${key}: ${error}`);
  }

  /**
   * Get remaining retries for message+broker combination
   */
  getRemainingRetries(eventId: string, brokerId: string): number {
    const maxAttempts = this.config.maxAttempts;
    const key = `${eventId}-${brokerId}`;
    const currentRetryCount = this.retryCountMap.get(key) || 0;

    return Math.max(0, maxAttempts - currentRetryCount);
  }

  /**
   * Get failure reason for message+broker combination
   */
  getFailureReason(eventId: string, brokerId: string): string | null {
    const key = `${eventId}-${brokerId}`;
    return this.failureReasonMap.get(key) || null;
  }

  /**
   * Calculate delay with exponential backoff and jitter
   */
  private calculateDelay(attempt: number): number {
    // Exponential backoff calculation
    let delay = this.config.initialDelayMs * Math.pow(this.config.backoffMultiplier, attempt - 1);

    // Add jitter to avoid thundering herd problem
    const jitter = Math.random() * delay * this.config.randomizationFactor;

    // Cap at maximum delay
    return Math.min(delay + jitter, this.config.maxDelayMs);
  }

  /**
   * Get retry configuration
   */
  getConfig(): RetryConfig {
    return this.config;
  }

  /**
   * Reset retry state for all messages
   */
  resetAll(): void {
    this.retryCountMap.clear();
    this.failureReasonMap.clear();
    console.log('[RETRY_HANDLER] Reset all retry states');
  }

  /**
   * Get summary statistics for all tracked messages
   */
  getStatistics(): { totalRetries: number; failedMessages: number } {
    const totalRetries = Array.from(this.retryCountMap.values()).reduce((sum, count) => sum + count, 0);
    const failedMessages = Array.from(this.retryCountMap.keys()).filter(key => 
      this.retryCountMap.get(key)! >= this.config.maxAttempts
    ).length;

    return { totalRetries, failedMessages };
  }
}

// Export singleton instance for use across event broker adapter
const retryHandler = new RetryHandler();

export default retryHandler;
export { DEFAULT_RETRY_CONFIG, type RetryConfig };
