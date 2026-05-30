/**
 * Claims Service - Coverage Request Schema (Phase P1.5)
 * 
   Defines request/response validation schemas for coverage endpoints
 */

import { ValidationError, ValidationSchema } from './types';

/**
 * Coverage Verification Request Schema
 * Used for POST /api/coverage/verify endpoint
 */
export const coverageVerificationRequest: ValidationSchema = {
  properties: {
    claim: {
      $ref: '#/$defs/claim_data'
    }
  },
  required: ['claim']
};

/**
 * Coverage Check Request Schema
 * Used for GET /api/coverage/check/:claimId with query params
 */
export const coverageCheckRequest: ValidationSchema = {
  properties: {
    claim_id: { type: 'string' }
  },
  required: ['claim_id']
};

/**
 * Coverage Status Request Schema
 * Used for GET /api/coverage/status/:claimId endpoint
 */
export const coverageStatusRequest: ValidationSchema = {
  properties: {
    claim_id: { type: 'string' }
  },
  required: ['claim_id']
};

/**
 * Coverage Endorsement Request Schema
 * Used for POST /api/coverage/check-endorsement endpoint
 */
export const coverageEndorsementRequest: ValidationSchema = {
  properties: {
    endorsement: {
      $ref: '#/$defs/endorsement_data'
    }
  },
  required: ['endorsement']
};

/**
 * Coverage Reservation Request Schema
 * Used for POST /api/coverage/reserve endpoint
 */
export const coverageReservationRequest: ValidationSchema = {
  properties: {
    reservation: {
      $ref: '#/$defs/reservation_data'
    }
  },
  required: ['reservation']
};

/**
 * Claim Data Definition
 */
export interface claimData {
  type: 'object';
  required: [''];
  properties: {
    policy_number: string; // Required: Policy identifier
    claim_type: string; // Required: Type of claim (collision, comprehensive, etc.)
    claim_amount: number; // Optional: Claim dollar amount
    incident_date: string; // Optional: Date of incident
    description: string; // Optional: Brief description of incident
    location: string; // Optional: Location of incident
  };
}

/**
 * Endorsement Data Definition
 */
export interface endorsementData {
  type: 'object';
  required: ['type'];
  properties: {
    type: string; // Required: Endorsement identifier (e.g., 'additional_coverage')
    effect_date: string; // Optional: Effective date of endorsement
    description: string; // Optional: Endorsement description
    premium_adjustment: number; // Optional: Premium amount change
  };
}

/**
 * Reservation Data Definition
 */
export interface reservationData {
  type: 'object';
  required: ['claim_amount'];
  properties: {
    claim_amount: number; // Required: Amount to reserve coverage for
    reservation_reason: string; // Optional: Reason for reservation
    release_condition: string; // Optional: Condition for releasing reserved coverage
  };
}

/**
 * Coverage Information Response Schema
 */
export const coverageInfoResponse: ValidationSchema = {
  type: 'object',
  properties: {
    is_active: { type: 'boolean' }, // Whether policy is currently active
    policy_number: { type: 'string' },
    coverage_limits: {
      type: 'object',
      properties: {
        liability_bodily_injury: { type: 'number' },
        liability_property_damage: { type: 'number' },
        collision_deductible: { type: 'number' },
        comprehensive_deductible: { type: 'number' }
      },
      required: [] // All fields optional for backwards compatibility
    },
    covered_perils: {
      type: 'array',
      items: { type: 'string' }
    },
    endorsements: {
      type: 'array',
      items: {}
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Coverage Status Response Schema
 */
export const coverageStatusResponse: ValidationSchema = {
  type: 'object',
  properties: {
    claim_id: { type: 'string' },
    is_active: { type: 'boolean' },
    is_expired: { type: 'boolean' },
    coverage_percentage_used: { type: 'number' },
    remaining_coverage_days: { type: 'number' },
    status_flags: {
      type: 'object',
      properties: {
        active: { type: 'boolean' },
        current_period: { type: 'boolean' },
        no_cancellation: { type: 'boolean' }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Check Limits Response Schema
 */
export const checkLimitsResponse: ValidationSchema = {
  type: 'object',
  properties: {
    claim_id: { type: 'string' },
    remaining_limits: {
      type: 'object',
      properties: {
        liability_bodily_injury: { type: 'number' },
        liability_property_damage: { type: 'number' }
      }
    },
    current_deductible_amount: { type: 'number' },
    is_within_limits: { type: 'boolean' },
    claim_type: { type: 'string' },
    is_covered_peril: { type: 'boolean' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Endorsement Check Response Schema
 */
export const endorsementCheckResponse: ValidationSchema = {
  type: 'object',
  properties: {
    is_endorsed: { type: 'boolean' },
    endorsement_type: { type: 'string' },
    affects_claim_eligibility: { type: 'boolean' },
    additional_protections: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          type: { type: 'string' },
          status: { type: 'string' }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Reservation Response Schema
 */
export const reservationResponse: ValidationSchema = {
  type: 'object',
  properties: {
    reservation_id: { type: 'string' },
    is_reserved: { type: 'boolean' },
    reserved_amount: { type: 'number' },
    release_date: { type: 'string', format: 'date-time' },
    status: { type: 'string' }
  },
  required: [] // All fields optional for backwards compatibility
};

/**
 * Type definitions for validation errors
 */
export interface ValidationErrorType {
  field: string;
  message: string;
}

/**
 * Validation errors response structure
 */
export const validationErrorResponse: ValidationSchema = {
  type: 'object',
  properties: {
    error: { type: 'string' },
    details: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string' },
          message: { type: 'string' }
        }
      }
    }
  },
  required: [] // All fields optional for backwards compatibility
};
