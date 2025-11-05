import { ClassValue, clsx } from 'clsx';

/**
 * A utility for conditionally joining CSS class names together
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}