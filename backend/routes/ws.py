"""
WebSocket routes for the Amazon Product Analysis backend.
"""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.config import settings
from backend.services import redis_service, websocket_manager

# Configure logging
logger = logging.getLogger(__name__)

# Create WebSocket router
router = APIRouter(tags=["WebSocket"])


async def redis_subscriber(channel_name: str):
    """
    Background task that subscribes to Redis and broadcasts messages to WebSocket clients.
    
    Args:
        channel_name: The Redis channel to subscribe to
    """
    client = await redis_service.get_connection()
    pubsub = client.pubsub()
    
    try:
        await pubsub.subscribe(channel_name)
        logger.info(f"Subscribed to Redis channel: {channel_name}")
        
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = message.get('data')
                if data and isinstance(data, str):
                    await websocket_manager.broadcast(channel_name, data)
    except asyncio.CancelledError:
        logger.info(f"Redis subscription for {channel_name} cancelled")
    except Exception as e:
        logger.error(f"Redis subscription error: {str(e)}")
    finally:
        await pubsub.unsubscribe(channel_name)
        # Don't close the Redis connection as it comes from pool


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for task status updates.
    
    Args:
        websocket: The WebSocket connection
        task_id: The task ID to subscribe to
    """
    # Use a consistent channel prefix from settings
    channel_prefix = getattr(settings, "redis_channel_prefix", "product_analysis")
    channel_name = f"{channel_prefix}_{task_id}"
    
    await websocket_manager.connect(websocket, channel_name)
    
    try:
        # Start Redis subscription if this is the first client for this channel
        if channel_name not in redis_service.active_subscriptions:
            subscription_task = asyncio.create_task(redis_subscriber(channel_name))
            redis_service.add_subscription(channel_name, subscription_task)
        
        # Confirm subscription to client
        await websocket.send_json({"event": "subscribed", "channel": channel_name})
        
        # Keep connection open and handle client messages
        while True:
            # Wait for client messages (primarily disconnect)
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle unsubscribe message
                if message.get("action") == "unsubscribe":
                    break
            except json.JSONDecodeError:
                logger.error("Received invalid JSON from client")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from {channel_name}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        # Clean up
        websocket_manager.disconnect(websocket, channel_name)
        
        # If no more clients for this channel, cancel the subscription task
        if not websocket_manager.has_connections(channel_name):
            redis_service.remove_subscription(channel_name)
