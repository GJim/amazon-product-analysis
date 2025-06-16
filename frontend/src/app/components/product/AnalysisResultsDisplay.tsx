import React from 'react';
import Card, { CardHeader, CardTitle, CardContent } from '../ui/Card';
import Button from '../ui/Button';
import AnalysisSummary from './AnalysisSummary';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Type definitions based on the backend report structure
interface Product {
  title: string;
  price: string;
  description?: string;
  main_image_url?: string;
}

interface AnalysisReport {
  main_product: Product;
  competitive_products: Product[];
  market_analysis: string;
  optimization_suggestions: string;
}

interface AnalysisResultsDisplayProps {
  report: AnalysisReport;
  taskId: string;
  onNewAnalysis: () => void;
}

const AnalysisResultsDisplay: React.FC<AnalysisResultsDisplayProps> = ({
  report,
  taskId,
  onNewAnalysis,
}) => {
  const formatPrice = (price: string) => {
    if (!price) return 'Price not available';
    return price.startsWith('$') ? price : `$${price}`;
  };

  const renderTextSection = (text: string | undefined, title: string) => {
    if (!text) return null;
    
    return (
      <div className="mb-4">
        <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">{title}</h4>
        <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed markdown-content">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]} 
            components={{
              table: ({ ...props }) => (
                <table className="min-w-full divide-y divide-gray-200 shadow-md rounded-lg overflow-hidden" {...props} />
              ),
              thead: ({ ...props }) => (
                <thead className="bg-gray-50" {...props} />
              ),
              th: ({ ...props }) => (
                <th
                  className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  {...props}
                />
              ),
              tbody: ({ ...props }) => (
                <tbody className="bg-white divide-y divide-gray-200" {...props} />
              ),
              tr: ({ ...props }) => (
                <tr className="hover:bg-gray-100 transition-colors duration-200" {...props} />
              ),
              td: ({ ...props }) => (
                <td className="px-2 py-1 whitespace-normal text-xs text-gray-900" {...props} />
              ),
            }}
          >
            {text}
          </ReactMarkdown>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl">Analysis Results</CardTitle>
            <Button onClick={onNewAnalysis} variant="secondary">
              New Analysis
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Summary */}
      <AnalysisSummary
        mainProductTitle={report.main_product.title}
        competitiveProductsCount={report.competitive_products?.length || 0}
        hasMarketAnalysis={!!report.market_analysis}
        hasOptimizationSuggestions={!!report.optimization_suggestions}
        taskId={taskId}
      />

      {/* Main Product Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl text-blue-600 dark:text-blue-400">
            Main Product
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              {report.main_product.main_image_url && (
                <div>
                  <img src={report.main_product.main_image_url} alt={report.main_product.title} className="w-full h-auto" />
                </div>
              )}
              <h3 className="font-semibold text-lg mb-2">{report.main_product.title}</h3>
              <div className="space-y-2 text-sm">
                <p><span className="font-medium">Price:</span> {formatPrice(report.main_product.price)}</p>
              </div>
            </div>
            {report.main_product.description && (
              <div>
                <h4 className="font-medium mb-2">Description</h4>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  {report.main_product.description}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Competitive Products Section */}
      {report.competitive_products && report.competitive_products.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-green-600 dark:text-green-400">
              Competitive Products ({report.competitive_products.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {report.competitive_products.map((product, index) => (
                <div key={index} className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                  {product.main_image_url && (
                    <div>
                      <img src={product.main_image_url} alt={product.title} className="w-full h-auto" />
                    </div>
                  )}
                  <h4 className="font-medium text-sm mb-2 line-clamp-2">{product.title}</h4>
                  <div className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                    <p><span className="font-medium">Price:</span> {formatPrice(product.price)}</p>
                  </div>
                  {product.description && (
                    <p className="text-xs text-gray-700 dark:text-gray-300 mt-2 line-clamp-3">
                      {product.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Market Analysis Section */}
      {report.market_analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-purple-600 dark:text-purple-400">
              Market Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                {renderTextSection(report.market_analysis, "Market Positioning")}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Optimization Suggestions Section */}
      {report.optimization_suggestions && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-orange-600 dark:text-orange-400">
              Optimization Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                {renderTextSection(report.optimization_suggestions, "Optimization Suggestions")}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AnalysisResultsDisplay;
