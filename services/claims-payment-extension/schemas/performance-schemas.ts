/**
 * Claims Service - Performance Evaluation Schemas (Phase P2.0)
 * 
   Provides type definitions and validation schemas for performance tracking endpoints
 */

import { ValidationError, ValidationSchema } from './types';

/**
 * Performance Metrics Request Schema
 * Used for GET /api/performance/metrics endpoint
 */
export const performanceMetricsRequest: ValidationSchema = {
  type: 'object',
  properties: {
    // Optional filtering parameters
    service: { 
      type: 'string', 
      enum: ['claims_processing', 'payment_processing', 'fraud_detection', 'coverage_validation'] 
    },
    time_range: { 
      type: 'string',
      enum: ['1h', '24h', '7d', '30d'] 
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Dashboard Data Request Schema
 * Used for GET /api/performance/dashboard endpoint
 */
export const dashboardDataRequest: ValidationSchema = {
  type: 'object',
  properties: {
    widgets: { 
      type: 'array',
      items: {
        type: 'string',
        enum: ['active_claims', 'payments_today', 'processing_time']
      }
    },
    charts: { 
      type: 'array',
      items: {
        type: 'string',
        enum: ['claims_latency_over_time', 'payment_throughput_by_hour', 'fraud_detection_rate']
      }
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Latency Statistics Request Schema
 * Used for GET /api/performance/latency endpoint
 */
export const latencyStatisticsRequest: ValidationSchema = {
  type: 'object',
  properties: {
    service: { 
      type: 'string',
      enum: [
        'claims_coverage_check',
        'claims_payment_initiate',
        'payments_payment_process',
        'fraud_detection_check',
        'coverage_reserve'
      ]
    },
    percentile: { 
      type: 'number',
      minimum: 0,
      maximum: 100
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Error Rate Analysis Request Schema
 * Used for GET /api/performance/error-rates endpoint
 */
export const errorRateAnalysisRequest: ValidationSchema = {
  type: 'object',
  properties: {
    error_type: { 
      type: 'string',
      enum: ['payment_gateway_timeout', 'fraud_detection_api_error', 'coverage_validation_failed']
    },
    severity_level: { 
      type: 'string',
      enum: ['critical', 'high', 'medium', 'low']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Queue Depth Request Schema
 * Used for GET /api/performance/queue-depth endpoint
 */
export const queueDepthRequest: ValidationSchema = {
  type: 'object',
  properties: {
    queue_name: { 
      type: 'string',
      enum: ['claims_processing', 'payment_processing', 'fraud_detection']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * System Health Request Schema
 * Used for GET /api/performance/health endpoint
 */
export const systemHealthRequest: ValidationSchema = {
  type: 'object',
  properties: {
    service: { 
      type: 'string',
      enum: ['claims_service', 'payment_gateway', 'fraud_detection_api', 'banking_network']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Performance Alerts Configuration Request Schema
 * Used for POST /api/performance/alerts/config endpoint
 */
export const performanceAlertsConfigRequest: ValidationSchema = {
  type: 'object',
  required: ['thresholds'],
  properties: {
    thresholds: {
      $ref: '#/$defs/thresholds_config'
    }
  },
  additionalProperties: true // Allow optional fields for flexibility
};

/**
 * Thresholds Configuration Definition
 */
export interface thresholdsConfig {
  type: 'object';
  required: ['latency_warning_threshold_ms', 'throughput_target_per_minute'];
  properties: {
    latency_warning_threshold_ms: number; // Latency threshold in milliseconds for warnings
    throughput_target_per_minute: number; // Target throughput per minute
    error_rate_max_percentage: number; // Maximum acceptable error rate percentage
  };
}

/**
 * Performance Trends Request Schema
 * Used for GET /api/performance/trends endpoint
 */
export const performanceTrendsRequest: ValidationSchema = {
  type: 'object',
  properties: {
    period: { 
      type: 'string',
      enum: ['1h', '6h', '24h', '7d', '30d']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Performance Metrics Response Schema
 */
export const performanceMetricsResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    claims_processing: {
      type: 'object',
      properties: {
        avg_latency_ms: { type: 'number' },
        p99_latency_ms: { type: 'number' },
        throughput_claims_per_minute: { type: 'number' },
        success_rate_percentage: { type: 'number' },
        queue_depth: { type: 'integer' }
      }
    },
    payment_processing: {
      type: 'object',
      properties: {
        avg_latency_ms: { type: 'number' },
        p99_latency_ms: { type: 'number' },
        throughput_payments_per_hour: { type: 'number' },
        success_rate_percentage: { type: 'number' },
        failed_transactions_last_hour: { type: 'integer' }
      }
    },
    fraud_detection: {
      type: 'object',
      properties: {
        avg_latency_ms: { type: 'number' },
        p99_latency_ms: { type: 'number' },
        false_positive_rate: { type: 'number' },
        flagged_claims_reviewed: { type: 'integer' },
        rejected_claims_count: { type: 'integer' }
      }
    },
    coverage_validation: {
      type: 'object',
      properties: {
        avg_latency_ms: { type: 'number' },
        p99_latency_ms: { type: 'number' },
        success_rate_percentage: { type: 'number' },
        expired_policies_detected_today: { type: 'integer' }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Dashboard Data Response Schema
 */
export const dashboardDataResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    widgets: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          type: { 
            type: 'string',
            enum: ['stat', 'chart', 'alert']
          },
          title: { type: 'string' },
          value: {}, // Any widget-specific data
          trend: { type: 'string' }
        }
      }
    },
    charts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          title: { type: 'string' },
          data_points: {
            type: 'array',
            items: { type: 'number' }
          }
        }
      }
    },
    alerts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          level: { 
            type: 'string',
            enum: ['info', 'warning', 'error']
          },
          message: { type: 'string' },
          started_at: { type: 'string', format: 'date-time' }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Latency Statistics Response Schema
 */
export const latencyStatisticsResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    service_latencies: {
      type: 'object',
      properties: {
        claims_coverage_check: {
          type: 'object',
          properties: {
            avg_ms: { type: 'number' },
            p50_ms: { type: 'number' },
            p95_ms: { type: 'number' }
          }
        },
        claims_payment_initiate: {
          type: 'object',
          properties: {
            avg_ms: { type: 'number' },
            p50_ms: { type: 'number' },
            p95_ms: { type: 'number' }
          }
        },
        payments_payment_process: {
          type: 'object',
          properties: {
            avg_ms: { type: 'number' },
            p50_ms: { type: 'number' },
            p95_ms: { type: 'number' }
          }
        },
        fraud_detection_check: {
          type: 'object',
          properties: {
            avg_ms: { type: 'number' },
            p50_ms: { type: 'number' },
            p95_ms: { type: 'number' }
          }
        },
        coverage_reserve: {
          type: 'object',
          properties: {
            avg_ms: { type: 'number' },
            p50_ms: { type: 'number' },
            p95_ms: { type: 'number' }
          }
        }
      }
    },
    external_api_latencies: {
      type: 'object',
      properties: {
        payment_gateway_avg_ms: { type: 'number' },
        fraud_detection_api_avg_ms: { type: 'number' },
        banking_network_avg_ms: { type: 'number' }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Error Rate Analysis Response Schema
 */
export const errorRateAnalysisResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    errors_by_type: {
      type: 'object',
      properties: {
        payment_gateway_timeout: {
          type: 'object',
          properties: {
            count: { type: 'integer' },
            rate_per_million: { type: 'number' }
          }
        },
        fraud_detection_api_error: {
          type: 'object',
          properties: {
            count: { type: 'integer' },
            rate_per_million: { type: 'number' }
          }
        },
        coverage_validation_failed: {
          type: 'object',
          properties: {
            count: { type: 'integer' },
            rate_per_million: { type: 'number' }
          }
        }
      }
    },
    errors_by_severity: {
      type: 'object',
      properties: {
        critical: {
          type: 'object',
          properties: {
            count: { type: 'integer' },
            rate_per_million: { type: 'number' }
          }
        },
        high: {
          type: 'object',
          properties: {
            count: { type: 'integer' },
            rate_per_million: { type: 'number' }
          }
        },
        medium: {
          type: 'object',
          properties: {
            count: { type: 'integer' },
            rate_per_million: { type: 'number' }
          }
        },
        low: {
          type: 'object',
          properties: {
            count: { type: 'integer' },
            rate_per_million: { type: 'number' }
          }
        }
      }
    },
    top_error_messages: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          message: { type: 'string' },
          occurrences: { type: 'integer' }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Queue Depth Response Schema
 */
export const queueDepthResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    queues: {
      type: 'object',
      properties: {
        claims_processing: {
          type: 'object',
          properties: {
            depth: { type: 'integer' },
            processing_rate_per_second: { type: 'number' },
            estimated_wait_seconds: { type: 'number' }
          }
        },
        payment_processing: {
          type: 'object',
          properties: {
            depth: { type: 'integer' },
            processing_rate_per_second: { type: 'number' },
            estimated_wait_seconds: { type: 'number' }
          }
        },
        fraud_detection: {
          type: 'object',
          properties: {
            depth: { type: 'integer' },
            processing_rate_per_second: { type: 'number' },
            estimated_wait_seconds: { type: 'number' }
          }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * System Health Response Schema
 */
export const systemHealthResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    overall_status: { 
      type: 'string', 
      enum: ['healthy', 'degraded', 'critical'] 
    },
    services: {
      type: 'object',
      properties: {
        claims_service: {
          type: 'object',
          properties: {
            status: { 
              type: 'string',
              enum: ['healthy', 'degraded', 'unreachable']
            },
            latency_ms: { type: 'number' }
          }
        },
        payment_gateway: {
          type: 'object',
          properties: {
            status: { 
              type: 'string',
              enum: ['healthy', 'degraded', 'unreachable']
            },
            latency_ms: { type: 'number' }
          }
        },
        fraud_detection_api: {
          type: 'object',
          properties: {
            status: { 
              type: 'string',
              enum: ['healthy', 'degraded', 'unreachable']
            },
            latency_ms: { type: 'number' }
          }
        },
        banking_network: {
          type: 'object',
          properties: {
            status: { 
              type: 'string',
              enum: ['healthy', 'degraded', 'unreachable']
            },
            latency_ms: { type: 'number' },
            message: { type: 'string' }
          }
        }
      }
    },
    warnings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          type: { type: 'string' },
          service: { type: 'string' },
          details: { type: 'string' }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Configuration Response Schema
 */
export const configurationResponse: ValidationSchema = {
  type: 'object',
  properties: {
    message: { type: 'string' },
    updated_at: { type: 'string', format: 'date-time' },
    configuration_summary: {
      type: 'object',
      properties: {
        latency_warning_threshold_ms: { type: 'number' },
        throughput_target_per_minute: { type: 'number' },
        error_rate_max_percentage: { type: 'number' }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Trends Response Schema
 */
export const trendsResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    period: { type: 'string' },
    trend_data: {
      type: 'object',
      properties: {
        latency_trend: { type: 'number' }, // Negative is improvement (faster)
        throughput_trend: { type: 'number' }, // Positive is good (more volume)
        error_rate_trend: { type: 'number' }, // Negative is good (fewer errors)
        fraud_detection_accuracy_trend: { type: 'number' } // Positive is good (better detection)
      }
    },
    historical_data: {
      type: 'array',
      items: {} // Would use specific schema in production
    }
  },
  required: [] // All fields optional for backwards compatibility
};
