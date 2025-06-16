"use client";

import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import ProductAnalysisContainer from './components/product/ProductAnalysisContainer';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Amazon Product Analysis Tool
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Analyze Amazon products and get valuable insights using our advanced WebSocket-powered analysis system
          </p>
        </div>
        
        <ProductAnalysisContainer />
      </main>
      
      <Footer />
    </div>
  );
}
