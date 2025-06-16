import React, { useState, useEffect } from 'react';
import Card, { CardHeader, CardTitle, CardContent } from '../ui/Card';
import Button from '../ui/Button';
import useWebSocket from '../../hooks/useWebSocket';
import { getTaskStatus, TaskStatusResponse } from '../../services/api';

interface TaskStatusDisplayProps {
  taskId: string;
  onReset: () => void;
}

const TaskStatusDisplay: React.FC<TaskStatusDisplayProps> = ({ taskId, onReset }) => {
  const [taskStatus, setTaskStatus] = useState<TaskStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Connect to WebSocket for real-time updates
  const { lastMessage, isConnected } = useWebSocket(taskId, {
    onOpen: () => console.log('WebSocket connected for task:', taskId),
  });
  
  // Fetch initial task status
  useEffect(() => {
    const fetchTaskStatus = async () => {
      try {
        setLoading(true);
        const status = await getTaskStatus(taskId);
        setTaskStatus(status);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch task status');
        console.error('Error fetching task status:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchTaskStatus();
  }, [taskId]);
  
  // Update when receiving WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      console.log('WebSocket message received:', lastMessage);
      // Update the task status based on the WebSocket message
      if (lastMessage.status) {
        setTaskStatus(prevStatus => ({
          ...(prevStatus || {}),
          status: lastMessage.status,
          result: lastMessage.result || prevStatus?.result,
          task_id: taskId
        }));
      }
    }
  }, [lastMessage, taskId]);
  
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
  
  if (loading && !taskStatus) {
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
          <div className="py-4 text-center">
            <p className="mb-4">Your analysis is in progress.</p>
            <div className="flex justify-center items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mr-2"></div>
              <span>Processing...</span>
            </div>
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
            <p className="text-green-600 mb-4">Analysis completed successfully!</p>
            
            {taskStatus.result && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Results</h3>
                {formatJson(taskStatus.result)}
              </div>
            )}
            
            <div className="mt-6">
              <Button onClick={onReset} variant="secondary">New Analysis</Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TaskStatusDisplay;
