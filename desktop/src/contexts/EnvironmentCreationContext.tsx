import { createContext, useContext, useState } from 'react';
import type { ReactNode, FC } from 'react';

interface EnvironmentCreationContextType {
  isCreatingEnvironment: boolean;
  setIsCreatingEnvironment: (isCreating: boolean) => void;
}

const EnvironmentCreationContext = createContext<EnvironmentCreationContextType | undefined>(undefined);

export const useEnvironmentCreation = () => {
  const context = useContext(EnvironmentCreationContext);
  if (context === undefined) {
    throw new Error('useEnvironmentCreation must be used within an EnvironmentCreationProvider');
  }
  return context;
};

interface EnvironmentCreationProviderProps {
  children: ReactNode;
}

export const EnvironmentCreationProvider: FC<EnvironmentCreationProviderProps> = ({ children }) => {
  const [isCreatingEnvironment, setIsCreatingEnvironment] = useState(false);

  return (
    <EnvironmentCreationContext.Provider value={{ isCreatingEnvironment, setIsCreatingEnvironment }}>
      {children}
    </EnvironmentCreationContext.Provider>
  );
}; 