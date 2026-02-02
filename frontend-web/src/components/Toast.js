import React, { useEffect } from 'react';
import './Toast.css';

function Toast({ message, type }) {
  useEffect(() => {
    const timer = setTimeout(() => {}, 4000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`toast toast-${type}`}>
      <span className="toast-icon">
        {type === 'success' && '✅'}
        {type === 'error' && '❌'}
        {type === 'info' && 'ℹ️'}
      </span>
      <span className="toast-message">{message}</span>
    </div>
  );
}

export default Toast;
