import React, { useId} from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: string;
}

const Input: React.FC<InputProps> = ({
  className = '',
  label,
  helperText,
  error,
  id,
  ...props
}) => {
  const reactId = useId();
  const inputId = id || reactId;

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          {label}
        </label>
      )}
      <div className="relative">
        <input
          id={inputId}
          className={`
            w-full rounded-md border border-gray-300 dark:border-gray-600
            bg-white dark:bg-gray-800 px-3 py-2 text-sm
            placeholder-gray-400 dark:placeholder-gray-500
            shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500
            dark:focus:ring-blue-600 dark:text-white
            disabled:opacity-50 ${error ? 'border-red-500 focus:ring-red-500' : ''}
            ${className}
          `}
          {...props}
        />
      </div>
      {helperText && !error && (
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {helperText}
        </p>
      )}
      {error && (
        <p className="mt-1 text-xs text-red-500">
          {error}
        </p>
      )}
    </div>
  );
};

export default Input;
