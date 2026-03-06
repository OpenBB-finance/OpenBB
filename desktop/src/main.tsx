import ReactDOM from 'react-dom/client';
import './styles.css';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { StrictMode } from 'react';

const FORWARD_REF_WARNING = 'forwardRef render functions accept exactly two parameters';

const shouldSuppressKnownConsoleNoise = (args: unknown[]): boolean =>
  args.some((arg) => typeof arg === 'string' && arg.includes(FORWARD_REF_WARNING));

const patchConsoleMethod = (
  originalMethod: (...args: unknown[]) => void,
) => (...args: unknown[]) => {
  if (shouldSuppressKnownConsoleNoise(args)) {
    return;
  }
  originalMethod.apply(console, args);
};

console.error = patchConsoleMethod(console.error.bind(console));
console.warn = patchConsoleMethod(console.warn.bind(console));

const createAppRouter = async () => {
  const { routeTree } = await import('./routeTree.gen');
  return createRouter({ routeTree });
};

type AppRouter = Awaited<ReturnType<typeof createAppRouter>>;

declare module '@tanstack/react-router' {
  interface Register {
    router: AppRouter
  }
}

const bootstrap = async () => {
  const rootElement = document.getElementById('app')!;
  if (rootElement.innerHTML) {
    return;
  }

  const router = await createAppRouter();
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  );
};

void bootstrap();
