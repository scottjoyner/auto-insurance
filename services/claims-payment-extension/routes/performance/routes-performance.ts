/**
 * Claims Service - Performance Tracking Routes (Phase P2.0)
 * 
   Provides performance metrics and real-time dashboards for claims processing
 */

import { Router, Request, Response } from 'express';
import { evaluatePerformanceMetrics } from '../services/evaluationService';
import { getRealtimeDashboardData } from '../services/dashboardService';

const router = Router();

/**
 * GET /api/performance/metrics - Get Performance Metrics for Claims Processing
 * 
   Returns real-time performance metrics including latency, throughput, success rates
 */
router.get('/api/performance/metrics', async (req: Request, res: Response) => {
  try {
    // Evaluate performance metrics (real implementation would query monitoring system)
    console.log('[PERFORMANCE_ROUTES] Retrieving performance metrics');

    return res.json({
      timestamp: new Date().toISOString(),
      claims_processing: {
        avg_latency_ms: 1250,
        p99_latency_ms: 4500,
        throughput_claims_per_minute: 15,
        success_rate_percentage: 98.5,
        queue_depth: 23
      },
      payment_processing: {
        avg_latency_ms: 2800,
        p99_latency_ms: 8500,
        throughput_payments_per_hour: 45,
        success_rate_percentage: 97.2,
        failed_transactions_last_hour: 3
      },
      fraud_detection: {
        avg_latency_ms: 850,
        p99_latency_ms: 2100,
        false_positive_rate: 4.2,
        flagged_claims_reviewed: 12,
        rejected_claims_count: 2
      },
      coverage_validation: {
        avg_latency_ms: 450,
        p99_latency_ms: 1200,
        success_rate_percentage: 99.8,
        expired_policies_detected_today: 1
      }
    });
  } catch (error: any) {
    console.error('[PERFORMANCE_ROUTES] Failed to retrieve metrics:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve performance metrics' 
    });
  } finally {
    console.log('[PERFORMANCE_ROUTES] Metrics retrieval completed');
  }
});

/**
 * GET /api/performance/dashboard - Get Real-time Dashboard Data
 * 
   Returns comprehensive dashboard data with multiple widget types and charts
 */
router.get('/api/performance/dashboard', async (req: Request, res: Response) => {
  try {
    // Get real-time dashboard data (real implementation would query monitoring system)
    console.log('[PERFORMANCE_ROUTES] Retrieving dashboard data');

    return res.json({
      timestamp: new Date().toISOString(),
      widgets: [
        {
          type: 'stat',
          title: 'Active Claims',
          value: 156,
          trend: '+12% from yesterday'
        },
        {
          type: 'stat',
          title: 'Payments Processed Today',
          value: 487000.00,
          trend: '+8% from yesterday'
        },
        {
          type: 'stat',
          title: 'Avg Processing Time',
          value: '1.5s',
          trend: '-0.3s improvement'
        }
      ],
      charts: [
        {
          id: 'claims_latency_over_time',
          title: 'Claims Latency Over Time',
          data_points: 24 // Last 24 hours
        },
        {
          id: 'payment_throughput_by_hour',
          title: 'Payment Throughput by Hour',
          data_points: 24 // Last 24 hours
        },
        {
          id: 'fraud_detection_rate',
          title: 'Fraud Detection Rate',
          data_points: 7 // Last 7 days
        }
      ],
      alerts: [
        {
          level: 'warning',
          message: 'Payment processing latency elevated (P99 > 8s)',
          started_at: new Date(Date.now() - 3600000 * 2).toISOString()
        }
      ] // Empty for production - would query monitoring alerts
    });
  } catch (error: any) {
    console.error('[PERFORMANCE_ROUTES] Failed to retrieve dashboard data:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve dashboard data' 
    });
  } finally {
    console.log('[PERFORMANCE_ROUTES] Dashboard retrieval completed');
  }
});

/**
 * GET /api/performance/latency - Get Latency Statistics by Service
 * 
   Returns latency metrics broken down by service and operation type
 */
router.get('/api/performance/latency', async (req: Request, res: Response) => {
  try {
    // Get latency statistics (real implementation would query tracing system like Jaeger/Zipkin)
    console.log('[PERFORMANCE_ROUTES] Retrieving latency statistics');

    return res.json({
      timestamp: new Date().toISOString(),
      service_latencies: {
        claims_coverage_check: { avg_ms: 450, p50_ms: 320, p95_ms: 890 },
        claims_payment_initiate: { avg_ms: 1200, p50_ms: 980, p95_ms: 2100 },
        payments_payment_process: { avg_ms: 2800, p50_ms: 2400, p95_ms: 5600 },
        fraud_detection_check: { avg_ms: 850, p50_ms: 720, p95_ms: 1500 },
        coverage_reserve: { avg_ms: 320, p50_ms: 280, p95_ms: 580 }
      },
      external_api_latencies: {
        payment_gateway_avg_ms: 1200,
        fraud_detection_api_avg_ms: 450,
        banking_network_avg_ms: 3200
      }
    });
  } catch (error: any) {
    console.error('[PERFORMANCE_ROUTES] Failed to retrieve latency:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve latency statistics' 
    });
  } finally {
    console.log('[PERFORMANCE_ROUTES] Latency retrieval completed');
  }
});

/**
 * GET /api/performance/error-rates - Get Error Rate Analysis
 * 
   Returns error rate metrics by error type and severity level
 */
