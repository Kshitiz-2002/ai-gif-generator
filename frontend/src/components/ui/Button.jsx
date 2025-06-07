import React from 'react';

export function Button({ children, className = '', ...props }) {
  return (
    <button
      className={
        `inline-flex items-center justify-center rounded-md px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 transition ${className}`
      }
      {...props}
    >
      {children}
    </button>
  );
}
