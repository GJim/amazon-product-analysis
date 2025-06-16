import React, { useState } from 'react';
import Input from '../ui/Input';
import Button from '../ui/Button';
import Card, { CardHeader, CardTitle, CardContent, CardFooter } from '../ui/Card';
import { createAnalysisTask } from '../../services/api';

interface ProductAnalysisFormProps {
  onTaskCreated: (taskId: string) => void;
}

const ProductAnalysisForm: React.FC<ProductAnalysisFormProps> = ({ onTaskCreated }) => {
  const [url, setUrl] = useState('');
  const [maxProducts, setMaxProducts] = useState(10);
  const [maxCompetitive, setMaxCompetitive] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!url) {
      setError('Please enter an Amazon product URL');
      return;
    }
    
    // Clear previous errors
    setError(null);
    setIsLoading(true);
    
    try {
      const response = await createAnalysisTask({
        url,
        max_products: maxProducts,
        max_competitive: maxCompetitive
      });
      
      onTaskCreated(response.task_id);
    } catch (err: any) {
      setError(err.message || 'Failed to create analysis task');
      console.error('Error creating task:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Analyze Amazon Product</CardTitle>
      </CardHeader>
      
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <Input
            label="Amazon Product URL"
            placeholder="https://www.amazon.com/dp/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            type="url"
            disabled={isLoading}
            error={error || undefined}
            helperText="Enter the full URL to an Amazon product page"
          />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Max Products"
              type="number"
              min={1}
              max={50}
              value={maxProducts}
              onChange={(e) => setMaxProducts(parseInt(e.target.value))}
              disabled={isLoading}
              helperText="Maximum number of products to collect (1-50)"
            />
            
            <Input
              label="Max Competitive Products"
              type="number"
              min={1}
              max={20}
              value={maxCompetitive}
              onChange={(e) => setMaxCompetitive(parseInt(e.target.value))}
              disabled={isLoading}
              helperText="Maximum competitive products to analyze (1-20)"
            />
          </div>
        </CardContent>
        
        <CardFooter>
          <Button 
            type="submit" 
            isLoading={isLoading} 
            disabled={isLoading}
            className="w-full"
          >
            Start Analysis
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default ProductAnalysisForm;
