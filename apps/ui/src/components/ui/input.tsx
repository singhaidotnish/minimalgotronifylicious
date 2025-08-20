'use client';
import * as React from 'react';

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', ...props }, ref) => (
    <input
      ref={ref}
      className={[
        'block w-full rounded-md border border-gray-300 bg-white',
        'px-3 py-2 text-sm leading-5',
        'placeholder:text-gray-400',
        'focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500',
        'disabled:cursor-not-allowed disabled:opacity-50',
        className,
      ].join(' ')}
      {...props}
    />
  )
);
Input.displayName = 'Input';

export { Input };
export default Input;
