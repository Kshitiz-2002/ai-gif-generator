import React from 'react';

export function Input({ className = '', ...props }) {
  return (
    <input
      className={
        `w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring focus:ring-blue-200 ${className}`
      }
      {...props}
    />
  );
}
 