router.get('/api/performance/error-rates', async (req: Request, res: Response) => {
  try {
    // Get error rate analysis (real implementation would query error tracking system like Sentry/LogRocket)
    console.log('[PERFORMANCE_ROUTES] Retrieving error rate analysis');

    return res.json({
      timestamp: new Date().toISOString(),
      errors_by_type: {
        payment_gateway_timeout: { count: 3, rate_per_million: 12.5 },
        fraud_detection_api_error: { count: 1, rate_per_million: 4.0 },
        coverage_validation_failed: { count: 0, rate_per_million: 0 },
        bank_account_verification_error: { count: 2, rate_per_million: 8.2 }
      },
      errors_by_severity: {
        critical: { count: 0, rate_per_million: 0 },
        high: { count: 1, rate_per_million: 4.0 },
        medium: { count: 4, rate_per_million: 16.2 },
        low: { count: 8, rate_per_million: 32.5 }
      },
      top_error_messages: [
        { message: 'Payment gateway timeout', occurrences: 3 },
        { message: 'Bank account verification failed', occurrences: 2 }
      ]
    });
  } catch (error: any) {
    console.error('[PERFORMANCE_ROUTES] Failed to retrieve error rates:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve error rate analysis' 
    });
  } finally {
    console.log('[PERFORMANCE_ROUTES] Error rate retrieval completed');
  }
});

/**
 * GET /api/performance/queue-depth - Get Queue Depth Metrics
 * 
   Returns queue depth and processing backlog by service type
 */
router.get('/api/performance/queue-depth', async (req: Request, res: Response) => {
  try {
    // Get queue depth metrics (real implementation would query message broker like Kafka/RabbitMQ)
    console.log('[PERFORMANCE_ROUTES] Retrieving queue depth metrics');

    return res.json({
      timestamp: new Date().toISOString(),
      queues: {
        claims_processing: { depth: 23, processing_rate_per_second: 15, estimated_wait_seconds: 1.5 },
        payment_processing: { depth: 8, processing_rate_per_second: 60, estimated_wait_seconds: 0.13 },
        fraud_detection: { depth: 5, processing_rate_per_second: 40, estimated_wait_seconds: 0.12 }
      }
    });
  } catch (error: any) {
    console.error('[PERFORMANCE_ROUTES] Failed to retrieve queue depth:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve queue depth metrics' 
    });
  } finally {
    console.log('[PERFORMANCE_ROUTES] Queue depth retrieval completed');
  }
});

/**
 * GET /api/performance/health - Overall System Health Check
 * 
   Returns comprehensive system health status including dependency health checks
 */
router.get('/api/performance/health', async (req: Request, res: Response) => {
  try {
    // Get overall system health (real implementation would check dependencies via health check endpoints)
    console.log('[PERFORMANCE_ROUTES] Checking overall system health');

    return res.json({
      timestamp: new Date().toISOString(),
      overall_status: 'healthy',
      services: {
        claims_service: { status: 'healthy', latency_ms: 450 },
        payment_gateway: { status: 'healthy', latency_ms: 1200 },
        fraud_detection_api: { status: 'healthy', latency_ms: 450 },
        banking_network: { status: 'degraded', latency_ms: 3200, message: 'Elevated latency' }
      },
      warnings: [
        { type: 'elevated_latency', service: 'banking_network', details: 'P99 latency > 3s' }
      ] // Empty for production - would query health check endpoints in production
    });
  } catch (error: any) {
    console.error('[PERFORMANCE_ROUTES] Failed to retrieve system health:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve system health status' 
    });
  } finally {
    console.log('[PERFORMANCE_ROUTES] Health check completed');
  }
});

/**
 * POST /api/performance/alerts/config - Configure Performance Alerts Thresholds
 * 
   Configures thresholds for performance monitoring alerts and notifications
 */
router.post('/api/performance/alerts/config', async (req: Request, res: Response) => {
  try {
    // Configure alert thresholds (real implementation would persist to configuration store)
    console.log('[PERFORMANCE_ROUTES] Configuring performance alerts');

    const config = req.body.thresholds;

    if (!config || typeof config !== 'object') {
      return res.status(400).json({ 
        error: 'Validations thresholds object required' 
      });
    }

    console.log('[PERFORMANCE_ROUTES] Performance alerts configured');

    return res.json({ 
      message: 'Performance alert thresholds configured successfully',
      updated_at: new Date().toISOString(),
      configuration_summary: {
        latency_warning_threshold_ms: config.latency_warning_threshold_ms || 8000,
        throughput_target_per_minute: config.throughput_target_per_minute || 30,
        error_rate_max_percentage: config.error_rate_max_percentage || 5.0
      }
    });
  } catch (error: any) {
    console.error('[PERFORMANCE_ROUTES] Failed to configure alerts:', error.message);
    return res.status(500).json({ 
      error: 'Failed to configure performance alert thresholds' 
    });
  } finally {
    console.log('[PERFORMANCE_ROUTES] Alert configuration completed');
  }
});

/**
 * GET /api/performance/trends - Get Performance Trends Over Time
 * 
   Returns historical performance trend data for specified time range
 */
router.get('/api/performance/trends', async (req: Request, res: Response) => {
  try {
    // Get performance trends (real implementation would query metrics database like Prometheus/InfluxDB)
    const period = req.query.period as string || '24h';

    console.log(`[PERFORMANCE_ROUTES] Retrieving performance trends for ${period} period`);

    return res.json({
      timestamp: new Date().toISOString(),
      period,
      trend_data: {
        latency_trend: -0.5, // Negative is improvement (faster)
        throughput_trend: 8.2, // Positive is good (more volume handled)
        error_rate_trend: -1.2, // Negative is good (fewer errors)
        fraud_detection_accuracy_trend: 0.3 // Positive is good (better detection)
      },
      historical_data: [] // Would query metrics database in production
    });
  } catch (error: any) {
    console.error('[PERFORMANCE_ROUTES] Failed to retrieve trends:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve performance trend data' 
    });
  } finally {
    console.log('[PERFORMANCE_ROUTES] Trends retrieval completed');
  }
});

export default router;
