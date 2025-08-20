import React from 'react';

const TemplateBuilder: React.FC = () => {
  // Mocked point-and-extract functionality
  const handleElementClick = (e: React.MouseEvent<HTMLDivElement>) => {
    e.stopPropagation();
    const target = e.target as HTMLElement;
    alert(`Selected element: <${target.tagName.toLowerCase()}>`);
    // TODO: Implement logic to get CSS selector or XPath
  };

  return (
    <div>
      <h1>Template Builder (Point-and-Extract Mock)</h1>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Note: This builder currently works with the latest template version. Full historical versioning and retrieval via `/templates/{id}/versions/{ver}` is a future enhancement.
      </p>
      <div style={{ border: '1px solid black', padding: '1rem', marginTop: '1rem' }}>
        <h3>Mock Website Content</h3>
        <div onClick={handleElementClick}>
          <h2 style={{ color: 'blue' }}>Product Title</h2>
          <p>This is a product description.</p>
          <span style={{ fontWeight: 'bold' }}>$99.99</span>
        </div>
      </div>
    </div>
  );
};

export default TemplateBuilder;