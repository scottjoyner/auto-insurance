/**
 * Claims Service - Payment Orchestration Types (Phase P1.5)
 * 
   Provides type definitions for payment processing and fraud detection
 */

export enum PaymentStatus {
  INITIATED = 'initiated',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum FraudRiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum PaymentMethod {
  ACH = 'ach',
  WIRE = 'wire',
  CHECK = 'check',
  CREDIT_CARD = 'credit_card',
  DEBIT_CARD = 'debit_card'
}

export interface FraudDetectionResult {
  is_suspect: boolean;
  risk_score: number; // 0.0 - 1.0 (lower is safer)
  risk_level: string; // low, medium, high, critical
  reasons: Array<string>;
  recommendation: 'approve' | 'review' | 'reject';
}

export interface PaymentConfig {
  gateway_url: string;
  fraud_detection_api_key: string;
  reimbursement_tracking_enabled: boolean;
}

/**
 * Payment Initiation Configuration
 */
export interface PaymentInitiationConfig {
  amount: number;
  claim_id: string;
  payment_method?: PaymentMethod;
  customer_reference?: string;
  external_metadata?: Record<string, any>;
}

/**
 * Fraud Check Options
 */
export interface FraudCheckOptions {
  enable_identity_verification?: boolean;
  check_previous_claims?: boolean;
  verify_policy_number?: boolean;
  check_address_match?: boolean;
}

/**
 * Payment Processing History Entry
 */
export interface PaymentProcessingHistory {
  timestamp: string;
  stage: string;
  status: 'success' | 'failed';
  error?: string;
  metadata?: Record<string, any>;
}

/**
 * Reimbursement Account Configuration
 */
export interface ReimbursementAccountConfig {
  payment_method: PaymentMethod;
  bank_account_number?: string; // Last 4 digits in production
  routing_number?: string;
  customer_name: string;
  enable_direct_deposit: boolean;
  processing_fee_percentage: number;
}

/**
 * Check Generation Configuration
 */
export interface CheckGenerationConfig {
  claim_id: string;
  amount?: number; // Use existing claim amount if not specified
  mailing_address: string;
  expedited_delivery?: boolean;
}

/**
 * Payment Receipt Metadata
 */
export interface PaymentReceiptMetadata {
  receipt_number: string;
  issued_at: string;
  payment_reference_id: string;
  customer_email?: string;
  delivery_method: 'email' | 'print' | 'portal';
}

/**
 * Delivery Tracking Configuration
 */
export interface DeliveryTrackingConfig {
  carrier: string; // USPS, FedEx, UPS, etc.
  tracking_number: string;
  estimated_delivery_days: number;
  insurance_amount?: number;
}

/**
 * Payment Method Selection Criteria
 */
export interface PaymentMethodCriteria {
  payment_methods: Array<{
    method: PaymentMethod;
    available: boolean;
    preferred: boolean;
    processing_time_hours: number;
    fee_percentage: number;
    minimum_amount: number;
    maximum_amount: number;
  }>;
}

/**
 * Adjudication Decision
 */
export interface AdjudicationDecision {
  approved: boolean;
  amount_approved: number;
  reason?: string;
  decision_criteria: Array<string>;
}
