import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Card, { CardHeader, CardTitle, CardContent } from '../ui/Card';
import Button from '../ui/Button';
import useWebSocket from 'react-use-websocket';
import { getTaskStatus, TaskStatusResponse } from '../../services/api';

// Message structure that comes from WebSocket
interface AgentMessage {
  agent: string;
  message: string;
  timestamp: string;
}

interface TaskStatusDisplayProps {
  taskId: string;
  onReset: () => void;
}

const TaskStatusDisplay: React.FC<TaskStatusDisplayProps> = ({ taskId, onReset }) => {
  const [taskStatus, setTaskStatus] = useState<TaskStatusResponse | null>(null);
  // const [loading, _setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastAgentMessage, setLastAgentMessage] = useState<AgentMessage | null>(null);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  
  // WebSocket URL construction
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = window.location.host;
  const wsUrl = `${wsProtocol}//${wsHost}/ws/${taskId}`;
  
  // Connect to WebSocket for real-time updates using react-use-websocket
  const { lastMessage, readyState } = useWebSocket(wsUrl, {
    onOpen: () => console.log('WebSocket connected for task:', taskId),
    onError: (event) => {
      setError('WebSocket error: ' + event);
      console.error('WebSocket error:', event)
    },
    onClose: () => console.log('WebSocket closed for task:', taskId),
    shouldReconnect: () => true, // Attempt to reconnect on all close events
    reconnectAttempts: 5,
    reconnectInterval: 3000,
  });
  
  // Determine connection status from readyState
  const isConnected = readyState === 1; // WebSocket.OPEN
  
  // Update when receiving WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        // Parse the message data as JSON (react-use-websocket doesn't auto-parse)
        const messageData = JSON.parse(lastMessage.data);
        console.log('WebSocket message received:', messageData);
        
        // Handle agent messages
        if (messageData.agent) {
          // Store the message as last agent message
          setLastAgentMessage(messageData as AgentMessage);
          
          // Set current agent
          setCurrentAgent(messageData.agent);
          
          // When we receive a message from any agent, change status to running
          setTaskStatus(prevStatus => ({
            ...(prevStatus || {}),
            status: 'running',
            task_id: taskId,
            result: prevStatus?.result || null
          }));
          
          // If message is from SupervisorAgent, check task status
          if (messageData.agent === 'SupervisorAgent') {
            checkTaskStatus();
          }
        }
        // Also handle traditional status updates
        else if (messageData.status) {
          setTaskStatus(prevStatus => ({
            ...(prevStatus || {}),
            status: messageData.status,
            result: messageData.result || prevStatus?.result,
            task_id: taskId
          }));
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    }
  }, [lastMessage, taskId]);
  
  // Function to check task status from the API
  const checkTaskStatus = async () => {
    try {
      const status = await getTaskStatus(taskId);
      
      // If status is finished (success or error), update with the final status
      if (status.status === 'success' || status.status === 'error') {
        setTaskStatus(status);
      }
    } catch (err) {
      console.error('Error checking task status:', err);
    }
  };
  
  // Status indicator with appropriate color
  const getStatusBadge = (status: string) => {
    const baseClasses = "inline-block px-2 py-1 text-xs font-medium rounded-full";
    
    switch (status) {
      case 'pending':
        return <span className={`${baseClasses} bg-yellow-100 text-yellow-800`}>Pending</span>;
      case 'running':
        return <span className={`${baseClasses} bg-blue-100 text-blue-800`}>Running</span>;
      case 'success':
        return <span className={`${baseClasses} bg-green-100 text-green-800`}>Success</span>;
      case 'error':
        return <span className={`${baseClasses} bg-red-100 text-red-800`}>Error</span>;
      default:
        return <span className={`${baseClasses} bg-gray-100 text-gray-800`}>{status}</span>;
    }
  };
  
  // Format JSON for display
  const formatJson = (json: any) => {
    return (
      <pre className="bg-gray-50 dark:bg-gray-900 p-4 rounded-md overflow-auto text-sm">
        {JSON.stringify(json, null, 2)}
      </pre>
    );
  };
  
  const router = useRouter();
  
  if (!taskStatus) {
    return (
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Loading task status...</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-red-600">Error Loading Task</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4">{error}</p>
          <Button onClick={onReset}>Start New Analysis</Button>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Task {taskId.slice(0, 8)}...</span>
          {taskStatus && getStatusBadge(taskStatus.status)}
        </CardTitle>
        <div className="text-xs text-gray-500 mt-1 flex items-center space-x-2">
          <span>WebSocket: {isConnected ? 
            <span className="text-green-500">Connected</span> : 
            <span className="text-red-500">Disconnected</span>}
          </span>
        </div>
        
        {/* Current Agent Display */}
        {currentAgent && (
          <div className="mt-2 bg-blue-50 dark:bg-blue-900/20 p-2 rounded-md border border-blue-200 dark:border-blue-700">
            <div className="font-medium text-sm text-blue-800 dark:text-blue-300">
              Current Agent: <span className="font-bold">{currentAgent}</span>
            </div>
          </div>
        )}
      </CardHeader>
      
      <CardContent>
        {taskStatus?.status === 'pending' && (
          <div className="py-4 text-center">
            <p className="mb-4">Your analysis task is in the queue and will start soon.</p>
            <div className="flex justify-center items-center">
              <div className="animate-pulse rounded-full h-4 w-4 bg-yellow-500 mr-2"></div>
              <span>Waiting to start...</span>
            </div>
          </div>
        )}
        
        {taskStatus?.status === 'running' && (
          <div className="py-4">
            <p className="mb-4 text-center">Your analysis is in progress.</p>
            <div className="flex justify-center items-center mb-4">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mr-2"></div>
              <span>Processing...</span>
            </div>
            
            {/* Last Agent Message Display */}
            {lastAgentMessage && (
              <div className="mt-4 bg-gray-50 dark:bg-gray-800/50 p-3 rounded-md border border-gray-200 dark:border-gray-700">
                <div className="text-xs text-gray-500 mb-1">
                  {new Date(lastAgentMessage.timestamp).toLocaleString()}
                </div>
                <p className="text-sm whitespace-pre-wrap">{lastAgentMessage.message}</p>
              </div>
            )}
          </div>
        )}
        
        {taskStatus?.status === 'error' && (
          <div className="py-4">
            <p className="text-red-600 mb-2">An error occurred during analysis:</p>
            {taskStatus.result && formatJson(taskStatus.result)}
            <div className="mt-4">
              <Button onClick={onReset} variant="secondary">Start New Analysis</Button>
            </div>
          </div>
        )}
        
        {taskStatus?.status === 'success' && (
          <div className="py-2">
            {/* <p className="text-green-600 mb-4">Analysis completed successfully!</p>
            
            {taskStatus.result && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Results</h3>
                {formatJson(taskStatus.result)}
              </div>
            )} */}
            
            {lastAgentMessage && (
              <div className="mt-4 bg-gray-50 dark:bg-gray-800/50 p-3 rounded-md border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium">Final Report</h3>
                <div className="text-xs text-gray-500 mb-1">
                  {new Date(lastAgentMessage.timestamp).toLocaleString()}
                </div>
                <p className="text-sm whitespace-pre-wrap">{lastAgentMessage.message}</p>
              </div>
            )}
            
            <div className="mt-6 space-y-2">
              <Button 
                onClick={() => router.push(`/results?taskId=${taskId}`)}
                className="w-full"
              >
                View More Detailed
              </Button>
              <Button onClick={onReset} variant="secondary" className="w-full">
                New Analysis
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TaskStatusDisplay;
