import React, { useState } from 'react';
import ProductAnalysisForm from './ProductAnalysisForm';
import TaskStatusDisplay from './TaskStatusDisplay';

/**
 * Main container component that manages the product analysis workflow
 * Controls the state between submitting a new analysis and viewing results
 */
const ProductAnalysisContainer: React.FC = () => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  
  // Handle when a new task is created
  const handleTaskCreated = (taskId: string) => {
    setActiveTaskId(taskId);
  };
  
  // Reset the workflow to create a new task
  const handleReset = () => {
    setActiveTaskId(null);
  };
  
  return (
    <div className="w-full max-w-4xl mx-auto">
      {!activeTaskId ? (
        <ProductAnalysisForm onTaskCreated={handleTaskCreated} />
      ) : (
        <TaskStatusDisplay taskId={activeTaskId} onReset={handleReset} />
      )}
    </div>
  );
};

export default ProductAnalysisContainer;
