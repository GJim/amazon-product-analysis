import React from 'react';

const SimpleComponent: React.FC = () => {
  return (
    <div className="bg-blue-500 text-white p-4 rounded-md">
      <h1 className="text-xl font-bold">Hello from SimpleComponent!</h1>
      <p>This component is styled with Tailwind CSS.</p>
    </div>
  );
};

export default SimpleComponent;
