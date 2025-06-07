import React from 'react';

export function Label({ children, htmlFor, className = '' }) {
  return (
    <label
      htmlFor={htmlFor}
      className={`block text-gray-700 font-medium mb-1 ${className}`}
    >
      {children}
    </label>
  );
}
