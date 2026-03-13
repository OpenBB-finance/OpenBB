import ReactDOM from 'react-dom/client';
import './styles.css';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { StrictMode } from 'react';

// Suppress known forwardRef warning from Radix UI in @openbb/ui-pro
// This is a harmless warning from older Radix UI versions
const originalError = console.error;
console.error = (...args) => {
  if (typeof args[0] === 'string' && args[0].includes('forwardRef render functions accept exactly two parameters')) {
    return;
  }
  originalError.apply(console, args);
};

// Import the generated route tree
import { routeTree } from './routeTree.gen'

// Create a new router instance
const router = createRouter({ routeTree })

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

// Render the app
const rootElement = document.getElementById('app')!
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  )
}
