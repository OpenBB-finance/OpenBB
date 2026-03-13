import { useNavigate } from "@tanstack/react-router";
import { useForm, FormProvider } from "react-hook-form";
import { Button, Tooltip } from "@openbb/ui-pro";
import { invoke } from "@tauri-apps/api/core";
import { confirm } from "@tauri-apps/plugin-dialog";
import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect, useRef } from "react";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {FolderIcon} from "~/components/Icon";

// Define form schema using Zod
const formSchema = z.object({
  installDir: z.string().min(1, "Installation directory is required").refine(value => !/\s/.test(value), {
    message: "Path cannot contain spaces",
  }),
  userDataDir: z.string().min(1, "User data directory is required").refine(value => !/\s/.test(value), {
    message: "Path cannot contain spaces",
  }),
});

type FormValues = z.infer<typeof formSchema>;

// Define the route
export const Route = createFileRoute("/setup")({
  component: Setup,
});

export default function Setup() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [defaultHome, setDefaultHome] = useState("");
  const isSubmittingRef = useRef(false);

  // Initialize React Hook Form
  const methods = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      installDir: "",
      userDataDir: "",
    },
  });

  const { handleSubmit, setValue, watch, formState } = methods;
  const { errors } = formState;

  // Watch form values
  const installDir = watch("installDir");
  const userDataDir = watch("userDataDir");

  // Load home directory and set defaults on component mount
  useEffect(() => {
    async function loadHomeDirectory() {
      try {
        const homeDir = await invoke<string>("get_home_directory");
        if (homeDir) {
          setDefaultHome(homeDir);

          // Use platform detection for Windows vs. POSIX paths
          if (navigator.userAgent.includes("Windows")) {
            setValue("installDir", `${homeDir}\\OpenBB`);
            setValue("userDataDir", `${homeDir}\\OpenBBUserData`);
          } else {
            setValue("installDir", `${homeDir}/OpenBB`);
            setValue("userDataDir", `${homeDir}/OpenBBUserData`);
          }
        }
      } catch (error) {
        console.error("Failed to get home directory:", error);
        setErrorMessage(`Unable to determine home directory: ${error}`);
      }
    }

    loadHomeDirectory();
  }, [setValue]);

  // Handle installation start with debounce protection
  async function onSubmit(data: FormValues) {
    // Prevent duplicate submissions
    if (isSubmittingRef.current) {
      console.log("Submission already in progress, ignoring duplicate call");
      return;
    }

    setErrorMessage(null);
    isSubmittingRef.current = true;

    try {
      // Check if the installation directory already exists
      const directoryExists = await invoke<boolean>("check_directory_exists", {
        path: data.installDir.trim(),
      });

      if (directoryExists) {
        // Use Tauri dialog confirm instead of modal
        const confirmed = await confirm(
          "Target destination already exists.\n\nDo you want to overwrite?\n\n",
          { title: "Overwrite Installation Directory?", kind: "warning" }
        );
        if (!confirmed) {
          isSubmittingRef.current = false;
          return;
        }
      }

      // Proceed with installation if directory doesn't exist
      await proceedWithInstallation(data);
    } catch (error) {
      console.error("Failed to check directory existence:", error);
      setErrorMessage(`Failed to check directory existence: ${error}`);
      isSubmittingRef.current = false;
    }
  }

  // Proceed with installation
  async function proceedWithInstallation(data: FormValues) {
    setIsLoading(true);

    try {
      await invoke("install_to_directory", {
        directory: data.installDir,
        userDataDirectory: data.userDataDir,
      });

      navigate({
        to: "/installation-progress",
        search: {
          directory: data.installDir,
          userDataDir: data.userDataDir,
        },
      });
    } catch (error) {
      console.error("Failed to set up installation directories:", error);
      setErrorMessage(`Installation setup failed: ${error}`);
      isSubmittingRef.current = false;
    } finally {
      setIsLoading(false);
    }
  }

  // Browse for directories with automatic window focus restoration
  async function browseDirectory(field: keyof FormValues, title: string) {
    try {
      const selectedDir = await invoke<string>("select_directory", {
        prompt: `Select ${title}`,
      });

      if (selectedDir) {
        setValue(field, selectedDir, { shouldValidate: true });
      }
    } catch (error) {
      console.error(`Error selecting ${title.toLowerCase()} directory:`, error);
      if (String(error).includes("User canceled")) {
        console.log("User canceled directory selection");
      } else {
        setErrorMessage(`Failed to select directory: ${error}`);
      }
    }
  }

  return (
    <div>
      <FormProvider {...methods}>
        <div className="flex flex-col bg-theme-secondary">
					<p className="text-theme-secondary body-xs-regular mt-6">
						STEP <span className="text-theme-accent">1</span> OF <span className="text-theme-accent">3</span>
					</p>
          <h1 className="body-xl-bold mb-2 text-theme-primary">Installation & Setup</h1>
          <p className="mb-4 body-sm-regular text-theme-secondary">
            This application uses an isolated Miniforge installation for environment management and dependency solving.<br />
            Existing Conda executables, environments, and global packages will be unaffected.
            <br />
          </p>
          <p className="mb-5 body-sm-regular text-theme-primary mt-1">
            Please select the directories where Conda, OpenBB, and its user data will be stored.
          </p>

          {errorMessage && (
            <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100 rounded border border-red-300 dark:border-red-700">
              {errorMessage}
            </div>
          )}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
            {/* Installation Directory Input */}
            <div className="rounded-sm bg-theme-primary shadow-md px-5 pt-5 pb-5">
              <div className="space-y-3">
              <label htmlFor="installDir" className="text-theme-secondary body-md-medium">
                Installation Directory
              </label>
                <div className="flex w-full gap-2">
                  <input
                    id="installDir"
                    placeholder={defaultHome || "Select directory..."}
                    value={installDir}
                    onChange={(e) => setValue("installDir", e.target.value, { shouldValidate: true })}
                    name="installDir"
                    className="directory-input flex-1 text-theme-secondary"
                  />
                  <Tooltip
                    content="Browse for installation directory."
                    className="tooltip tooltip-theme"
                  >
                    <Button
                      type="button"
                      onClick={() => browseDirectory("installDir", "Installation Directory")}
                      size="icon"
                      className="button-ghost ml-2"
                      variant="ghost"
                      aria-label="browse for installation directory"
                    >
                      <FolderIcon className="h-5 w-5" />
                    </Button>
                  </Tooltip>
                </div>
              </div>
              {errors.installDir && (
                <p className="text-sm font-medium text-red-500 dark:text-red-400 mt-1">
                  {errors.installDir.message}
                </p>
              )}
              <p className="body-xs-regular text-theme-muted mt-3">
                Where Miniforge, environments, and other application files will be installed.
              </p>
            </div>

            {/* User Data Directory Input */}
              <div className="rounded-md bg-theme-primary shadow-md px-5 pt-4 pb-4">
                <div className="space-y-3">
                  <label htmlFor="userDataDir" className="text-theme-secondary body-md-medium">
                    User Data Directory
                  </label>
                <div className="flex w-full gap-2">
                  <input
                    id="userDataDir"
                    placeholder="Select user data directory..."
                    value={userDataDir}
                    onChange={(e) => setValue("userDataDir", e.target.value, { shouldValidate: true })}
                    name="userDataDir"
                    className="directory-input flex-1"
                  />
                  <Tooltip
                    content="Browse for user data directory."
                    className="tooltip tooltip-theme"
                  >
                    <Button
                      type="button"
                      onClick={() => browseDirectory("userDataDir", "User Data Directory")}
                      size="icon"
                      className="button-ghost"
                      variant="ghost"
                      aria-label="browse for user data directory"
                    >
                      <FolderIcon className="h-5 w-5 ml-2" />
                    </Button>
                  </Tooltip>
                </div>
              </div>
              {errors.userDataDir && (
                <p className="text-sm font-medium text-red-500 dark:text-red-400 mt-1">
                  {errors.userDataDir.message}
                </p>
              )}
              <p className="body-xs-regular text-theme-muted mt-3">
                Where OpenBBUserData files and cache will be stored.
              </p>
            </div>
          </form>
          </div>
          <div className="flex justify-between items-center bg-theme-secondary mb-5">
            <div className="mt-4">
            <p className="body-xs-medium text-theme-muted text-left pt-5">
              Expect the initial installation to take a few minutes, and between 1-2 GB of disk space.
              <br />
              By continuing, you explicitly agree to the terms and conditions of the {" "}
              <a
                href="https://raw.githubusercontent.com/conda-forge/miniforge/refs/heads/main/LICENSE"
                target="_blank"
                rel="noopener noreferrer"
                className="text-theme-accent"
              >
                Miniforge License
              </a>
              .
            </p>
            </div>
          {/* Form Actions - Outside the form containers */}
          <div className="flex flex-row gap-2 justify-end mt-5 ml-2">
            <Tooltip
              content="Cancel the installation and quit the application."
              className="tooltip tooltip-theme"
            >
              <Button
                type="button"
                onClick={async () => {
                  const confirmed = await confirm(
                    "Are you sure you want to quit the installation?",
                    { title: "Quit Installation", kind: "warning" }
                  );
                  if (confirmed) {
                    // Quit the application
                    await invoke("quit_application");
                  }
                }}
                variant="outline"
                disabled={isLoading}
                size="sm"
                className="button-outline px-2 py-1 shadow-md"
              >
                Cancel
              </Button>
            </Tooltip>
            <Tooltip
              content="Begin the installation process by installing Miniforge and setting up the environment. "
              className="tooltip tooltip-theme"
            >
              <Button 
                onClick={handleSubmit(onSubmit)} 
                disabled={isLoading} 
                variant="neutral" 
                size="sm" 
                className="button-neutral shadow-md px-2 py-1 whitespace-nowrap"
              >
                {isLoading ? "Setting up..." : "Begin Installation"}
              </Button>
            </Tooltip>
          </div>
        </div>
      </FormProvider>
    </div>
  );
}
