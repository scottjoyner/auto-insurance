/**
 * Claims Service - Payment Request Schema (Phase P1.5)
 * 
   Defines request/response validation schemas for payment endpoints
 */

import { ValidationError, ValidationSchema } from './types';

/**
 * Payment Initiation Request Schema
 * Used for POST /api/payment/initiate endpoint
 */
export const paymentInitiationRequest: ValidationSchema = {
  type: 'object',
  required: ['payment'],
  properties: {
    payment: {
      $ref: '#/$defs/payment_data'
    }
  },
  additionalProperties: true // Allow optional fields for flexibility
};

/**
 * Payment Processing Request Schema
 * Used for POST /api/payment/process endpoint
 */
export const paymentProcessingRequest: ValidationSchema = {
  type: 'object',
  required: ['processing'],
  properties: {
    processing: {
      $ref: '#/$defs/processing_data'
    }
  },
  additionalProperties: true // Allow optional fields for flexibility
};

/**
 * Payment Cancellation Request Schema
 * Used for POST /api/payment/cancel endpoint
 */
export const paymentCancellationRequest: ValidationSchema = {
  type: 'object',
  required: ['cancellation'],
  properties: {
    cancellation: {
      $ref: '#/$defs/cancellation_data'
    }
  },
  additionalProperties: true // Allow optional fields for flexibility
};

/**
 * Reimbursement Setup Request Schema
 * Used for POST /api/reimbursement/setup endpoint
 */
export const reimbursementSetupRequest: ValidationSchema = {
  type: 'object',
  required: ['setup'],
  properties: {
    setup: {
      $ref: '#/$defs/setup_data'
    }
  },
  additionalProperties: true // Allow optional fields for flexibility
};

/**
 * Check Generation Request Schema
 * Used for POST /api/check/generate endpoint
 */
export const checkGenerationRequest: ValidationSchema = {
  type: 'object',
  required: ['check'],
  properties: {
    check: {
      $ref: '#/$defs/check_data'
    }
  },
  additionalProperties: true // Allow optional fields for flexibility
};

/**
 * Payment Data Definition
 */
export interface paymentData {
  type: 'object';
  required: ['claim_id', 'claim_amount'];
  properties: {
    claim_id: string; // Required: Claim identifier
    claim_amount: number; // Required: Dollar amount for claim
    payment_method: string; // Optional: ACH, credit card, check
    customer_name: string; // Optional: Customer name for confirmation
    notification_email: string; // Optional: Email for receipt delivery
  };
}

/**
 * Processing Data Definition
 */
export interface processingData {
  type: 'object';
  required: ['claim_id', 'claim_amount'];
  properties: {
    claim_id: string; // Required: Claim identifier
    claim_amount: number; // Required: Dollar amount for claim
    payment_id: string; // Optional: Associated payment ID
    gateway_transaction_id: string; // Optional: Gateway transaction reference
  };
}

/**
 * Cancellation Data Definition
 */
export interface cancellationData {
  type: 'object';
  required: ['reason'];
  properties: {
    reason: string; // Required: Reason for cancellation
    refund_request: boolean; // Optional: Request immediate refund
    notification_email: string; // Optional: Email for cancellation notice
  };
}

/**
 * Setup Data Definition
 */
export interface setupData {
  type: 'object';
  required: ['payment_method'];
  properties: {
    payment_method: string; // Required: ACH, wire transfer, etc.
    bank_account_number: string; // Optional: Bank account number (last 4 only in production)
    routing_number: string; // Optional: Routing number
    customer_name: string; // Optional: Customer name for verification
  };
}

/**
 * Check Data Definition
 */
export interface checkData {
  type: 'object';
  required: ['claim_id'];
  properties: {
    claim_id: string; // Required: Claim identifier for payment
    claim_amount: number; // Optional: Dollar amount (use existing if not specified)
    customer_address: string; // Optional: Mailing address for check delivery
    expedited_delivery: boolean; // Optional: Request overnight shipping
  };
}

/**
 * Payment Initiation Response Schema
 */
