import React, { useState, useRef, useEffect } from 'react';
import { Button, Tooltip } from '@openbb/ui-pro';
import CustomIcon from './Icon';
import { GamestonkIcon } from './GamestonkIcon';

interface EnvironmentActionsProps {
  env: {
    name: string;
  };
  isUpdatingEnvironment: boolean;
  installDir: string | null;
  hasCliSupport: (name: string) => boolean;
  hasIPythonSupport: (name: string) => boolean;
  hasJupyterSupport: (name: string) => boolean;
  jupyterStatus: string;
  openSystemTerminal: (name: string) => void;
  startCliSession: (name: string) => void;
  startPythonSession: (name: string) => void;
  startIPythonSession: (name: string) => void;
  startJupyterLab: (name: string) => void;
  openJupyterWindow: (url: string) => void;
  jupyterUrl: string | null;
}

export const EnvironmentActions: React.FC<EnvironmentActionsProps> = ({
  env,
  isUpdatingEnvironment,
  installDir,
  hasCliSupport,
  hasIPythonSupport,
  hasJupyterSupport,
  jupyterStatus,
  openSystemTerminal,
  startCliSession,
  startPythonSession,
  startIPythonSession,
  startJupyterLab,
  openJupyterWindow,
  jupyterUrl,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);

  const toggleModal = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsModalOpen((prev) => !prev);
  };

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsModalOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const applications = [
    {
      name: 'Jupyter',
      description: 'Start a Jupyter Lab session.',
      icon: <CustomIcon id="jupyter-logo" className="w-8 h-8" />,
      action: () => {
        if (jupyterStatus === 'running') {
          if (jupyterUrl) openJupyterWindow(jupyterUrl);
        } else {
          startJupyterLab(env.name);
        }
      },
      disabled: !hasJupyterSupport(env.name) || jupyterStatus === 'starting' || jupyterStatus === 'stopping' || isUpdatingEnvironment,
      condition: hasJupyterSupport(env.name),
      status: jupyterStatus,
    },
    {
      name: 'Python',
      description: 'Start a Python session.',
      icon: <CustomIcon id="python" className="w-8 h-8" />,
      action: () => startPythonSession(env.name),
      disabled: !env.name || !installDir || isUpdatingEnvironment,
      condition: true,
    },
    {
      name: 'IPython',
      description: 'Start an interactive IPython session.',
      icon: <CustomIcon id="ipy" className="w-9 h-9 -py-2 -mr-1" />,
      action: () => startIPythonSession(env.name),
      disabled: !env.name || !installDir || !hasIPythonSupport(env.name) || isUpdatingEnvironment,
      condition: hasIPythonSupport(env.name),
    },
    {
      name: 'OpenBB CLI',
      description: 'Start an OpenBB CLI session.',
      icon: <GamestonkIcon className="w-8 h-8" />,
      action: () => startCliSession(env.name),
      disabled: !env.name || !installDir || !hasCliSupport(env.name) || isUpdatingEnvironment,
      condition: hasCliSupport(env.name),
    },
    {
      name: 'System Shell',
      description: 'Open the default system shell in the environment.',
      icon: <CustomIcon id="terminal" className="w-9 h-9 -mr-1" />,
      action: () => openSystemTerminal(env.name),
      disabled: !env.name || !installDir || isUpdatingEnvironment,
      condition: true,
    },
  ];

  return (
    <div>
      <Tooltip content="Open applications" className="tooltip-theme">
        <Button
          onClick={toggleModal}
          variant="secondary"
          className="button-secondary shadow-sm px-2 py-1"
          size="xs"
          type="button"
        >
          <span className="body-xs-medium">
            Applications
          </span>
        </Button>
      </Tooltip>
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
          <div
            ref={modalRef}
            className="bg-theme-secondary border border-theme-modal rounded-lg shadow-lg w-full max-w-lg p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="body-lg-bold text-theme-primary">
                Applications
              </h2>
              <Tooltip content="Close" className="tooltip-theme">
                <Button
                  onClick={toggleModal}
                  variant="ghost"
                  size="icon"
                  className="button-ghost"
                >
                  <CustomIcon id="close" className="h-6 w-6" />
                </Button>
              </Tooltip>
            </div>
            <ul className="space-y-3">
              {applications.map((app) =>
                app.condition ? (
                  <li
                    key={app.name}
                    className="bg-theme-tertiary rounded-sm border border-theme-modal p-2 flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div className="mr-4">{app.icon}</div>
                      <div>
                        <p className="body-md-bold text-theme-primary">{app.name}</p>
                        <p className="body-xs-regular text-theme-secondary">{app.description}</p>
                      </div>
                    </div>
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        app.action();
                      }}
                      disabled={app.disabled}
                      variant="secondary"
                      size="xs"
                      className={`shadow-sm px-2 py-1 mr-1 ${app.name === 'Jupyter' && app.status === 'starting' ? 'button-outline' : 'button-startstop stopped'}`}
                    >
                      {app.name === 'Jupyter' && (app.status === 'starting' || app.status === 'stopping') ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-theme-accent" />
                      ) : app.name === 'Jupyter' && app.status === 'running' ? (
                        'Open'
                      ) : app.name === 'System Shell' ? (
                        'Open'
                      ) : (
                        'Start'
                      )}
                    </Button>
                  </li>
                ) : null
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
