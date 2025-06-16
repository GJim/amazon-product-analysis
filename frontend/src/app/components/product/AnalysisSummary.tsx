import React from 'react';
import Card, { CardHeader, CardTitle, CardContent } from '../ui/Card';

interface AnalysisSummaryProps {
  mainProductTitle: string;
  competitiveProductsCount: number;
  hasMarketAnalysis: boolean;
  hasOptimizationSuggestions: boolean;
  taskId: string;
}

const AnalysisSummary: React.FC<AnalysisSummaryProps> = ({
  mainProductTitle,
  competitiveProductsCount,
  hasMarketAnalysis,
  hasOptimizationSuggestions,
  taskId,
}) => {
  return (
    <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-700">
      <CardHeader>
        <CardTitle className="text-lg text-blue-800 dark:text-blue-300">
          Analysis Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="mb-2">
              <span className="font-medium text-gray-900 dark:text-gray-100">Product:</span>
              <span className="text-gray-700 dark:text-gray-300 ml-2 line-clamp-2">
                {mainProductTitle}
              </span>
            </p>
            <p className="mb-2">
              <span className="font-medium text-gray-900 dark:text-gray-100">Task ID:</span>
              <span className="text-gray-600 dark:text-gray-400 ml-2 font-mono text-xs">
                {taskId.slice(0, 8)}...
              </span>
            </p>
          </div>
          <div>
            <p className="mb-2">
              <span className="font-medium text-gray-900 dark:text-gray-100">Competitive Products:</span>
              <span className="text-gray-700 dark:text-gray-300 ml-2">
                {competitiveProductsCount} found
              </span>
            </p>
            <div className="flex space-x-4 text-xs">
              <span className={`px-2 py-1 rounded-full ${
                hasMarketAnalysis 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }`}>
                Market Analysis {hasMarketAnalysis ? '✓' : '✗'}
              </span>
              <span className={`px-2 py-1 rounded-full ${
                hasOptimizationSuggestions 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }`}>
                Optimization {hasOptimizationSuggestions ? '✓' : '✗'}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AnalysisSummary;
