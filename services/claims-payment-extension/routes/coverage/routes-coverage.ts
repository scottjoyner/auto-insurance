/**
 * Claims Service - Coverage Validation Routes (Phase P1.5)
 * 
   Provides coverage verification endpoints for claim submissions
 */

import { Router, Request, Response } from 'express';
import { validateCoverageRequest } from '../schemas/coverage-schema';

const router = Router();

/**
 * POST /api/coverage/verify - Verify Policy Active Status Before Claim
 * 
   Checks if policy is active and eligible for claim submission before proceeding
 */
router.post('/api/coverage/verify', async (req: Request, res: Response) => {
  try {
    const validationErrors = validateCoverageRequest(req.body);

    if (!validationErrors.valid) {
      return res.status(400).json({ 
        error: 'Invalid coverage request',
        details: validationErrors.errors || []
      });
    }

    // Verify policy active status (real implementation would query claims database)
    const claimData = req.body.claim;

    console.log(`[COVERAGE_ROUTES] Verifying coverage for claim: ${claimData.}`);

    return res.json({
      is_active: true, // Would check in production
      policy_number: claimData.policy_number || 'POL-001',
      coverage_limits: {
        liability_bodily_injury: 100000,
        liability_property_damage: 50000,
        collision_deductible: 500
      },
      endorsements: [] // Would query endorsement records in production
    });
  } catch (error: any) {
    console.error('[COVERAGE_ROUTES] Failed to verify coverage:', error.message);
    return res.status(500).json({ 
      error: 'Failed to verify policy active status' 
    });
  } finally {
    console.log('[COVERAGE_ROUTES] Verification operation completed');
  }
});

/**
 * GET /api/coverage/:claimId - Get Coverage Details for Claim
 * 
   Retrieves coverage details including limits, deductibles, and active status
 */
router.get('/api/coverage/:claimId', async (req: Request, res: Response) => {
  try {
    const claimId = req.params.claimId;

    // Retrieve coverage details for claim (real implementation would query claims database)
    console.log(`[COVERAGE_ROUTES] Retrieving coverage for claim: ${claimId}`);

    return res.json({
      claim_id: claimId,
      policy_number: 'POL-001',
      is_active: true,
      coverage_limits: {
        liability_bodily_injury: 100000,
        liability_property_damage: 50000,
        collision_deductible: 500,
        comprehensive_deductible: 1000
      },
      covered_perils: [
        'collision',
        'comprehensive',
        'liability_bodily_injury',
        'liability_property_damage'
      ],
      endorsements: [] // Would query endorsement records in production
    });
  } catch (error: any) {
    console.error('[COVERAGE_ROUTES] Failed to retrieve coverage:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve coverage details' 
    });
  } finally {
    console.log('[COVERAGE_ROUTES] Coverage retrieval operation completed');
  }
});

/**
 * GET /api/coverage/check/:claimId - Check Coverage Limits and Deductibles
 * 
   Specifically checks remaining limits and deductible amounts for current claim
 */
router.get('/api/coverage/check/:claimId', async (req: Request, res: Response) => {
  try {
    const claimId = req.params.claimId;

    // Check coverage limits and deductibles (real implementation would query claims database)
    console.log(`[COVERAGE_ROUTES] Checking coverage for claim: ${claimId}`);

    return res.json({
      claim_id: claimId,
      remaining_limits: {
        liability_bodily_injury: 95000, // Would calculate from claims paid to date
        liability_property_damage: 45000
      },
      current_deductible_amount: 500,
      is_within_limits: true, // Would check against actual claim amount in production
      claim_type: 'collision',
      is_covered_peril: true
    });
  } catch (error: any) {
    console.error('[COVERAGE_ROUTES] Failed to check coverage:', error.message);
    return res.status(500).json({ 
      error: 'Failed to check coverage limits' 
    });
  } finally {
    console.log('[COVERAGE_ROUTES] Coverage check operation completed');
  }
});

/**
 * POST /api/coverage/check-endorsement - Check Endorsement Impact on Claim
 * 
   Evaluates how endorsements affect current claim eligibility and coverage
 */
router.post('/api/coverage/check-endorsement', async (req: Request, res: Response) => {
  try {
    const endorsementData = req.body.endorsement;

    // Check endorsement impact on claim (real implementation would query endorsement records)
    console.log(`[COVERAGE_ROUTES] Checking endorsement impact for claim`);

    return res.json({
      is_endorsed: true,
      endorsement_type: 'added_coverage',
      affects_claim_eligibility: false,
      additional_protections: [
        { type: 'additional_insured', status: 'active' },
        { type: 'scheduled_personal_property', status: 'pending' }
      ] // Would query endorsement details in production
    });
  } catch (error: any) {
    console.error('[COVERAGE_ROUTES] Failed to check endorsement:', error.message);
    return res.status(500).json({ 
      error: 'Failed to check endorsement impact' 
    });
  } finally {
    console.log('[COVERAGE_ROUTES] Endorsement check operation completed');
  }
});

/**
 * GET /api/coverage/status/:claimId - Get Overall Coverage Status
 * 
   Returns comprehensive coverage status including active flags, limits, etc.
 */
router.get('/api/coverage/status/:claimId', async (req: Request, res: Response) => {
  try {
    const claimId = req.params.claimId;

    // Get overall coverage status (real implementation would query claims database)
    console.log(`[COVERAGE_ROUTES] Getting coverage status for claim: ${claimId}`);

    return res.json({
      claim_id: claimId,
      is_active: true,
      is_expired: false,
      coverage_percentage_used: 45, // Would calculate from claims paid to date
      remaining_coverage_days: 91, // Assuming 365 day policy term
      status_flags: {
        active: true,
        current_period: true,
        no_cancellation: true
      }
    });
  } catch (error: any) {
    console.error('[COVERAGE_ROUTES] Failed to get coverage status:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve coverage status' 
    });
  } finally {
    console.log('[COVERAGE_ROUTES] Status retrieval operation completed');
  }
});

/**
 * POST /api/coverage/reserve - Reserve Coverage for Pending Claim
 * 
   Sets aside coverage amount while claim is being adjudicated
 */
router.post('/api/coverage/reserve', async (req: Request, res: Response) => {
  try {
    const reservationData = req.body.reservation;

    // Reserve coverage amount (real implementation would query claims database)
    console.log(`[COVERAGE_ROUTES] Reserving coverage for pending claim`);

    return res.json({
      reservation_id: `res-${Date.now()}`,
      is_reserved: true,
      reserved_amount: reservationData.claim_amount || 0,
      release_date: new Date(Date.now() + 86400000).toISOString(), // Release after 1 day if not paid
      status: 'reserved'
    });
  } catch (error: any) {
    console.error('[COVERAGE_ROUTES] Failed to reserve coverage:', error.message);
    return res.status(500).json({ 
      error: 'Failed to reserve coverage for pending claim' 
    });
  } finally {
    console.log('[COVERAGE_ROUTES] Coverage reservation operation completed');
  }
});

export default router;
