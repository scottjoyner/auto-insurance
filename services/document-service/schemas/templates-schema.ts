/**
 * Document Service - API Request/Response Schemas (Phase P1.2)
 * 
   Provides type definitions and schema validation rules for all document service endpoints
 */

import { validationResult } from 'express-validator';

/**
 * Template Creation Schema
 */
export interface CreateTemplateRequest {
  /** Document type identifier (one of the 10+ supported types) */
  document_type: string;
  
  /** Version number (e.g., "1.0", "2.1") */
  version: string;
  
  /** Template status ("draft", "approved", "deprecated", "archived") */
  status?: 'draft' | 'approved' | 'deprecated' | 'archived';
  
  /** User ID who created this template */
  created_by?: string;
  
  /** Jinja2-style content template with variable placeholders */
  content_template: string;
  
  /** Document variables metadata for validation (optional) */
  variables?: Array<CreateTemplateVariable>;
  
  /** Template category for organizational grouping (optional) */
  template_category?: string;
  
  /** Whether compliance review is required before activation (optional, defaults to true) */
  requires_approval?: boolean;
}

/**
 * Variable definition in template creation request
 */
export interface CreateTemplateVariable {
  /** Variable identifier (e.g., "customer_name") */
  name: string;
  
  /** Variable type ("string", "number", etc.) */
  type: 'string' | 'number' | 'boolean';
  
  /** Whether variable is required in document generation */
  required?: boolean;
  
  /** Format specification for numbers (optional) */
  format?: 'currency' | 'date' | 'datetime' | 'percentage';
}

/**
 * Template Upgrade Request Schema
 */
export interface TemplateUpgradeRequest {
  /** Updated content template for new version */
  content_template: string;
  
  /** New version number (optional, auto-incremented if not specified) */
  version?: string;
  
  /** Deprecation note for previous versions (optional) */
  deprecation_note?: string;
  
  /** User ID who initiated upgrade (optional, from auth context) */
  changed_by?: string;
}

/**
 * Template Deprecation Request Schema
 */
export interface TemplateDeprecateRequest {
  /** Reason for deprecation */
  reason: string;
  
  /** Replacement template ID (if available) */
  replacement_template_id?: string;
  
  /** Additional notes about deprecation */
  notes?: string;
}

/**
 * Document Generation Request Schema
 */
export interface DocumentGenerationRequest {
  /** Template ID to use for generation */
  template_id: string;
  
  /** Customer data for personalization */
  customer_data: Record<string, any>;
  
  /** Owner/user ID generating this document */
  owner_id?: string;
  
  /** Generation mode ("sync", "async") */
  generation_mode?: 'sync' | 'async';
}

/**
 * Customer Data Object for Document Personalization
 */
export interface CustomerData {
  /** Customer full name */
  customer_name?: string;
  
  /** Policy number */
  policy_number?: string;
  
  /** Coverage start date */
  coverage_period_start?: string; // ISO format
  
  /** Coverage end date */
  coverage_period_end?: string; // ISO format
  
  /** Premium amount due */
  premium_amount?: number;
  
  /** Liability bodily injury limit */
  liability_bodily_injury?: number;
  
  /** Liability property damage limit */
  liability_property_damage?: number;
  
  /** Collision deductible */
  collision_deductible?: number;
  
  /** Comprehensive deductible */
  comprehensive_deductible?: number;
  
  /** Company name (optional, for letterhead) */
  company_name?: string;
  
  /** Company address (optional, for letterhead) */
  company_address?: string;
}

/**
 * Document Version Metadata
 */
export interface GeneratedDocument {
  /** Unique document identifier */
  id: string;
  
  /** Template ID used for generation */
  template_id: string;
  
  /** Customer data that was used */
  customer_data: Record<string, any>;
  
  /** Document status ("generated", "pending_review", "approved", etc.) */
  status: 'generated' | 'pending_review' | 'approved' | 'rejected';
  
  /** Timestamp when document was generated */
  generated_at: string; // ISO format
  
  /** PDF URL for downloading (computed property) */
  pdf_url?: string;
  
  /** Filename for download (computed property) */
  filename?: string;
  
  /** Owner/user ID of this document */
  owner_id?: string;
  
  /** Document type identifier */
  document_type?: string;
  
  /** Whether PDF has been generated */
  generated: boolean;
}

/**
 * Approval Request Schema
 */
export interface ApprovalRequest {
  /** Unique approval request identifier */
  id: string;
  
  /** Template ID under review */
  template_id: string;
  
  /** Request status ("under_review", "completed", "cancelled") */
  status: 'under_review' | 'completed' | 'cancelled';
  
  /** User ID who submitted approval request */
  requested_by: string;
  
  /** Timestamp when request was submitted */
  requested_at: string; // ISO format
  
  /** Assigned compliance officer (may be "pending_assignment") */
  compliance_officer?: string;
}

/**
 * Review Decision Schema
 */
export interface ApprovalReviewRequest {
  /** Review decision ("approve" or "reject") */
  decision: 'approve' | 'reject';
  
  /** Reviewer comments (optional) */
  notes?: string;
}

/**
 * Document Validation Rules (for client-side validation before API calls)
 */
export const DOCUMENT_VALIDATION_RULES = {
  template_type: /^[a-z_]+$/, // Must match document_type enum
  version_pattern: /^\d+\.\d+$/, // Semantic versioning (e.g., "1.0", "2.1")
  required_variables: ['customer_name', 'policy_number', 'coverage_period_start'],
  
  customerDataRequiredFields: [
    'customer_name',
    'policy_number'
  ] as Array<keyof CustomerData>,
  
  customerDataOptionalFields: [] as Array<keyof CustomerData>
};

/**
 * Document validation middleware function
 */
export function validateDocumentRequest(request: any): { 
  valid: boolean; 
  errors?: Array<{ field: string; message: string }>; 
} {
  const schema = request.schema;
  const data = request.data;
  
  // Check required fields
  const missingRequired = DOCUMENT_VALIDATION_RULES.requiredFields.map((field) => {
    if (data[field] === undefined || data[field] === null) {
      return `Missing required field: ${field}`;
    }
    return null;
  }).filter(Boolean);
  
  // Check field types
  const typeErrors = Object.entries(schema.properties).map(([field, rules]) => {
    const dataValue = data[field];
    
    if (dataValue === undefined || dataValue === null) {
      return null; // Skip required field check here
    }
    
    if (typeof dataValue !== typeof schema.properties[field].type) {
      return `Invalid type for field: ${field}`;
    }
    
    return null;
  }).filter(Boolean);
  
  return { 
    valid: missingRequired.length === 0 && typeErrors.length === 0,
    errors: [...missingRequired, ...typeErrors]
  };
}

export default {}; // Placeholder - use schema definitions above directly
