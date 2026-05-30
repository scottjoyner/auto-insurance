/**
 * Claims Service - Coverage Validation Types (Phase P1.5)
 * 
   Provides type definitions and validation utilities for coverage requests
 */

export interface ValidationResult {
  valid: boolean;
  errors?: ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Coverage Request Schema Definition
 */
export interface CoverageRequestSchema {
  properties: Record<string, any>;
  required: string[];
}

/**
 * Validate coverage request structure and fields
 */
export function validateCoverageRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'request',
      message: 'Coverage request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate claim data structure
  if (request.claim && typeof request.claim === 'object') {
    const claim = request.claim;

    if (!claim.policy_number) {
      errors.push({
        field: 'claim.policy_number',
        message: 'Policy number is required for coverage verification'
      });
    }

    if (!claim.claim_type) {
      errors.push({
        field: 'claim.claim_type',
        message: 'Claim type is required for coverage verification'
      });
    }

    // Validate claim amount format if provided
    if (typeof claim.claim_amount === 'number' && claim.claim_amount < 0) {
      errors.push({
        field: 'claim.claim_amount',
        message: 'Claim amount must be a non-negative number'
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate payment request structure and fields
 */
export function validatePaymentRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'payment.request',
      message: 'Payment request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate payment data structure
  if (request.payment && typeof request.payment === 'object') {
    const payment = request.payment;

    if (!payment.claim_id) {
      errors.push({
        field: 'payment.claim_id',
        message: 'Claim ID is required for payment initiation'
      });
    }

    if (!payment.claim_amount) {
      errors.push({
        field: 'payment.claim_amount',
        message: 'Claim amount is required for payment processing'
      });
    }

    // Validate claim amount format if provided
    if (typeof payment.claim_amount === 'number' && payment.claim_amount < 0) {
      errors.push({
        field: 'payment.claim_amount',
        message: 'Claim amount must be a non-negative number'
      });
    }

    // Validate payment method if provided
    if (payment.payment_method && !['ach', 'wire', 'check'].includes(payment.payment_method)) {
      errors.push({
        field: 'payment.payment_method',
        message: `Payment method must be one of: ach, wire, check. Received: ${payment.payment_method}`
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate cancellation request structure and fields
 */
export function validateCancellationRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'cancellation.request',
      message: 'Cancellation request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate cancellation data structure
  if (request.cancellation && typeof request.cancellation === 'object') {
    const cancellation = request.cancellation;

    if (!cancellation.reason) {
      errors.push({
        field: 'cancellation.reason',
        message: 'Cancellation reason is required'
      });
    }

    // Validate reason format (basic length check)
    if (cancellation.reason && cancellation.reason.length > 500) {
      errors.push({
        field: 'cancellation.reason',
        message: 'Cancellation reason must be 500 characters or less'
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate setup request structure and fields
 */
export function validateSetupRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'setup.request',
      message: 'Setup request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate setup data structure
  if (request.setup && typeof request.setup === 'object') {
    const setup = request.setup;

    if (!setup.payment_method) {
      errors.push({
        field: 'setup.payment_method',
        message: 'Payment method is required for reimbursement setup'
      });
    }

    // Validate payment method format
    if (setup.payment_method && !['ach', 'wire', 'check'].includes(setup.payment_method)) {
      errors.push({
        field: 'setup.payment_method',
        message: `Payment method must be one of: ach, wire, check. Received: ${setup.payment_method}`
      });
    }

    // Validate bank account number length if provided (last 4 digits only in production)
    if (setup.bank_account_number && setup.bank_account_number.length > 4) {
      errors.push({
        field: 'setup.bank_account_number',
        message: 'Bank account number must be the last 4 digits only'
      });
    }

    // Validate routing number length if provided
    if (setup.routing_number && setup.routing_number.length < 9) {
      errors.push({
        field: 'setup.routing_number',
        message: 'Routing number must be at least 9 digits'
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate check request structure and fields
 */
export function validateCheckRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'check.request',
      message: 'Check generation request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate check data structure
  if (request.check && typeof request.check === 'object') {
    const check = request.check;

    if (!check.claim_id) {
      errors.push({
        field: 'check.claim_id',
        message: 'Claim ID is required for check generation'
      });
    }

    // Validate claim amount format if provided
    if (typeof check.claim_amount === 'number' && check.claim_amount < 0) {
      errors.push({
        field: 'check.claim_amount',
        message: 'Claim amount must be a non-negative number'
      });
    }

    // Validate customer address format if provided
    if (check.customer_address && typeof check.customer_address === 'string') {
      if (check.customer_address.length < 10) {
        errors.push({
          field: 'check.customer_address',
          message: 'Customer address must be at least 10 characters'
        });
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate receipt request structure and fields
 */
export function validateReceiptRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'receipt.request',
      message: 'Receipt request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate receipt data structure
  if (request.receipt && typeof request.receipt === 'object') {
    const receipt = request.receipt;

    if (!receipt.payment_id) {
      errors.push({
        field: 'receipt.payment_id',
        message: 'Payment ID is required for receipt generation'
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate tracking request structure and fields
 */
export function validateTrackingRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'tracking.request',
      message: 'Tracking request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate tracking data structure
  if (request.tracking && typeof request.tracking === 'object') {
    const tracking = request.tracking;

    if (!tracking.payment_id) {
      errors.push({
        field: 'tracking.payment_id',
        message: 'Payment ID is required for delivery tracking'
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate history request structure and fields
 */
export function validateHistoryRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'history.request',
      message: 'History request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate history data structure
  if (request.history && typeof request.history === 'object') {
    const history = request.history;

    if (!history.customer_id) {
      errors.push({
        field: 'history.customer_id',
        message: 'Customer ID is required for payment history retrieval'
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate fraud detection request structure and fields
 */
export function validateFraudDetectionRequest(request: any): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!request || typeof request !== 'object') {
    errors.push({
      field: 'fraud_detection.request',
      message: 'Fraud detection request must be a valid object'
    });
    return { valid: false, errors };
  }

  // Validate fraud detection data structure
  if (request.fraud && typeof request.fraud === 'object') {
    const fraud = request.fraud;

    if (!fraud.claim_id) {
      errors.push({
        field: 'fraud.claim_id',
        message: 'Claim ID is required for fraud check'
      });
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}
