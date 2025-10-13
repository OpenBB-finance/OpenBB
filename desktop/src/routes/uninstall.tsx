import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { confirm } from "@tauri-apps/plugin-dialog";
import { listen } from "@tauri-apps/api/event";
import { Button } from "@openbb/ui-pro";
import CustomIcon from "../components/Icon";

export default function Uninstall() {
  const router = useRouter();
  const [isUninstalling, setIsUninstalling] = useState(false);
  const [removeUserData, setRemoveUserData] = useState(false);
  const [removeSettings, setRemoveSettings] = useState(false);
  const [uninstallProgress, setUninstallProgress] = useState("");
  const [installationDirectory, setInstallationDirectory] = useState<string>("");
  const [userDataDirectory, setUserDataDirectory] = useState<string>("");
  const [settingsDirectory, setSettingsDirectory] = useState<string>("");
  const [showProgressDialog, setShowProgressDialog] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(true);

  // Fetch directories on component mount
  useEffect(() => {
    async function fetchDirectories() {
      try {
        const installDir = await invoke('get_installation_directory');
        setInstallationDirectory(installDir as string);
        const userDataDir = await invoke('get_userdata_directory');
        setUserDataDirectory(userDataDir as string);
        const settingsDir = await invoke('get_settings_directory');
        setSettingsDirectory(settingsDir as string);
      } catch (error) {
        console.error('Error fetching directories:', error);
      }
    }

    fetchDirectories();
  }, []);

  // Listen for uninstallation progress events
  useEffect(() => {
    if (!isUninstalling) return;

    const unlisten = listen("uninstall_progress", (event) => {
      setUninstallProgress(event.payload as string);
    });

    return () => {
      unlisten.then(fn => fn());
    };
  }, [isUninstalling]);

  const handleCloseModal = () => {
    if (!isUninstalling) {
      setIsModalOpen(false);
      router.history.back();
    }
  };

  const handleUninstall = async () => {
    const confirmed = await confirm(
      'This action cannot be undone.\n\nClick OK to continue.',
      { title: 'Confirm Uninstall', kind: 'warning' }
    );

    if (!confirmed) return;

    setIsUninstalling(true);
    setShowProgressDialog(true);

    try {
      setUninstallProgress("Starting uninstallation...");
      
      await invoke('uninstall_application', { 
        removeUserData, 
        removeSettings 
      });
      
      // Show final progress message
      setUninstallProgress("Uninstallation complete! Closing application...");
      
      // Give user time to see the completion message before closing
      setTimeout(() => {
        setShowProgressDialog(false);
        invoke('app.exit');
      }, 2000);
      
    } catch (error) {
      console.error('Uninstallation error:', error);
      setIsUninstalling(false);
      setShowProgressDialog(false);
      await confirm(
        `An error occurred during uninstallation: ${error}`,
        { title: 'Uninstallation Error', kind: 'error' }
      );
    }
  };

  if (!isModalOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
      <div className="relative bg-theme-secondary rounded-lg border border-theme-modal shadow-lg max-w-[90vw] w-full max-h-[90vh] overflow-y-auto">
        <div className="p-5 flex flex-col">
          <div className="flex flex-1 justify-between items-center">
            <h1 className="body-xl-bold mb-2 relative bottom-2 text-theme-primary">Uninstall Application & Data</h1>
                    {/* Close button */}
            <Button
              onClick={handleCloseModal}
              disabled={isUninstalling}
              className="button-ghost absolute top-4 right-4 text-theme-muted hover:text-theme-primary disabled:opacity-50 disabled:cursor-not-allowed z-10"
              variant="ghost"
              size="icon"
              aria-label="Close modal"
            >
              <CustomIcon id="close" className="w-6 h-6" />
            </Button>
          </div>
          <p className="mb-4 body-sm-regular text-theme-secondary">
            Remove the application, environments, and associated files from your system.< br />
            To uninstall only the UI application, please use your system's standard application removal process.
          </p>
          <p className="mb-3 body-sm-regular text-theme-primary ml-1 mt-2">
            Please select the components you wish to remove. <span className="body-sm-bold">This action cannot be undone.</span>
          </p>
          <div className="pt-1 pb-3">

            <div className="space-y-5">
              {/* Required Removal */}
              <div className="rounded-sm bg-theme-quartary shadow-md px-5 pt-4 pb-5">
                <div className="flex items-center">
                  <input
                    className="checkbox relative top-0.5 mr-3 h-4 w-4"
                    type="checkbox"
                    id="removeCondaEnv"
                    checked={true}
                    readOnly
                  />
                  <label className="form-check-label" htmlFor="removeCondaEnv">
                    <strong className="text-red-500">Remove Conda and Environments</strong>
                    <span className="ml-2 text-xs align-middle bg-red-100 text-red-600 px-2 py-0.5 rounded">Required</span>
                    <p className="body-xs-regular text-theme-muted mb-0 mt-1">
                      <code>{installationDirectory}</code>
                    </p>
                  </label>
                </div>
              </div>

              {/* User Data Removal */}
              <div className="rounded-sm bg-theme-quartary shadow-md px-5 pt-4 pb-5">
                <div className="flex items-center">
                  <input
                    className="checkbox relative top-0.5 mr-3 h-4 w-4"
                    type="checkbox"
                    id="removeUserData"
                    checked={removeUserData}
                    onChange={(e) => setRemoveUserData(e.target.checked)}
                    disabled={isUninstalling}
                  />
                  <label className="form-check-label" htmlFor="removeUserData">
                    <strong className="text-theme-primary">Remove user data</strong>
                    <p className="body-xs-regular text-theme-muted mb-0 mt-1">
                      <code>{userDataDirectory}</code>
                    </p>
                  </label>
                </div>
              </div>

              {/* Settings Removal */}
              <div className="rounded-sm bg-theme-quartary shadow-md px-5 pt-4 pb-5">
                <div className="flex items-center">
                  <input
                    className="checkbox relative top-0.5 mr-3 h-4 w-4"
                    type="checkbox"
                    id="removeSettings"
                    checked={removeSettings}
                    onChange={(e) => setRemoveSettings(e.target.checked)}
                    disabled={isUninstalling}
                  />
                  <label className="form-check-label" htmlFor="removeSettings">
                    <strong className="text-theme-primary">Remove application settings</strong>
                    <p className="body-xs-regular text-theme-muted mb-0 mt-1">
                      <code>{settingsDirectory}</code>
                    </p>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Uninstall Button */}
          <div className="flex gap-2 justify-end mt-4">
            <Button
              className="button-outline shadow-md px-2 py-1"
              variant="outline"
              size="sm"
              onClick={handleCloseModal}
              disabled={isUninstalling}
            >
              Cancel
            </Button>
            <Button
              className="button-danger shadow-md px-2 py-1"
              variant="danger"
              size="sm"
              onClick={handleUninstall}
              disabled={isUninstalling}
            >
              {isUninstalling ? "Uninstalling..." : "Uninstall"}
            </Button>
          </div>
        </div>

        {/* Progress Dialog */}
        {showProgressDialog && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center cursor-not-allowed rounded-lg">
            <div className="bg-theme-secondary border border-theme-accent rounded-lg shadow-lg p-6 max-w-md w-full">
              <div className="flex flex-col items-center">
                <div className="flex items-center justify-center p-4 rounded-lg w-full">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-theme-accent mr-3" />
                  <span className="text-theme-primary body-sm-regular">{uninstallProgress || "Processing..."}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export const Route = createFileRoute("/uninstall")({
  component: Uninstall,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      directory: search.directory as string | undefined,
      userDataDir: search.userDataDir as string | undefined
    };
  }
});