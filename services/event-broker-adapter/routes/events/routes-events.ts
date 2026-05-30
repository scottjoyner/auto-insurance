/**
 * Event Broker Adapter - Event Publishing Routes (Phase P1.3)
 * 
   Provides event publishing and management endpoints with multi-broker support
 */

import { Router, Request, Response } from 'express';
import brokerService from '../services/brokerService';

const router = Router();

/**
 * POST /api/events/publish - Publish Event to All Brokers
 * 
   Sends an event to all configured brokers (Kafka, SNS, PubSub) and tracks publication status
 */
router.post('/api/events/publish', async (req: Request, res: Response) => {
  try {
    // Extract event data from request body
    const eventData = req.body;

    // Validate required fields
    if (!eventData.event_type || !eventData.payload) {
      return res.status(400).json({ 
        error: 'Missing required fields: event_type, payload' 
      });
    }

    // Publish event to brokers
    const result = await brokerService.publishEvent(eventData);

    console.log(`[EVENT_ROUTES] Published event: ${result.id}`);

    return res.status(201).json(result);
  } catch (error: any) {
    console.error('[EVENT_ROUTES] Failed to publish event:', error.message);
    return res.status(500).json({ 
      error: 'Failed to publish event to brokers' 
    });
  } finally {
    console.log('[EVENT_ROUTES] Publish operation completed');
  }
});

/**
 * POST /api/events/batch - Batch Publish Multiple Events
 * 
   Publishes multiple events in a single batch operation for efficiency
 */
router.post('/api/events/batch', async (req: Request, res: Response) => {
  try {
    // Extract batch event data from request body
    const events = req.body.events;

    if (!Array.isArray(events) || events.length === 0) {
      return res.status(400).json({ 
        error: 'events array required and must contain at least one event' 
      });
    }

    // Validate each event
    const invalidEvents = events.filter(e => !e.event_type);

    if (invalidEvents.length > 0) {
      return res.status(400).json({ 
        error: 'Some events missing required fields',
        invalidCount: invalidEvents.length
      });
    }

    // Batch publish events
    const result = await brokerService.batchPublish(events);

    console.log(`[EVENT_ROUTES] Batch published ${result.count} events`);

    return res.json(result);
  } catch (error: any) {
    console.error('[EVENT_ROUTES] Failed to batch publish:', error.message);
    return res.status(500).json({ 
      error: 'Failed to batch publish events' 
    });
  } finally {
    console.log('[EVENT_ROUTES] Batch operation completed');
  }
});

/**
 * GET /api/events/:eventId/status - Check Publication Status
 * 
   Retrieves publication status for a specific event across all brokers
 */
router.get('/api/events/:eventId/status', async (req: Request, res: Response) => {
  try {
    const eventId = req.params.eventId;

    // Check publication status
    const status = await brokerService.getPublicationStatus(eventId);

    return res.json(status);
  } catch (error: any) {
    console.error('[EVENT_ROUTES] Failed to check status:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve event publication status' 
    });
  } finally {
    console.log('[EVENT_ROUTES] Status check completed');
  }
});

/**
 * GET /api/events - List Recent Published Events (paginated)
 * 
   Returns list of recently published events with metadata
 */
router.get('/api/events', async (req: Request, res: Response) => {
  try {
    // Mock pagination (real implementation would query event log/database)
    const page = Math.max(1, parseInt(req.query.page as string) || 1);
    const limit = Math.min(100, parseInt(req.query.limit as string) || 20);

    return res.json({
      events: [], // Would come from database in production
      pagination: { page, limit }
    });
  } catch (error: any) {
    console.error('[EVENT_ROUTES] Failed to list events:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve published events' 
    });
  } finally {
    console.log('[EVENT_ROUTES] List operation completed');
  }
});

/**
 * GET /api/events/:eventId - Get Event Details
 * 
   Retrieves detailed information about a specific event including publication status
 */
router.get('/api/events/:eventId', async (req: Request, res: Response) => {
  try {
    const eventId = req.params.eventId;

    // Mock lookup (real implementation would query event log/database)
    return res.json({
      id: eventId,
      event_type: 'quote_submitted',
      payload: {},
      timestamp: new Date().toISOString(),
      status: 'published'
    });
  } catch (error: any) {
    console.error('[EVENT_ROUTES] Failed to retrieve event:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve event details' 
    });
  } finally {
    console.log('[EVENT_ROUTES] Get operation completed');
  }
});

export default router;
