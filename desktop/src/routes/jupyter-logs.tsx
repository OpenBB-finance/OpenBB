import { createFileRoute } from '@tanstack/react-router';
import { useEffect } from 'react';
import JupyterLogsPage from "../components/JupyterLogsPage";

// Define a wrapper component to handle class cleanup properly
const JupyterLogsWrapper = () => {
  useEffect(() => {
    // Add class when component mounts
    document.body.classList.add('jupyter-logs-view');
    
    // Return cleanup function for when component unmounts
    return () => {
      document.body.classList.remove('jupyter-logs-view');
      // Do NOT clear localStorage shutdown events so that main window can still detect them
    };
  }, []);
  
  return <JupyterLogsPage />;
};

// Define the route
export const Route = createFileRoute('/jupyter-logs')({
  component: JupyterLogsWrapper,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      environment: search.env as string || null
    };
  }
});

export default Route;