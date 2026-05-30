/**
 * Event Broker Adapter - Dead-Letter Queue Routes (Phase P1.3)
 * 
   Provides DLQ management and failed message reprocessing endpoints
 */

import { Router, Request, Response } from 'express';
import dlqService from '../services/dlqService';

const router = Router();

/**
 * GET /api/dlq/messages - List Dead-Letter Queue Messages (paginated)
 * 
   Returns list of messages that failed to publish and were moved to DLQ
 */
router.get('/api/dlq/messages', async (req: Request, res: Response) => {
  try {
    const options = {
      page: parseInt(req.query.page as string) || 1,
      limit: parseInt(req.query.limit as string) || 20
    };

    // List DLQ messages with pagination
    const result = await dlqService.listDlqMessages(options);

    return res.json(result);
  } catch (error: any) {
    console.error('[DLQ_ROUTES] Failed to list DLQ messages:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve dead-letter queue messages' 
    });
  } finally {
    console.log('[DLQ_ROUTES] List operation completed');
  }
});

/**
 * GET /api/dlq/messages/:messageId - Get Failed Message Details
 * 
   Retrieves detailed information about a specific failed message including retry history
 */
router.get('/api/dlq/messages/:messageId', async (req: Request, res: Response) => {
  try {
    const messageId = req.params.messageId;

    // Get failed message details
    const message = await dlqService.getFailedMessage(messageId);

    if (!message) {
      return res.status(404).json({ 
        error: 'Failed message not found in DLQ' 
      });
    }

    return res.json(message);
  } catch (error: any) {
    console.error('[DLQ_ROUTES] Failed to retrieve message:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve failed message details' 
    });
  } finally {
    console.log('[DLQ_ROUTES] Get operation completed');
  }
});

/**
 * POST /api/dlq/retry/:messageId - Retry Failed Message
 * 
   Re-attempts failed message to original broker with exponential backoff
 */
router.post('/api/dlq/retry/:messageId', async (req: Request, res: Response) => {
  try {
    const messageId = req.params.messageId;

    // Check if retry is permitted (not exceeded max retries)
    const message = await dlqService.getFailedMessage(messageId);

    if (!message) {
      return res.status(404).json({ 
        error: 'Failed message not found in DLQ' 
      });
    }

    // Check if already exceeded max retry attempts
    if (message.retry_count >= 3) {
      return res.status(409).json({ 
        error: 'Message exceeded maximum retry attempts',
        reason: 'Message moved to permanent dead letter queue'
      });
    }

    // Retry failed message
    const result = await dlqService.retryMessage(messageId);

    console.log(`[DLQ_ROUTES] Retried message: ${messageId}`);

    return res.json(result);
  } catch (error: any) {
    console.error('[DLQ_ROUTES] Failed to retry message:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retry dead-letter queue message' 
    });
  } finally {
    console.log('[DLQ_ROUTES] Retry operation completed');
  }
});

/**
 * POST /api/dlq/purge - Purge Old DLQ Messages
 * 
   Removes messages from DLQ that are older than specified age threshold
 */
router.post('/api/dlq/purge', async (req: Request, res: Response) => {
  try {
    const ageInHours = parseInt(req.query.ageInHours as string) || 24;

    // Purge old messages from DLQ
    await dlqService.purgeOldMessages(ageInHours);

    console.log(`[DLQ_ROUTES] Purged DLQ messages older than ${ageInHours} hours`);

    return res.json({ 
      message: `Purged DLQ messages older than ${ageInHours} hours`,
      timestamp: new Date().toISOString()
    });
  } catch (error: any) {
    console.error('[DLQ_ROUTES] Failed to purge DLQ messages:', error.message);
    return res.status(500).json({ 
      error: 'Failed to purge dead-letter queue messages' 
    });
  } finally {
    console.log('[DLQ_ROUTES] Purge operation completed');
  }
});

/**
 * POST /api/dlq/reprocess/:messageId - Reprocess with Modified Payload
 * 
   Reprocesses failed message with specified modifications to payload
 */
router.post('/api/dlq/reprocess/:messageId', async (req: Request, res: Response) => {
  try {
    const messageId = req.params.messageId;

    // Extract modifications from request body
    const modifications = req.body.modifications || {};

    if (!modifications || typeof modifications !== 'object') {
      return res.status(400).json({ 
        error: 'Validations required modifications object' 
      });
    }

    // Reprocess message with modifications
    const result = await dlqService.reprocessMessage(messageId, modifications);

    console.log(`[DLQ_ROUTES] Reprocessing message: ${messageId}`);

    return res.json(result);
  } catch (error: any) {
    console.error('[DLQ_ROUTES] Failed to reprocess message:', error.message);
    return res.status(500).json({ 
      error: 'Failed to reprocess dead-letter queue message' 
    });
  } finally {
    console.log('[DLQ_ROUTES] Reprocess operation completed');
  }
});

/**
 * DELETE /api/dlq/messages/:messageId - Discard Failed Message Permanently
 * 
   Removes failed message from DLQ permanently (requires admin authorization)
 */
router.delete('/api/dlq/messages/:messageId', async (req: Request, res: Response) => {
  try {
    const messageId = req.params.messageId;

    // Check if user has admin authorization
    if (!req.user?.isAdmin) {
      return res.status(403).json({ 
        error: 'Admin authorization required to permanently discard message' 
      });
    }

    // Discard message from DLQ permanently
    await dlqService.discardMessage(messageId);

    console.log(`[DLQ_ROUTES] Discarded message: ${messageId}`);

    return res.json({ 
      message: `Discarded message ${messageId} permanently`,
      timestamp: new Date().toISOString()
    });
  } catch (error: any) {
    console.error('[DLQ_ROUTES] Failed to discard message:', error.message);
    return res.status(500).json({ 
      error: 'Failed to discard dead-letter queue message' 
    });
  } finally {
    console.log('[DLQ_ROUTES] Discard operation completed');
  }
});

/**
 * GET /api/dlq/statistics - Get DLQ Statistics
 * 
   Returns statistics about dead-letter queue including message counts and age distribution
 */
router.get('/api/dlq/statistics', async (req: Request, res: Response) => {
  try {
    // Get DLQ statistics
    const statistics = await dlqService.getDlqStatistics();

    return res.json(statistics);
  } catch (error: any) {
    console.error('[DLQ_ROUTES] Failed to retrieve DLQ statistics:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve dead-letter queue statistics' 
    });
  } finally {
    console.log('[DLQ_ROUTES] Statistics operation completed');
  }
});

export default router;
