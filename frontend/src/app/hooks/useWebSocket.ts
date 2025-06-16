import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketHookOptions {
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (event: Event) => void;
  reconnectInterval?: number;
  reconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  lastMessage: any;
  sendMessage: (data: any) => void;
  disconnect: () => void;
}

/**
 * Custom hook to handle WebSocket connections
 */
const useWebSocket = (
  taskId: string | null,
  options: WebSocketHookOptions = {}
): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const webSocketRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  const {
    onOpen,
    onClose,
    onError,
    reconnectInterval = 3000,
    reconnectAttempts = 5
  } = options;

  // Create WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (!taskId) return;
    
    // Get host dynamically to work in both development and production
    // const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // const host = window.location.host;
    // const wsUrl = `${protocol}//${host}/ws/${taskId}`;
    const wsUrl = `/ws/${taskId}`;
    
    try {
      setIsConnecting(true);
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = (event) => {
        console.log('WebSocket connected:', wsUrl);
        setIsConnected(true);
        setIsConnecting(false);
        reconnectCountRef.current = 0;
        onOpen?.(event);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      ws.onclose = (event) => {
        console.log('WebSocket connection closed');
        setIsConnected(false);
        onClose?.(event);
        
        // Attempt to reconnect if not closed intentionally
        if (!event.wasClean && reconnectCountRef.current < reconnectAttempts) {
          reconnectTimerRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect (${reconnectCountRef.current + 1}/${reconnectAttempts})...`);
            reconnectCountRef.current += 1;
            connectWebSocket();
          }, reconnectInterval);
        }
      };
      
      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        onError?.(event);
      };
      
      webSocketRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setIsConnecting(false);
    }
  }, [taskId, onOpen, onClose, onError, reconnectInterval, reconnectAttempts]);
  
  // Send message through WebSocket
  const sendMessage = useCallback((data: any) => {
    if (webSocketRef.current && isConnected) {
      webSocketRef.current.send(JSON.stringify(data));
    } else {
      console.warn('Cannot send message: WebSocket is not connected');
    }
  }, [isConnected]);
  
  // Close WebSocket connection
  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    
    if (webSocketRef.current) {
      webSocketRef.current.close();
      webSocketRef.current = null;
    }
    
    setIsConnected(false);
    setIsConnecting(false);
  }, []);
  
  // Initialize WebSocket connection when taskId changes
  useEffect(() => {
    if (taskId) {
      connectWebSocket();
    } else {
      console.log('WebSocket connection closed: Reason: taskId is null');
      disconnect();
    }
    
    // Clean up on unmount or taskId change
    return () => {
      if (webSocketRef.current?.readyState === WebSocket.OPEN) {
        console.log('WebSocket connection closed: Reason: taskId changed');
        disconnect();
      }
    };
  }, [taskId, connectWebSocket, disconnect]);
  
  return {
    isConnected,
    isConnecting,
    lastMessage,
    sendMessage,
    disconnect
  };
};

export default useWebSocket;
