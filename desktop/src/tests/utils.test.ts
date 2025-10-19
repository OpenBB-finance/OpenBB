import { expect, test } from 'vitest';
import { cn } from '../utils';

test('cn joins class names correctly', () => {
  expect(cn('class1', 'class2')).toBe('class1 class2');
});

test('cn handles conditional class names', () => {
  expect(cn('class1', 'class2', undefined)).toBe('class1 class2');
});

test('cn handles arrays of class names', () => {
  expect(cn(['class1', 'class2'], 'class3')).toBe('class1 class2 class3');
});

test('cn handles mixed inputs', () => {
  expect(cn('class1', { class2: true, class3: false }, ['class4', 'class5'])).toBe('class1 class2 class4 class5');
});

test('cn handles empty inputs', () => {
  expect(cn()).toBe('');
});

test('cn handles null and undefined inputs', () => {
  expect(cn(null, 'class1', undefined, 'class2')).toBe('class1 class2');
});
