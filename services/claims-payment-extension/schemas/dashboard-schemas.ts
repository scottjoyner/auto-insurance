/**
 * Claims Service - Dashboard Schemas (Phase P2.0)
 * 
   Provides type definitions and validation schemas for realtime dashboard endpoints
 */

import { ValidationError, ValidationSchema } from './types';

/**
 * Live Metrics Request Schema
 * Used for GET /api/monitoring/metrics endpoint
 */
export const liveMetricsRequest: ValidationSchema = {
  type: 'object',
  properties: {
    // Optional filtering parameters
    metric_type: { 
      type: 'string',
      enum: ['claims_submitted', 'payments_processed', 'coverage_checks']
    },
    since_timestamp: { type: 'string', format: 'date-time' }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Widget Data Request Schema
 * Used for GET /api/monitoring/widget/:widgetType endpoint
 */
export const widgetDataRequest: ValidationSchema = {
  type: 'object',
  properties: {
    widget_type: { 
      type: 'string',
      enum: ['claims_count', 'payments_today', 'processing_time', 'error_rate']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Chart Data Request Schema
 * Used for GET /api/monitoring/chart/:chartId endpoint
 */
export const chartDataRequest: ValidationSchema = {
  type: 'object',
  properties: {
    chart_id: { 
      type: 'string',
      enum: ['claims_latency_over_time', 'payment_throughput_by_hour', 'fraud_detection_rate']
    },
    time_range: { 
      type: 'string',
      enum: ['1h', '24h', '7d', '30d']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * System Status Request Schema
 * Used for GET /api/monitoring/status endpoint
 */
export const systemStatusRequest: ValidationSchema = {
  type: 'object',
  properties: {
    service: { 
      type: 'string',
      enum: ['claims_service', 'payment_gateway', 'fraud_detection_api']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Active Alerts Request Schema
 * Used for GET /api/monitoring/alerts endpoint
 */
export const activeAlertsRequest: ValidationSchema = {
  type: 'object',
  properties: {
    severity_level: { 
      type: 'string',
      enum: ['info', 'warning', 'error', 'critical']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Processing Queue Request Schema
 * Used for GET /api/monitoring/queue endpoint
 */
export const processingQueueRequest: ValidationSchema = {
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
 * Geographic Distribution Request Schema
 * Used for GET /api/monitoring/geographic endpoint
 */
export const geographicDistributionRequest: ValidationSchema = {
  type: 'object',
  properties: {
    region: { 
      type: 'string',
      enum: ['North America', 'Europe', 'Asia Pacific']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Processing Funnel Request Schema
 * Used for GET /api/monitoring/funnel endpoint
 */
export const processingFunnelRequest: ValidationSchema = {
  type: 'object',
  properties: {}, // No required or optional fields - returns full funnel data
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Risk Distribution Request Schema
 * Used for GET /api/monitoring/risk endpoint
 */
export const riskDistributionRequest: ValidationSchema = {
  type: 'object',
  properties: {}, // No required or optional fields - returns full distribution data
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Top Performers Request Schema
 * Used for GET /api/monitoring/performance/:performerType endpoint
 */
export const topPerformersRequest: ValidationSchema = {
  type: 'object',
  properties: {
    performer_type: { 
      type: 'string',
      enum: ['agents', 'providers']
    },
    limit: { 
      type: 'integer',
      minimum: 1,
      maximum: 50,
      default: 10
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Recent Events Request Schema
 * Used for GET /api/monitoring/events endpoint
 */
export const recentEventsRequest: ValidationSchema = {
  type: 'object',
  properties: {
    event_type: { 
      type: 'string',
      enum: ['payment_completed', 'coverage_validated', 'fraud_alert']
    },
    since_timestamp: { type: 'string', format: 'date-time' }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Widget Configuration Request Schema
 * Used for GET /api/monitoring/widget/:widgetId/config endpoint
 */
export const widgetConfigRequest: ValidationSchema = {
  type: 'object',
  properties: {
    widget_id: { 
      type: 'string',
      enum: ['claims_count', 'payments_today', 'processing_time', 'error_rate']
    }
  },
  additionalProperties: false // No optional fields to keep it strict
};

/**
 * Dashboard Widget Response Schema
 */
export const dashboardWidgetResponse: ValidationSchema = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    title: { type: 'string' },
    value: {}, // Any widget-specific data (number, string, object)
    trend: { type: 'string' },
    icon: { type: 'string' },
    visible: { type: 'boolean' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Chart Data Response Schema
 */
export const chartDataResponse: ValidationSchema = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    time_range: { type: 'string' },
    title: { type: 'string' },
    data_points: {
      type: 'array',
      items: {
        oneOf: [
          { type: 'number' }, // Single value for line charts
          { 
            type: 'object',
            properties: {
              date: { type: 'string', format: 'date-time' },
              value: { type: 'number' }
            }
          } // Time series data object
        ]
      }
    },
    y_axis_label: { type: 'string' },
    chart_type: { 
      type: 'string',
      enum: ['line', 'bar', 'area', 'stacked']
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * System Status Response Schema
 */
export const systemStatusResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    overall_status: { 
      type: 'string',
      enum: ['operational', 'degraded', 'outage']
    },
    uptime_seconds: { type: 'integer' },
    version: { type: 'string' },
    environment: { 
      type: 'string',
      enum: ['development', 'staging', 'production']
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Active Alerts Response Schema
 */
export const activeAlertsResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    alert_count: { type: 'integer' },
    alerts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          severity: { 
            type: 'string',
            enum: ['info', 'warning', 'error', 'critical']
          },
          title: { type: 'string' },
          message: { type: 'string' },
          started_at: { type: 'string', format: 'date-time' },
          acknowledged: { type: 'boolean' },
          link: { type: 'string' }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Processing Queue Response Schema
 */
export const processingQueueResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    queues: {
      type: 'object',
      properties: {
        claims_processing: {
          type: 'object',
          properties: {
            waiting: { type: 'integer' },
            processing: { type: 'integer' },
            throughput_per_second: { type: 'number' },
            lag_seconds: { type: 'number' }
          }
        },
        payment_processing: {
          type: 'object',
          properties: {
            waiting: { type: 'integer' },
            processing: { type: 'integer' },
            throughput_per_second: { type: 'number' },
            lag_seconds: { type: 'number' }
          }
        },
        fraud_detection: {
          type: 'object',
          properties: {
            waiting: { type: 'integer' },
            processing: { type: 'integer' },
            throughput_per_second: { type: 'number' },
            lag_seconds: { type: 'number' }
          }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Geographic Distribution Response Schema
 */
export const geographicDistributionResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    regions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          region: { type: 'string' },
          claims_count: { type: 'integer' },
          percentage: { type: 'number' }
        }
      }
    },
    map_data: {
      type: 'array',
      items: {} // Would use GeoJSON in production
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Processing Funnel Response Schema
 */
export const processingFunnelResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    funnel_stages: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          stage: { type: 'string' },
          count: { type: 'integer' },
          dropoff_rate: { type: 'number' }
        }
      }
    },
    total_dropoff_percentage: { type: 'number' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Risk Distribution Response Schema
 */
export const riskDistributionResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    risk_categories: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          category: { 
            type: 'string',
            enum: ['low_risk', 'medium_risk', 'high_risk', 'critical_risk']
          },
          count: { type: 'integer' },
          percentage: { type: 'number' }
        }
      }
    },
    total_claims_checked_today: { type: 'integer' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Top Performers Response Schema
 */
export const topPerformersResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    leaders: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          rank: { type: 'integer' },
          name: { type: 'string' },
          claims_processed: { type: 'integer' },
          accuracy: { type: 'number' }
        }
      }
    },
    top_category: { type: 'string' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Recent Events Response Schema
 */
export const recentEventsResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    events: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          type: { 
            type: 'string',
            enum: ['payment_completed', 'coverage_validated', 'fraud_alert']
          },
          message: { type: 'string' },
          time_ago: { type: 'string' }
        }
      }
    },
    last_updated: { type: 'string', format: 'date-time' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Widget Configuration Response Schema
 */
export const widgetConfigResponse: ValidationSchema = {
  type: 'object',
  properties: {
    widget_id: { type: 'string' },
    visible: { type: 'boolean' },
    position: { 
      type: 'string',
      enum: ['top-left', 'top-right', 'bottom-left', 'bottom-right']
    },
    size: { 
      type: 'string',
      enum: ['small', 'medium', 'large']
    },
    refresh_interval_seconds: { type: 'integer' },
    auto_update: { type: 'boolean' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Live Metrics Response Schema
 */
export const liveMetricsResponse: ValidationSchema = {
  type: 'object',
  properties: {
    timestamp: { type: 'string', format: 'date-time' },
    live_metrics: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          metric: { 
            type: 'string',
            enum: ['claims_submitted', 'payments_processed', 'coverage_checks']
          },
          value: { oneOf: [{ type: 'integer' }, { type: 'number' }] },
          timestamp: { type: 'string', format: 'date-time' }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};
