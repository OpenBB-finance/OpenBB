import { createFileRoute } from '@tanstack/react-router';
import { useEffect } from 'react';
import BackendLogsPage from "../components/BackendLogsPage";

// Define a wrapper component to handle class cleanup properly
const BackendLogsWrapper = () => {
  useEffect(() => {
    // Add class when component mounts
    document.body.classList.add('jupyter-logs-view');
    // Return cleanup function for when component unmounts
    return () => {
      document.body.classList.remove('jupyter-logs-view');
    };
  }, []);
  return <BackendLogsPage />;
};

export const Route = createFileRoute('/backend-logs')({
  component: BackendLogsWrapper,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      id: search.id as string
    };
  }
});

export default Route;