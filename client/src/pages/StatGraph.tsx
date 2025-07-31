import React from 'react';

const StatGraph: React.FC = () => {
  // Dummy data or props can be passed here
  return (
    <div className="bg-blue-100 p-4 rounded shadow mb-6">
      <p className="text-blue-800 font-medium">Inbox: 60%</p>
      <p className="text-yellow-800 font-medium">Spam: 30%</p>
      <p className="text-gray-700 font-medium">Not Found: 10%</p>
    </div>
  );
};

export default StatGraph;