export const paymentInitiationResponse: ValidationSchema = {
  type: 'object',
  properties: {
    payment_id: { type: 'string' },
    status: { 
      type: 'string', 
      enum: ['initiated', 'processing', 'completed', 'failed'] 
    },
    amount: { type: 'number' },
    payment_method: { type: 'string' },
    initiated_at: { type: 'string', format: 'date-time' },
    expected_completion: { type: 'string', format: 'date-time' },
    fraud_check_status: { 
      type: 'string', 
      enum: ['pending', 'approved', 'review', 'rejected'] 
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Payment Processing Response Schema
 */
export const paymentProcessingResponse: ValidationSchema = {
  type: 'object',
  properties: {
    transaction_id: { type: 'string' },
    status: { 
      type: 'string', 
      enum: ['initiated', 'processing', 'completed', 'failed'] 
    },
    amount_processed: { type: 'number' },
    gateway_response_code: { type: 'string' },
    processed_at: { type: 'string', format: 'date-time' },
    receipt_url: { type: 'string' },
    confirmation_sent_to: { 
      type: 'string', 
      enum: ['email', 'sms', 'mail', 'none'] 
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Payment Status Response Schema
 */
export const paymentStatusResponse: ValidationSchema = {
  type: 'object',
  properties: {
    payment_id: { type: 'string' },
    status: { 
      type: 'string', 
      enum: ['initiated', 'processing', 'completed', 'failed', 'cancelled'] 
    },
    amount: { type: 'number' },
    claim_amount: { type: 'number' },
    deduction_type: { type: 'string' },
    deduction_amount: { type: 'number' },
    fraud_check_status: { 
      type: 'string', 
      enum: ['pending', 'cleared', 'suspicious', 'rejected'] 
    },
    gateway_status: { 
      type: 'string', 
      enum: ['pending', 'processing', 'processed', 'failed'] 
    },
    initiated_at: { type: 'string', format: 'date-time' },
    completed_at: { type: 'string', format: 'date-time' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Reimbursement Setup Response Schema
 */
export const reimbursementSetupResponse: ValidationSchema = {
  type: 'object',
  properties: {
    reimbursement_id: { type: 'string' },
    status: { 
      type: 'string', 
      enum: ['active', 'pending', 'inactive', 'cancelled'] 
    },
    payment_method: { type: 'string' },
    bank_account_last_four: { type: 'string' },
    routing_number_last_four: { type: 'string' },
    established_at: { type: 'string', format: 'date-time' },
    can_process_direct_deposit: { type: 'boolean' },
    processing_fee_percentage: { type: 'number' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Check Generation Response Schema
 */
export const checkGenerationResponse: ValidationSchema = {
  type: 'object',
  properties: {
    check_number: { type: 'string' },
    status: { 
      type: 'string', 
      enum: ['generated', 'processing', 'mailed', 'delivered'] 
    },
    amount: { type: 'number' },
    generated_at: { type: 'string', format: 'date-time' },
    mail_status: { 
      type: 'string', 
      enum: ['pending', 'in_transit', 'delivered', 'returned', 'lost'] 
    },
    processing_fee: { type: 'number' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Receipt Response Schema
 */
export const receiptResponse: ValidationSchema = {
  type: 'object',
  properties: {
    receipt_id: { type: 'string' },
    payment_id: { type: 'string' },
    status: { 
      type: 'string', 
      enum: ['initiated', 'processing', 'completed', 'failed'] 
    },
    amount_paid: { type: 'number' },
    claim_amount: { type: 'number' },
    deductible_deduction: { type: 'number' },
    processing_date: { type: 'string', format: 'date-time' },
    customer_name: { type: 'string' },
    payment_method_used: { type: 'string' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Delivery Tracking Response Schema
 */
export const deliveryTrackingResponse: ValidationSchema = {
  type: 'object',
  properties: {
    payment_id: { type: 'string' },
    delivery_status: { 
      type: 'string', 
      enum: ['pending', 'shipped', 'in_transit', 'delivered', 'returned', 'lost'] 
    },
    tracking_number: { type: 'string' },
    estimated_delivery_date: { type: 'string', format: 'date-time' },
    carrier: { type: 'string' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Payment History Item Schema
 */
export interface paymentHistoryItem {
  payment_id: string;
  claim_id: string;
  amount: number;
  status: string;
  date: string;
}

/**
 * Payment History Response Schema
 */
export const paymentHistoryResponse: ValidationSchema = {
  type: 'object',
  properties: {
    customer_id: { type: 'string' },
    total_payments_count: { type: 'number' },
    total_amount_paid: { type: 'number' },
    recent_transactions: {
      type: 'array',
      items: {} // Would use paymentHistoryItem in production
    }
  },
  required: [] // All fields optional for backwards compatibility
};
