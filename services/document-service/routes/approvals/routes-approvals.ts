/**
 * Document Service - Template Approval Workflow Routes (Phase P1.2)
 * 
   Provides approval and review endpoints for document templates
 */

import { Router, Request, Response } from 'express';
import templateService from '../services/templateService';
import { validationResult } from 'express-validator';

const router = Router();

/**
 * POST /api/approvals/requests - Submit Template Approval Request
 * 
   Submits a draft template for compliance review and approval
 */
router.post('/api/approvals/requests', async (req: Request, res: Response) => {
  try {
    const validationErrors = validationResult(req);
    if (!validationErrors.isEmpty()) {
      return res.status(400).json({ errors: validationErrors.mapped() });
    }

    // Extract approval request data from request body
    const approvalRequestData = req.body;

    // Create approval request record in service
    const approvalRequest = await templateService.createApprovalRequest(approvalRequestData);

    console.log(`[APPROVAL_REQUEST] Submitted for review: ${approvalRequest.request_id}`);

    return res.status(201).json(approvalRequest);
  } catch (error: any) {
    if (error.code === 'ALREADY_IN_REVIEW') {
      return res.status(409).json({ error: 'Template already under review' });
    }
    console.error('[APPROVAL_ROUTES] Failed to create approval request:', error.message);
    return res.status(500).json({ error: 'Failed to submit template for approval' });
  } finally {
    console.log('[APPROVAL_ROUTES] Request creation completed');
  }
});

/**
 * GET /api/approvals/requests - List Active Approval Requests (paginated)
 * 
   Returns list of templates awaiting compliance review
 */
router.get('/api/approvals/requests', async (req: Request, res: Response) => {
  try {
    const { page = 1, limit = 20 } = req.query;

    // Retrieve paginated approval requests from service
    const requests = await templateService.listApprovalRequests({
      page: parseInt(page as string),
      limit: parseInt(limit as string)
    });

    return res.json(requests);
  } catch (error: any) {
    console.error('[APPROVAL_ROUTES] Failed to list approval requests:', error.message);
    return res.status(500).json({ error: 'Failed to retrieve approval requests' });
  } finally {
    console.log('[APPROVAL_ROUTES] List operation completed');
  }
});

/**
 * GET /api/approvals/requests/:requestId - Get Approval Request Details
 * 
   Retrieves detailed information about an approval request including review status
 */
router.get('/api/approvals/requests/:requestId', async (req: Request, res: Response) => {
  try {
    const request = await templateService.getApprovalRequest(req.params.requestId);

    if (!request) {
      return res.status(404).json({ error: 'Approval request not found' });
    }

    return res.json(request);
  } catch (error: any) {
    console.error('[APPROVAL_ROUTES] Failed to retrieve approval request:', error.message);
    return res.status(500).json({ error: 'Failed to retrieve approval details' });
  } finally {
    console.log('[APPROVAL_ROUTES] Get operation completed');
  }
});

/**
 * POST /api/approvals/requests/:requestId/review - Submit Template Review Decision
 * 
   Compliance reviewer submits approval decision (approve/reject) with comments
 */
router.post('/api/approvals/requests/:requestId/review', async (req: Request, res: Response) => {
  try {
    const validationErrors = validationResult(req);
    if (!validationErrors.isEmpty()) {
      return res.status(400).json({ errors: validationErrors.mapped() });
    }

    // Extract review decision from request body
    const reviewData = req.body;

    // Process approval review and submit decision
    const result = await templateService.processApprovalReview(
      req.params.requestId,
      reviewData
    );

    return res.json(result);
  } catch (error: any) {
    if (error.code === 'ALREADY_REVIEWED') {
      return res.status(409).json({ error: 'This template has already been reviewed' });
    }
    console.error('[APPROVAL_ROUTES] Failed to process review:', error.message);
    return res.status(500).json({ error: 'Failed to submit review decision' });
  } finally {
    console.log('[APPROVAL_ROUTES] Review operation completed');
  }
});

/**
 * POST /api/approvals/templates/:templateId/approve - Approve Template Directly
 * 
   Compliance officer can approve draft template without full review workflow
 */
router.post('/api/approvals/templates/:templateId/approve', async (req: Request, res: Response) => {
  try {
    const validationErrors = validationResult(req);
    if (!validationErrors.isEmpty()) {
      return res.status(400).json({ errors: validationErrors.mapped() });
    }

    // Extract approval metadata from request body
    const approveData = req.body;

    // Approve template and activate version
    const result = await templateService.approveTemplateDirectly(
      req.params.templateId,
      approveData
    );

    console.log(`[TEMPLATE_APPROVAL] Approved template: ${req.params.templateId}`);

    return res.status(201).json(result);
  } catch (error: any) {
    console.error('[APPROVAL_ROUTES] Failed to approve template:', error.message);
    return res.status(500).json({ error: 'Failed to approve template' });
  } finally {
    console.log('[APPROVAL_ROUTES] Direct approval operation completed');
  }
});

/**
 * POST /api/approvals/templates/:templateId/reject - Reject Template Version
 * 
   Rejects a proposed template version with compliance reasons
 */
router.post('/api/approvals/templates/:templateId/reject', async (req: Request, res: Response) => {
  try {
    const validationErrors = validationResult(req);
    if (!validationErrors.isEmpty()) {
      return res.status(400).json({ errors: validationErrors.mapped() });
    }

    // Extract rejection data from request body
    const rejectData = req.body;

    // Reject template version and archive old content
    await templateService.rejectTemplateVersion(req.params.templateId, rejectData);

    return res.json({ message: 'Template version rejected successfully' });
  } catch (error: any) {
    console.error('[APPROVAL_ROUTES] Failed to reject template:', error.message);
    return res.status(500).json({ error: 'Failed to reject template version' });
  } finally {
    console.log('[APPROVAL_ROUTES] Rejection operation completed');
  }
});

/**
 * GET /api/approvals/workflow/history - Get Template Approval History
 * 
   Returns approval/rejection history for a specific template including all reviewers
 */
router.get('/api/approvals/workflow/:templateId/history', async (req: Request, res: Response) => {
  try {
    const history = await templateService.getApprovalWorkflowHistory(req.params.templateId);

    return res.json(history);
  } catch (error: any) {
    console.error('[APPROVAL_ROUTES] Failed to retrieve approval history:', error.message);
    return res.status(500).json({ error: 'Failed to retrieve approval workflow' });
  } finally {
    console.log('[APPROVAL_ROUTES] History operation completed');
  }
});

/**
 * DELETE /api/approvals/requests/:requestId - Cancel Approval Request
 * 
   Cancels pending approval request (requires proper authorization)
 */
router.delete('/api/approvals/requests/:requestId', async (req: Request, res: Response) => {
  try {
    const request = await templateService.getApprovalRequest(req.params.requestId);

    if (!request) {
      return res.status(404).json({ error: 'Approval request not found' });
    }

    // Verify requester has proper authorization
    if (request.status === 'under_review') {
      return res.status(403).json({ 
        error: 'Cannot cancel template under active review',
        reason: 'Waiting for compliance officer response'
      });
    }

    await templateService.cancelApprovalRequest(req.params.requestId);

    return res.json({ message: 'Approval request cancelled successfully' });
  } catch (error: any) {
    console.error('[APPROVAL_ROUTES] Failed to cancel approval request:', error.message);
    return res.status(500).json({ error: 'Failed to cancel approval request' });
  } finally {
    console.log('[APPROVAL_ROUTES] Cancel operation completed');
  }
});

export default router;
