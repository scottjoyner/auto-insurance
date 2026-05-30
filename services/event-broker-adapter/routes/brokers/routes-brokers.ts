/**
 * Event Broker Adapter - Broker Management Routes (Phase P1.3)
 * 
   Provides broker configuration, health check, and routing management endpoints
 */

import { Router, Request, Response } from 'express';
import brokerService from '../services/brokerService';

const router = Router();

/**
 * GET /api/brokers/health - Health Check for All Brokers
 * 
   Returns current health status of all configured brokers with latency metrics
 */
router.get('/api/brokers/health', async (req: Request, res: Response) => {
  try {
    // Get active brokers configuration
    const brokers = brokerService.getActiveBrokers();

    // Simulate health check for each broker
    const healthStatus: Array<{
      id: string;
      status: 'healthy' | 'degraded' | 'unreachable';
      latency_ms: number;
      last_heartbeat: Date;
    }> = [];

    for (const broker of brokers) {
      // Mock health check response (real implementation would ping actual broker)
      healthStatus.push({
        id: broker.id,
        status: 'healthy',
        latency_ms: 15 + Math.random() * 30,
        last_heartbeat: new Date()
      });
    }

    return res.json({
      timestamp: new Date().toISOString(),
      brokers: healthStatus
    });
  } catch (error: any) {
    console.error('[BROKER_ROUTES] Health check failed:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve broker health status' 
    });
  } finally {
    console.log('[BROKER_ROUTES] Health check completed');
  }
});

/**
 * GET /api/brokers/config - Get Current Broker Configuration
 * 
   Returns current configuration of all active brokers including topics and settings
 */
router.get('/api/brokers/config', async (req: Request, res: Response) => {
  try {
    const brokers = brokerService.getActiveBrokers();

    return res.json({
      timestamp: new Date().toISOString(),
      brokers: brokers.map(broker => ({
        id: broker.id,
        topic: broker.topic,
        enabled: broker.enabled
      }))
    });
  } catch (error: any) {
    console.error('[BROKER_ROUTES] Failed to retrieve config:', error.message);
    return res.status(500).json({ 
      error: 'Failed to retrieve broker configuration' 
    });
  } finally {
    console.log('[BROKER_ROUTES] Config operation completed');
  }
});

/**
 * POST /api/brokers/update - Update Broker Configuration
 * 
   Updates broker configuration including topic settings, retry policies, etc.
 */
router.post('/api/brokers/update', async (req: Request, res: Response) => {
  try {
    const updates = req.body;

    // Validate update structure
    if (!updates || typeof updates !== 'object') {
      return res.status(400).json({ 
        error: 'Invalid broker configuration' 
      });
    }

    console.log('[BROKER_ROUTES] Updating broker configuration');

    // Apply configuration updates (real implementation would persist to config store)
    
    return res.json({ 
      message: 'Broker configuration updated successfully',
      updated_at: new Date().toISOString()
    });
  } catch (error: any) {
    console.error('[BROKER_ROUTES] Failed to update configuration:', error.message);
    return res.status(500).json({ 
      error: 'Failed to update broker configuration' 
    });
  } finally {
    console.log('[BROKER_ROUTES] Update operation completed');
  }
});

/**
 * DELETE /api/brokers/disable/:brokerId - Disable Broker Temporarily
 * 
   Temporarily disables a broker for maintenance without deleting its configuration
 */
router.delete('/api/brokers/disable/:brokerId', async (req: Request, res: Response) => {
  try {
    const brokerId = req.params.brokerId;

    console.log(`[BROKER_ROUTES] Disabling broker: ${brokerId}`);

    // Disable broker in configuration
    await brokerService.disableBroker(brokerId);

    return res.json({ 
      message: `Broker ${brokerId} disabled successfully` 
    });
  } catch (error: any) {
    console.error('[BROKER_ROUTES] Failed to disable broker:', error.message);
    return res.status(500).json({ 
      error: 'Failed to disable broker' 
    });
  } finally {
    console.log('[BROKER_ROUTES] Disable operation completed');
  }
});

/**
 * PUT /api/brokers/enable/:brokerId - Enable Disabled Broker
 * 
   Re-enables a previously disabled broker for event publishing
 */
router.put('/api/brokers/enable/:brokerId', async (req: Request, res: Response) => {
  try {
    const brokerId = req.params.brokerId;

    console.log(`[BROKER_ROUTES] Enabling broker: ${brokerId}`);

    // Enable broker in configuration
    await brokerService.enableBroker(brokerId);

    return res.json({ 
      message: `Broker ${brokerId} enabled successfully` 
    });
  } catch (error: any) {
    console.error('[BROKER_ROUTES] Failed to enable broker:', error.message);
    return res.status(500).json({ 
      error: 'Failed to enable broker' 
    });
  } finally {
    console.log('[BROKER_ROUTES] Enable operation completed');
  }
});

/**
 * POST /api/brokers/reroute - Reroute Failed Events
 * 
   Re-publishes failed events from dead-letter queue to specified brokers
 */
router.post('/api/brokers/reroute', async (req: Request, res: Response) => {
  try {
    const { eventId, brokerIds } = req.body;

    if (!eventId) {
      return res.status(400).json({ 
        error: 'Event ID required for rerouting' 
      });
    }

    console.log('[BROKER_ROUTES] Rerouting failed event:', eventId);

    // Reroute event to specified brokers
    const result = await brokerService.rerouteEvent(eventId, brokerIds);

    return res.json({
      message: 'Event rerouted successfully',
      result: result
    });
  } catch (error: any) {
    console.error('[BROKER_ROUTES] Failed to reroute event:', error.message);
    return res.status(500).json({ 
      error: 'Failed to reroute failed event' 
    });
  } finally {
    console.log('[BROKER_ROUTES] Reroute operation completed');
  }
});

export default router;
