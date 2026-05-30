/**
 * Claims Service - Payment Processing Routes (Phase P1.5)
 * 
   Provides payment initiation, processing, and tracking endpoints
 */

import { Router, Request, Response } from 'express';
import validatePaymentRequest from '../schemas/payment-schema';

const router = Router();

/**
 * POST /api/payment/initiate - Initiate Payment for Approved Claim
 * 
   Starts payment process for claim that has passed adjudication and fraud check
 */
router.post('/api/payment/initiate', async (req: Request, res: Response) => {
  try {
    const validationErrors = validatePaymentRequest(req.body);

    if (!validationErrors.valid) {
      return res.status(400).json({ 
        error: 'Invalid payment request',
        details: validationErrors.errors || []
      });
    }

    // Extract payment data from request
    const paymentData = req.body.payment;

    console.log(`[PAYMENT_ROUTES] Initiating payment for claim: ${paymentData.claim_id}`);

    return res.json({
      payment_id: `pay-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      status: 'initiated',
      amount: paymentData.claim_amount || 0,
      payment_method: paymentData.payment_method || 'ach',
      initiated_at: new Date().toISOString(),
      expected_completion: new Date(Date.now() + 7200000).toISOString(), // Within 2 hours
      fraud_check_status: 'pending'
    });
  } catch (error: any) {
    console.error('[PAYMENT_ROUTES] Failed to initiate payment:', error.message);
    return res.status(500).json({ 
      error: 'Failed to initiate payment for claim' 
    });
  } finally {
    console.log('[PAYMENT_ROUTES] Payment initiation operation completed');
  }
});

/**
 * POST /api/payment/process - Process Payment via Gateway
 * 
   Sends payment instruction to external payment gateway for processing
 */
router.post('/api/payment/process', async (req: Request, res: Response) => {
  try {
    const processingData = req.body.processing;

    // Process payment via gateway (simulated - real implementation would call gateway API)
    console.log(`[PAYMENT_ROUTES] Processing payment for claim`);

    return res.json({
      transaction_id: `txn-${Date.now()}`,
      status: 'completed',
      amount_processed: processingData.claim_amount || 0,
      gateway_response_code: 'APPROVED',
      processed_at: new Date().toISOString(),
      receipt_url: '/receipts/pay-' + process.env.PAYMENT_ID, // Would be actual URL in production
      confirmation_sent_to: 'email' // Would check customer preferences for SMS/email/etc.
    });
  } catch (error: any) {
    console.error('[PAYMENT_ROUTES] Failed to process payment:', error.message);
    return res.status(500).json({ 
      error: 'Failed to process payment via gateway' 
    });
  } finally {
    console.log('[PAYMENT_ROUTES] Payment processing operation completed');
  }
});

/**
 * GET /api/payment/:paymentId/status - Get Payment Status
 * 
   Retrieves current status of payment including gateway response, fraud check result, etc.
 */
router.get('/api/payment/:paymentId/status', async (req: Request, res: Response) => {
  try {
    const paymentId = req.params.paymentId;

    // Get payment status (real implementation would query payments database)
    console.log(`[PAYMENT_ROUTES] Checking status for payment: ${paymentId}`);

    return res.json({
      payment_id: paymentId,
      status: 'completed', // Would query from payments database
      amount: 2500.00,
      claim_amount: 2750.00,
      deduction_type: 'deductible',
      deduction_amount: 250.00,
      fraud_check_status: 'cleared',
      gateway_status: 'processed',
      initiated_at: new Date(Date.now() - 1800000).toISOString(),
      completed_at: new Date().toISOString()
    });
  } catch (error: any) {
    console.error('[PAYMENT_ROUTES] Failed to check payment status:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve payment status' 
    });
  } finally {
    console.log('[PAYMENT_ROUTES] Status check operation completed');
  }
});

/**
 * POST /api/payment/cancel - Cancel Payment Before Processing
 * 
   Cancels pending payment that hasn't been processed by gateway yet
 */
router.post('/api/payment/cancel', async (req: Request, res: Response) => {
  try {
    const cancellationData = req.body.cancellation;

    // Cancel payment (real implementation would query payments database)
    console.log(`[PAYMENT_ROUTES] Cancelling pending payment`);

    return res.json({
      message: 'Payment cancelled successfully',
      cancelled_at: new Date().toISOString(),
      reason: cancellationData.reason || 'Cancelled by customer'
    });
  } catch (error: any) {
    console.error('[PAYMENT_ROUTES] Failed to cancel payment:', error.message);
    return res.status(500).json({ 
      error: 'Failed to cancel payment' 
    });
  } finally {
    console.log('[PAYMENT_ROUTES] Payment cancellation operation completed');
  }
});

/**
 * POST /api/reimbursement/setup - Set Up Reimbursement Account
 * 
   Configures reimbursement tracking and ACH/EFT direct deposit for claim payments
 */
router.post('/api/reimbursement/setup', async (req: Request, res: Response) => {
  try {
    const setupData = req.body.setup;

    // Set up reimbursement account (real implementation would query customers database)
    console.log(`[PAYMENT_ROUTES] Setting up reimbursement for claim`);

    return res.json({
      reimbursement_id: `reimb-${Date.now()}`,
      status: 'active',
      payment_method: setupData.payment_method || 'ach',
      bank_account_last_four: setupData.bank_account_last_four || '****',
      routing_number_last_four: setupData.routing_number_last_four || '****',
      established_at: new Date().toISOString(),
      can_process_direct_deposit: true,
      processing_fee_percentage: 0 // Direct deposit typically has no fee in production
    });
  } catch (error: any) {
    console.error('[PAYMENT_ROUTES] Failed to set up reimbursement:', error.message);
    return res.status(500).json({ 
      error: 'Failed to set up reimbursement account' 
    });
  } finally {
    console.log('[PAYMENT_ROUTES] Reimbursement setup operation completed');
  }
});

/**
 * GET /api/payment/:paymentId/receipt - Get Payment Receipt
 * 
   Retrieves official payment receipt with transaction details and confirmation
 */
router.get('/api/payment/:paymentId/receipt', async (req: Request, res: Response) => {
  try {
    const paymentId = req.params.paymentId;

    // Generate payment receipt (real implementation would query payments database)
    console.log(`[PAYMENT_ROUTES] Generating receipt for payment: ${paymentId}`);

    return res.json({
      receipt_id: `rec-${paymentId}`,
      payment_id: paymentId,
      status: 'completed',
      amount_paid: 2500.00,
      claim_amount: 2750.00,
      deductible_deduction: 250.00,
      processing_date: new Date().toISOString(),
      customer_name: 'John Doe', // Would query from customers table in production
      payment_method_used: 'ach'
    });
  } catch (error: any) {
    console.error('[PAYMENT_ROUTES] Failed to generate receipt:', error.message);
    return res.status(500).json({ 
      error: 'Failed to generate payment receipt' 
    });
  } finally {
    console.log('[PAYMENT_ROUTES] Receipt generation operation completed');
  }
});

/**
 * POST /api/check/generate - Generate Replacement Check
 * 
   Creates and sends replacement check for claim payment if electronic transfer fails or customer prefers paper
 */
router.post('/api/check/generate', async (req: Request, res: Response) => {
  try {
    const checkData = req.body.check;

    // Generate replacement check (real implementation would integrate with check printing service)
    console.log(`[PAYMENT_ROUTES] Generating replacement check`);

    return res.json({
      check_number: `CHK-${Date.now()}`,
      status: 'generated',
      amount: checkData.claim_amount || 0,
      generated_at: new Date().toISOString(),
      mail_status: 'pending', // Would integrate with postal tracking in production
      processing_fee: 2.50 // Paper check printing fee
    });
  } catch (error: any) {
    console.error('[PAYMENT_ROUTES] Failed to generate check:', error.message);
    return res.status(500).json({ 
      error: 'Failed to generate replacement check' 
    });
  } finally {
    console.log('[PAYMENT_ROUTES] Check generation operation completed');
  }
});

/**
 * GET /api/payment/:paymentId/track - Track Payment Delivery Status
 * 
   Tracks delivery status of payment (for checks, tracking number for mailed documents)
 */
router.get('/api/payment/:paymentId/track', async (req: Request, res: Response) => {
  try {
    const paymentId = req.params.paymentId;

    // Track payment delivery (real implementation would query tracking services)
    console.log(`[PAYMENT_ROUTES] Tracking delivery for payment: ${paymentId}`);

    return res.json({
      payment_id: paymentId,
      delivery_status: 'in_transit', // Would check with carrier API in production
      tracking_number: `TRACK-${Date.now()}`,
      estimated_delivery_date: new Date(Date.now() + 57600000).toISOString(),
      carrier: 'USPS'
    });
  } catch (error: any) {
    console.error('[PAYMENT_ROUTES] Failed to track delivery:', error.message);
    return res.status(500).json({ 
      error: 'Failed to track payment delivery status' 
    });
  } finally {
    console.log('[PAYMENT_ROUTES] Tracking operation completed');
  }
});

export default router;
