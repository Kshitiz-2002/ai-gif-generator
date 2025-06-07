import React from 'react';

export function Card({ children, className = '' }) {
  return (
    <div
      className={
        `bg-white/70 backdrop-blur-lg rounded-2xl shadow-xl p-6 ${className}`
      }
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '' }) {
  return (
    <div className={`mb-4 text-center ${className}`}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '' }) {
  return (
    <h1 className={`text-4xl font-extrabold ${className}`}>
      {children}
    </h1>
  );
}

export function CardContent({ children, className = '' }) {
  return (
    <div className={`p-4 ${className}`}>
      {children}
    </div>
  );
}
