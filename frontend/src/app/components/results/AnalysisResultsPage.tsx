'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AnalysisResultsDisplay from '../product/AnalysisResultsDisplay';
import Card, { CardHeader, CardTitle, CardContent } from '../ui/Card';
import Button from '../ui/Button';
import { getTaskStatus, TaskStatusResponse } from '../../services/api';

const AnalysisResultsPage: React.FC = () => {
  const router = useRouter();
  const [taskId, setTaskId] = useState<string | null>(null);
  
  // Parse query parameters manually for static export compatibility
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const taskIdParam = urlParams.get('taskId');
      setTaskId(taskIdParam);
    }
  }, []);
  
  const [taskStatus, setTaskStatus] = useState<TaskStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) {
      setError('No task ID provided');
      setLoading(false);
      return;
    }

    const fetchTaskStatus = async () => {
      try {
        setLoading(true);
        const status = await getTaskStatus(taskId);
        
        if (status.status !== 'success' || !status.result?.report) {
          setError('Analysis not completed or no results available');
        } else {
          setTaskStatus(status);
        }
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch analysis results');
        console.error('Error fetching analysis results:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTaskStatus();
  }, [taskId]);

  const handleNewAnalysis = () => {
    router.push('/');
  };

  const handleBackToStatus = () => {
    if (taskId) {
      router.push(`/?taskId=${taskId}`);
    } else {
      router.push('/');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="w-full max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Loading Analysis Results...</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="w-full max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="text-red-600">Error Loading Results</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">{error}</p>
            <div className="space-x-2">
              <Button onClick={handleNewAnalysis}>Start New Analysis</Button>
              {taskId && (
                <Button onClick={handleBackToStatus} variant="secondary">
                  Back to Task Status
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!taskStatus?.result?.report) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="w-full max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>No Results Available</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">No analysis results found for this task.</p>
            <Button onClick={handleNewAnalysis}>Start New Analysis</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <AnalysisResultsDisplay
        report={taskStatus.result.report}
        taskId={taskId || ''}
        onNewAnalysis={handleNewAnalysis}
      />
    </div>
  );
};

export default AnalysisResultsPage;
