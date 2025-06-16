"""
WebSocket connection manager for handling client connections.
"""
import logging
from typing import Dict, List

from fastapi import WebSocket

# Configure logging
logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manager for WebSocket connections."""
    
    def __init__(self):
        """Initialize the connection manager with empty containers."""
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        """
        Accept the WebSocket connection and add it to the active connections.
        
        Args:
            websocket: The WebSocket connection to add
            channel: The channel name for the connection
        """
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"WebSocket client connected to channel: {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """
        Remove a WebSocket connection from active connections.
        
        Args:
            websocket: The WebSocket connection to remove
            channel: The channel name for the connection
        """
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
                logger.info(f"WebSocket client disconnected from channel: {channel}")
            if not self.active_connections[channel]:
                del self.active_connections[channel]
                logger.info(f"Channel {channel} has no more active connections")
    
    def has_connections(self, channel: str) -> bool:
        """
        Check if a channel has active connections.
        
        Args:
            channel: The channel name to check
            
        Returns:
            bool: True if the channel has connections, False otherwise
        """
        return channel in self.active_connections and len(self.active_connections[channel]) > 0
    
    async def broadcast(self, channel: str, message: str):
        """
        Send a message to all connected clients for a specific channel.
        
        Args:
            channel: The channel to broadcast to
            message: The message to send
        """
        if channel not in self.active_connections:
            return
            
        dead_connections = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead, channel)


# Create a global instance of the WebSocket manager
websocket_manager = WebSocketManager()
