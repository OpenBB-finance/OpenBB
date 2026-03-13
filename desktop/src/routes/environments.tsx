import { Button, Tooltip } from "@openbb/ui-pro";
import { createFileRoute, useSearch } from "@tanstack/react-router";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { exists, BaseDirectory } from '@tauri-apps/plugin-fs';
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AddExtensionSelector, PythonVersionSelector } from "../components/AddExtensionSelector";
import { EnvironmentActions } from "../components/EnvironmentActions";
import { ExtensionSelector } from "../components/InstallComponents";
import CustomIcon, { DocumentationIcon, FolderIcon, RefreshIcon } from "../components/Icon";
import { useEnvironmentCreation } from "../contexts/EnvironmentCreationContext";

// LocalStorage key for environment extensions cache
const ENV_EXTENSIONS_CACHE_KEY = "env-extensions-cache";

// Types
interface Environment {
	name: string;
	pythonVersion: string;
	path: string;
}

interface InstallationState {
	is_installed: boolean;
	installation_directory: string | null;
}

interface Extension {
	package: string;
	version: string;
	install_method: "pip" | "conda";
	channel: string;
}

interface JupyterStatus {
	running: boolean;
	url?: string;
}

interface CacheEntry {
	extensions: Extension[];
	pythonVersion: string;
}

const openDocumentation = async () => {
	try {
		// Open documentation URL in a new window
		await invoke("open_url_in_window", {
			url: "https://docs.openbb.co/desktop/environments",
			title: "Open Data Platform Documentation",
		});
	} catch (err) {
		console.error("Failed to open documentation:", err);
	}
};

// Helper function to extract stderr portion from error messages
const extractStderr = (errorMessage: string): string => {
	if (typeof errorMessage !== "string") return String(errorMessage);

	if (errorMessage.includes("Stderr:")) {
		const stderrMatch = errorMessage.match(
			/Stderr:([\s\S]*?)(?:$|Exit code:|Stdout:)/,
		);
		return stderrMatch ? stderrMatch[1].trim() : errorMessage;
	}

	if (errorMessage.includes("Pip subprocess error:") && errorMessage.includes("Stdout:")) {
		const stdoutMatch = errorMessage.match(
			/Stdout:([\s\S]*?)(?:$|Exit code:|Stderr:)/,
		);
		return stdoutMatch ? stdoutMatch[1].trim() : errorMessage;
	}

	return errorMessage;
};

// Add a helper function at the top of the file after imports
const isFutureWarningOnly = (errorMsg: string): boolean => {
	if (!errorMsg) return false;

	// Check if error is only a FutureWarning (not a real error)
	return (
		errorMsg.includes("FutureWarning:") &&
		!errorMsg.includes("Error:") &&
		!errorMsg.includes("failed") &&
		!errorMsg.includes("Pip subprocess error:")
	);
};

const isPipSubprocessError = (errorMsg: string): boolean => {
	if (!errorMsg) return false;
	return errorMsg.includes("Pip subprocess error:");
}

const escapeAppleScriptString = (script: string) =>
	script.replace(/\\/g, "\\\\").replace(/"/g, '\\"');

function EnvironmentActionButtons({
	showCreateEnvironment,
	handleRequirementsFileSelect,
}: {
	showCreateEnvironment: () => void;
	handleRequirementsFileSelect: () => void;
}) {
	const handleUpdateAndReload = () => {
        localStorage.removeItem("env-extensions-cache");
        window.location.reload();
    };

	return (
		<div className="flex items-center justify-center">
			<div className="flex items-center gap-2">
				<Tooltip
					content="Create a new Conda environment."
					className="tooltip-theme"
				>
					<Button
						onClick={showCreateEnvironment}
						variant="neutral"
						className="button-neutral shadow-sm px-2 py-1"
						size="sm"
					>
						<span className="body-xs-medium text-theme-primary whitespace-nowrap justify-center">New Environment</span>
					</Button>
				</Tooltip>
				<Tooltip
					content="Create an environment from a YAML, pyproject.toml, or requirements.txt file."
					className="tooltip-theme"
				>
					<Button
						onClick={handleRequirementsFileSelect}
						variant="secondary"
						className="button button-secondary shadow-sm px-2 py-1"
						size="sm"
					>
						<span className="body-xs-medium text-theme-primary whitespace-nowrap">Import Environment</span>
					</Button>
				</Tooltip>
				<Tooltip
					content="Refresh the list of environments and extensions."
					className="tooltip-theme"
				>
					<Button
						onClick={handleUpdateAndReload}
						variant="secondary"
						className="button-secondary shadow-sm px-2 py-1 group"
						size="sm"
					>
						<RefreshIcon className="h-4 w-4 text-[var(--ghost-icon)] group-hover:text-[var(--ghost-icon-hover)]" />
					</Button>
				</Tooltip>
				<Tooltip
					content="Open the documentation for this screen."
					className="tooltip-theme"
				>
					<Button
						onClick={openDocumentation}
						variant="secondary"
						className="button-secondary shadow-sm px-2 py-1 group"
						size="sm"
					>
						<DocumentationIcon className="h-4 w-4 text-[var(--ghost-icon)] group-hover:text-[var(--ghost-icon-hover)]" />
					</Button>
				</Tooltip>
			</div>
		</div>
	);
}

function ExtensionRow({
    ext,
    updatingExtension,
    installExtensionsLoading,
    handleUpdateExtension,
    setExtensionToRemove,
    setShowRemoveConfirmation,
}: {
    ext: Extension;
    updatingExtension: string | null;
    installExtensionsLoading: boolean;
    handleUpdateExtension: (packageName: string) => void;
    setExtensionToRemove: (extension: Extension | null) => void;
    setShowRemoveConfirmation: (show: boolean) => void;
}) {
    return (
        <div className="ext-row flex justify-between items-center p-2 pl-2 border border-theme-modal rounded-sm relative mb-2 bg-theme-quartary shadow-sm">
            <div className="flex items-baseline whitespace-nowrap gap-2">
                <h5 className="body-sm text-theme leading-none">
                    {ext.package}
                </h5>
                <p className="body-xs-regular text-theme-secondary leading-none">
                    {ext.version || "unknown"}
                </p>
            </div>
            <div className="ext-actions flex gap-2 items-center">
                <Tooltip content="Update the extension to the latest version." className="tooltip-theme">
                    <Button
                        onClick={() => handleUpdateExtension(ext.package)}
                        disabled={!!updatingExtension || installExtensionsLoading}
                        variant="ghost"
                        size="icon"
                        className="button-ghost"
                    >
                        {updatingExtension === ext.package ? (
                            <div className="flex items-center justify-center w-4 h-4">
                                <div className="animate-spin h-4 w-4 border-t-2 border-b-2 border-blue-500 rounded-full" />
                            </div>
                        ) : (
                            <RefreshIcon className="h-4 w-4" />
                        )}
                    </Button>
                </Tooltip>
                <Tooltip content="Remove extension from the environment." className="tooltip-theme">
                    <Button
                        onClick={() => {
                            setExtensionToRemove(ext);
                            setShowRemoveConfirmation(true);
                        }}
                        disabled={installExtensionsLoading}
                        variant="ghost"
                        size="icon"
                        className="button-ghost"
                    >
                        <CustomIcon id="bin" className="h-4 w-4" />
                    </Button>
                </Tooltip>
            </div>
        </div>
    );
}

export default function EnvironmentsPage() {
	const search = useSearch({ from: "/environments" });
	const { setIsCreatingEnvironment } = useEnvironmentCreation();
	const [creatingFromRequirements, setCreatingFromRequirements] =
		useState(false);
	const [requirementsFileName, setRequirementsFileName] = useState<
		string | null
	>(null);
	const [requirementsEnvName, setRequirementsEnvName] = useState("");
	const [requirementsError, setRequirementsError] = useState<string | null>(
		null,
	);
	const [requirementsLogs, setRequirementsLogs] = useState<string[]>([]);
	const [requirementsComplete, setRequirementsComplete] = useState(false);
	const [requirementsWarning, setRequirementsWarning] = useState<string | null>(null);
	const [environments, setEnvironments] = useState<Environment[]>([]);
	const [environmentsLoading, setEnvironmentsLoading] = useState(false);
	const [environmentsError, setEnvironmentsError] = useState<string | null>(
		null,
	);
	const [installDir, setInstallDir] = useState<string | null>(null);
	const [isCancellingCreation, setIsCancellingCreation] = useState(false);
	const [createStep, setCreateStep] = useState<
		"name" | "python" | "extensions"
	>("name");
	const [newEnvName, setNewEnvName] = useState("");
	const [newEnvNameInvalid, setNewEnvNameInvalid] = useState(false);
	const [newEnvPython, setNewEnvPython] = useState("3.12");
	const [creationLoading, setCreationLoading] = useState(false);
	const [createEnvironmentError, setCreateEnvironmentError] = useState<
		string | null
	>(null);
	const [creationWarning, setCreationWarning] = useState<string | null>(null);
	const [creationLogs, setCreationLogs] = useState<string[]>([]);
	const [creationComplete, setCreationComplete] = useState(false);
	const [isRemoving, setIsRemoving] = useState(false);
	const [removeEnvironmentError, setRemoveEnvironmentError] = useState<
		string | null
	>(null);
	const [isUpdatingEnvironment, setIsUpdatingEnvironment] = useState<Set<string>>(new Set());
	const [updateEnvironmentError, setUpdateEnvironmentError] = useState<
		string | null
	>(null);

	const [extensionSearchQuery, setExtensionSearchQuery] = useState("");
	const [activeEnv, setActiveEnv] = useState<string | null>(null);
	const [extensions, setExtensions] = useState<Extension[]>([]);
	const [extensionsLoading, setExtensionsLoading] = useState(false);
	const [extensionsError, setExtensionsError] = useState<string | null>(null);
	const [installExtensionsLoading, setInstallExtensionsLoading] =
		useState(false);
	const [isRemovingExtension, setIsRemovingExtension] = useState(false);
	const [extensionRemoveError, setExtensionRemoveError] = useState<
		string | null
	>(null);
	const [updatingExtension, setUpdatingExtension] = useState<string | null>(
		null,
	);
	const [updateExtensionError, setUpdateExtensionError] = useState<
		string | null
	>(null);

	const [extensionSelectorKey, setExtensionSelectorKey] = useState(0);
	const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
	const [jupyterStatus, setJupyterStatus] = useState<{
		[key: string]: "stopped" | "starting" | "stopping" | "running" | "error";
	}>({});
	const jupyterUrlRef = useRef<{ [key: string]: string | null }>({});
	const activeServers = useRef<Set<string>>(new Set());
	const [environmentPackages, setEnvironmentPackages] = useState<{
		[key: string]: Set<string>;
	}>({});
	const [requirementsFilePath, setRequirementsFilePath] = useState<
		string | null
	>(null);
	const [extensionToRemove, setExtensionToRemove] = useState<Extension | null>(
		null,
	);
	const [showRemoveConfirmation, setShowRemoveConfirmation] = useState(false);
	const [environmentToRemove, setEnvironmentToRemove] = useState<string | null>(
		null,
	);
	const [
		showEnvironmentRemoveConfirmation,
		setShowEnvironmentRemoveConfirmation,
	] = useState(false);

	const creationWarningRef = useRef<string | null>(null);
	const [currentWorkingDir, setCurrentWorkingDir] = useState<string | null>(
		null,
	);
	const [workingDirInput, setWorkingDirInput] = useState("");
	const [workingDirValid, setWorkingDirValid] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
	const scrollContainerRef = useRef<HTMLDivElement>(null);
	const [hasScrollbar, setHasScrollbar] = useState(false);
	const filteredEnvironments = useMemo(() => {
        if (!searchQuery.trim()) return environments;

        const query = searchQuery.toLowerCase();
        return environments.filter(env =>
            env.name.toLowerCase().includes(query) ||
            env.pythonVersion.toLowerCase().includes(query) ||
            env.path.toLowerCase().includes(query)
        );
	}, [environments, searchQuery]);

	// Validate directory when input changes
	useEffect(() => {
		const validateDirectory = async () => {
			if (!workingDirInput.trim()) {
				setWorkingDirValid(true);
				return;
			}
			try {
				const exists = await invoke<boolean>("check_directory_exists", {
					path: workingDirInput.trim()
				});
				setWorkingDirValid(exists);
			} catch (err) {
				console.error("Error checking directory:", err);
				setWorkingDirValid(false);
			}
		};

		const timeoutId = setTimeout(validateDirectory, 500); // Debounce validation
		return () => clearTimeout(timeoutId);
	}, [workingDirInput]);

	const handleDirectoryInputSubmit = () => {
		if (workingDirValid) {
			setCurrentWorkingDir(workingDirInput.trim() || null);
		}
	};

	// Handle Enter key press in input
	const handleDirectoryInputKeyPress = (e: React.KeyboardEvent) => {
		if (e.key === "Enter") {
			handleDirectoryInputSubmit();
		}
	};

	const deletedEnvironments = useRef(new Set<string>());
	const envCreatedRef = useRef(false);
	const createEnvironmentRef = useRef<(extensions?: string[]) => Promise<void>>();

	// Update environment creation context when modal or loading state changes
	useEffect(() => {
		setIsCreatingEnvironment(isCreateModalOpen || creationLoading || creatingFromRequirements);
	}, [isCreateModalOpen, creationLoading, creatingFromRequirements, setIsCreatingEnvironment]);

	// Get platform info
	const getPlatformInfo = useCallback(() => {
		const userAgent = navigator.userAgent.toLowerCase();
		return {
			isWindows: userAgent.includes("win"),
			isMac: userAgent.includes("mac"),
			isLinux: !userAgent.includes("win") && !userAgent.includes("mac"),
		};
	}, []);

	useEffect(() => {
		// Save the directory preference to persist across sessions
		invoke("save_working_directory", { path: currentWorkingDir ?? "" }).catch(
			(err) =>
				console.error("Failed to save working directory preference:", err),
		);
	}, [currentWorkingDir]);

	// Track if we've loaded environments yet to avoid showing spinner on refresh
	const hasLoadedEnvironments = useRef(false);

	// Load environments
	const fetchEnvironments = useCallback(async () => {
		if (!installDir) return;

		try {
			// Only show loading spinner if we haven't loaded environments yet
			if (!hasLoadedEnvironments.current) {
				setEnvironmentsLoading(true);
			}
			setEnvironmentsError(null);

			const envs: Environment[] = await invoke("list_conda_environments", {
				directory: installDir,
			});

			// Filter out the "base" environment and any marked for deletion
			const filteredEnvs = envs.filter(
				(env) =>
					env.name.toLowerCase() !== "base" &&
					!deletedEnvironments.current.has(env.name)
			);

			setEnvironments(filteredEnvs);
			hasLoadedEnvironments.current = true;
		} catch (err) {
			console.error("Failed to load environments:", err);
			setEnvironmentsError(`Failed to load environments: ${err}`);
			setEnvironmentsLoading(false);
		}
	}, [installDir]);

	const selectWorkingDirectory = async () => {
		try {
			const selectedDir = await invoke<string>("select_directory", {
				prompt: "Select working directory",
			});

			if (selectedDir) {
				setCurrentWorkingDir(selectedDir);
			}
		} catch (err) {
			console.error("Failed to select working directory:", err);
		}
	};

	// Load environments from cache first, then optionally refresh from backend
	const loadEnvironmentsFromCache = useCallback(async () => {
		if (!installDir) return;

		console.log("Loading environments from cache first...");

		// First, check if we have cached environment names
		try {
			const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
			if (cachedData) {
				const cache = JSON.parse(cachedData);
				const envNames = Object.keys(cache);

				if (envNames.length > 0) {
					console.log("Found cached environments:", envNames);

					// Create mock Environment objects from cache
					const cachedEnvs: Environment[] = envNames.map(name => ({
						name,
						pythonVersion: cache[name]?.pythonVersion || "N/A",
						path: `${installDir}/conda/envs/${name}`
					}));

					setEnvironments(cachedEnvs);
					hasLoadedEnvironments.current = true;
					console.log("Loaded environments from cache:", cachedEnvs);
					return;
				}
			}
		} catch (error) {
			console.error("Error loading from cache:", error);
		}

		// If no cache, call backend as fallback
		console.log("No cache found, calling backend...");
		await fetchEnvironments();
	}, [installDir, fetchEnvironments]);

	// Update cache after backend operations
	const updateCacheAfterBackendOperation = useCallback(async () => {
		if (!installDir) return;

		try {
			// Get fresh environment list from backend
			const envs: Environment[] = await invoke("list_conda_environments", {
				directory: installDir,
			});

			// Filter environments
			const filteredEnvs = envs.filter(
				(env) =>
					env.name.toLowerCase() !== "base" &&
					!deletedEnvironments.current.has(env.name)
			);

			// Update UI state
			setEnvironments(filteredEnvs);

			// Update cache with new environment names
			// We need to preserve existing extension data but add new environments
			try {
				const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
				const cache = cachedData ? JSON.parse(cachedData) : {};

				// Add new environments to cache with empty extension arrays if they don't exist
				for (const env of filteredEnvs) {
					if (!cache[env.name]) {
						cache[env.name] = { extensions: [], pythonVersion: env.pythonVersion };
					} else {
						cache[env.name].pythonVersion = env.pythonVersion;
					}
				}

				// Remove deleted environments from cache
				const currentEnvNames = new Set(filteredEnvs.map(env => env.name));
				for (const envName of Object.keys(cache)) {
					if (!currentEnvNames.has(envName)) {
						delete cache[envName];
					}
				}

				localStorage.setItem(ENV_EXTENSIONS_CACHE_KEY, JSON.stringify(cache));
				console.log("Cache updated after backend operation");
			} catch (e) {
				console.error("Error updating cache:", e);
			}
		} catch (err) {
			console.error("Failed to update cache after backend operation:", err);
		}
	}, [installDir]);

	// Initialize current working directory and load environments when install directory is set
	useEffect(() => {
		if (installDir) {
			// Load saved working directory preference or default to install directory
			invoke<string>("get_working_directory", { defaultDir: installDir })
				.then((dir) => {
					setCurrentWorkingDir(dir);
					setWorkingDirInput(dir || "");
				})
				.catch(() => {
					setCurrentWorkingDir(installDir); // Fallback to install directory
					setWorkingDirInput(installDir || "");
				});

			// Load environments from cache first
			loadEnvironmentsFromCache();
		}
	}, [installDir, loadEnvironmentsFromCache]);

	const handleRequirementsFileSelect = async () => {
		try {
			const filePath = await invoke<string>("select_requirements_file");

			// If user canceled the dialog, filePath will be empty
			if (!filePath) {
				return;
			}

			// Extract the file name from the path
			const fileName =
				filePath.split("/").pop() || filePath.split("\\").pop() || "";
			const fileExt = fileName.split(".").pop()?.toLowerCase();

			// Validate file type by extension
			if (!["txt", "toml", "yml", "yaml"].includes(fileExt || "")) {
				setRequirementsError(
					"Only requirements.txt, pyproject.toml, or YAML files are supported",
				);
				return;
			}

			setRequirementsFileName(fileName);
			setRequirementsFilePath(filePath);
			setCreatingFromRequirements(true);
		} catch (err) {
			console.error("Failed to select file:", err);
			setRequirementsError(`Failed to select file: ${err}`);
		}
	};

	const createEnvironmentFromRequirements = async () => {
		if (!requirementsFilePath || !installDir) return;

		const envNameSnapshot = requirementsEnvName;
		const processId = `requirements-${envNameSnapshot}-${Date.now()}`;

		// Set up event listener for logs
		const unlisten = await listen<{ processId: string; output: string }>(
			"process-output",
			(event) => {
				if (event.payload.processId === processId) {
					setRequirementsLogs((prevLogs) => {
						const newLog = event.payload.output;
						if (prevLogs.length > 0) {
							const lastLog = prevLogs[prevLogs.length - 1];
							const lastLogColonIndex = lastLog.indexOf(":");
							const newLogColonIndex = newLog.indexOf(":");

							if (lastLogColonIndex !== -1 && newLogColonIndex !== -1) {
								const lastLogPrefix = lastLog.substring(0, lastLogColonIndex);
								const newLogPrefix = newLog.substring(0, newLogColonIndex);

								if (lastLogPrefix === newLogPrefix) {
									const newLogs = [...prevLogs];
									newLogs[newLogs.length - 1] = newLog;
									return newLogs;
								}
							}
						}
						return [...prevLogs, newLog];
					});
				}
			},
		);

		try {
			setCreationLoading(true);
			setRequirementsError(null);
			setCreationWarning(null);
			setRequirementsLogs([]); // Clear previous logs

			// Register for process monitoring
			await invoke("register_process_monitoring", { processId });

			await invoke("create_environment_from_requirements", {
				name: requirementsEnvName,
				filePath: requirementsFilePath,
				directory: installDir,
				processId,
			});

			if (deletedEnvironments.current.has(envNameSnapshot)) {
				unlisten();
				return;
			}

			// Reset form
			setRequirementsEnvName("");
			setRequirementsFilePath(null);
			// Update cache and environments list
			await updateCacheAfterBackendOperation();
			await refreshEnvironmentUIState(requirementsEnvName);
			// Fetch and cache extensions for the newly created environment
			localStorage.removeItem("env-extensions-cache");
		} catch (err: unknown) {
			const errorMsg = String(err);
			if (!deletedEnvironments.current.has(envNameSnapshot)) {
				console.error("Failed to create environment from requirements:", errorMsg);
				if (errorMsg.includes("Warning:")) {
					setRequirementsWarning(errorMsg);
				} else {
					setRequirementsError(`Failed to create environment: ${errorMsg}`);
				}
			}
		} finally {
			if (deletedEnvironments.current.has(envNameSnapshot)) {
				console.log(
					`Performing cleanup for cancelled environment: ${envNameSnapshot}`,
				);
				if (installDir) {
					try {
						await invoke("remove_environment", {
							name: envNameSnapshot,
							directory: installDir,
						});
					} catch (cleanupErr) {
						console.error("Failed cleaning up cancelled environment:", cleanupErr);
						setRequirementsError(
							`Installation was cancelled, but cleanup failed. You may need to manually remove the directory for '${envNameSnapshot}'.`,
						);
					}
				}
				deletedEnvironments.current.delete(envNameSnapshot);
			}

			setCreationLoading(false);
			setIsCancellingCreation(false);
			setRequirementsComplete(true);
			unlisten();
		}
	};

	// Get installation directory from URL or state
	useEffect(() => {
		const getInstallDir = async () => {
			try {
				// First check if directory was passed in URL search params
				if (search.directory) {
					setInstallDir(search.directory as string);
					return;
				}

				// Fall back to getting it from system state
				const state = await invoke<InstallationState>("get_installation_state");
				if (state.installation_directory) {
					setInstallDir(state.installation_directory);
				} else {
					// Only show error if application is installed but directory is missing
					if (state.is_installed) {
						setEnvironmentsError(
							"Installation directory not found. Please reinstall the application.",
						);
					}
					// If not installed, don't show error - this is expected during first-time installation
					// However, we should still try to get a default directory for first-time setup
					else {
						// Try to get a default installation directory for first-time setup
						try {
							const homeDir = await invoke<string>("get_home_directory");
							if (homeDir) {
								const defaultInstallDir = `${homeDir}/OpenBB`;
								console.log("Using default installation directory for first-time setup:", defaultInstallDir);
								setInstallDir(defaultInstallDir);
							}
						} catch (homeErr) {
							console.error("Failed to get home directory for default install path:", homeErr);
							// Don't set an error here - let the user proceed and they'll get a proper error
							// when they try to create an environment if the directory is truly missing
						}
					}
				}
			} catch (err) {
				console.error("Failed to get installation state:", err);
				setEnvironmentsError(`Failed to get installation information: ${err}`);
			}
		};

		getInstallDir();
	}, []);

	const getFilteredExtensions = useCallback(() => {
		if (!extensionSearchQuery.trim()) return extensions;

		const query = extensionSearchQuery.toLowerCase();
		return extensions.filter(
			(ext) =>
				ext.package.toLowerCase().includes(query) ||
				ext.version?.toLowerCase().includes(query),
		);
	}, [extensions, extensionSearchQuery]);

	const updateEnvironment = async (envName: string) => {
		if (!installDir) {
			setUpdateEnvironmentError("Installation directory not found");
			return;
		}

		sessionStorage.setItem(`updating-env-${envName}`, 'true');
		setIsUpdatingEnvironment((prev) => new Set(prev).add(envName));
		setUpdateEnvironmentError(null);

		try {
			await invoke("update_environment", {
				environment: envName,
				directory: installDir,
			});
			await refreshEnvironmentUIState(envName);
		} catch (err) {
			console.error(`Failed to update environment ${envName}:`, err);
			setUpdateEnvironmentError(`Failed to update environment: ${err}`);
		} finally {
			sessionStorage.removeItem(`updating-env-${envName}`);
			setIsUpdatingEnvironment((prev) => {
				const next = new Set(prev);
				next.delete(envName);
				return next;
			});
		}
	};

	useEffect(() => {
		const updating = new Set<string>();
		// Check sessionStorage for any environments that were updating
		environments.forEach(env => {
			if (sessionStorage.getItem(`updating-env-${env.name}`)) {
				updating.add(env.name);

				// Set a timeout to clear stale updating states
				setTimeout(() => {
					sessionStorage.removeItem(`updating-env-${env.name}`);
					setIsUpdatingEnvironment((prev) => {
						if (prev.has(env.name)) {
							const next = new Set(prev);
							next.delete(env.name);
							return next;
						}
						return prev;
					});
				}, 300000); // 5 minutes timeout
			}
		});
		if (updating.size > 0) {
			setIsUpdatingEnvironment(updating);
		}
	}, [environments]);

	// Terminal session handler
	const openSystemTerminal = useCallback(
		async (envName: string) => {
			if (!envName || !installDir) return;

			const { isWindows, isMac } = getPlatformInfo();
			const condaDir = `${installDir}/conda`;
			const workDir = currentWorkingDir || installDir;

			try {
				// Execute platform-specific command to open terminal with working directory
				if (isWindows) {
					await invoke("execute_in_environment", {
						command: `start cmd.exe /k "cd /d "${workDir}" && "${condaDir}\\Scripts\\activate.bat" ${envName}"`,
						environment: "base",
						directory: installDir,
					});
				} else if (isMac) {
					const hasIterm = await exists("/Applications/iTerm.app", {
						baseDir: BaseDirectory.Home,
					});
					const appleScript = escapeAppleScriptString(
						hasIterm
							? `
tell application "iTerm"
	activate
	delay 0.2
	set newWindow to (create window with default profile)
	tell current session of newWindow
		write text "cd ${workDir} && source ${condaDir}/bin/activate ${envName}"
	end tell
end tell
`
							: `
tell application "Terminal"
	do script "cd ${workDir} && source ${condaDir}/bin/activate ${envName}"
	activate
end tell
`
					);
					console.log("Using AppleScript:", appleScript);
					await invoke("execute_in_environment", {
						command: `osascript -e "${appleScript}"`,
						environment: "base",
						directory: installDir,
					});
				} else {
					await invoke("execute_in_environment", {
						command: `x-terminal-emulator -e "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && exec bash"`,
						environment: "base",
						directory: installDir,
					});
				}
			} catch (err) {
				console.error("Failed to open system terminal:", err);
			}
		},
		[installDir, getPlatformInfo, currentWorkingDir],
	);

	const startCliSession = useCallback(
		async (envName: string) => {
			if (!envName || !installDir) return;

			const { isWindows, isMac } = getPlatformInfo();
			const condaDir = `${installDir}/conda`;
			const workDir = currentWorkingDir || installDir;

			try {
				// Execute platform-specific command to open terminal with working directory
				if (isWindows) {
					await invoke("execute_in_environment", {
						command: `start cmd.exe /k "cd /d "${workDir}" && "${condaDir}\\Scripts\\activate.bat" "${envName}" && openbb && exit"`,
						environment: "base",
						directory: installDir,
					});
				} else if (isMac) {
					const hasIterm = await exists("/Applications/iTerm.app", {
						baseDir: BaseDirectory.Home,
					});
					const appleScript = escapeAppleScriptString(
						hasIterm
							? `
tell application "iTerm"
	activate
	delay 0.2
	set newWindow to (create window with default profile)
	tell current session of newWindow
		write text "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && openbb && exit"
	end tell
end tell
`
							: `
tell application "Terminal"
	do script "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && openbb && exit"
	activate
end tell
`
					);
					console.log("Using AppleScript:", appleScript);
					await invoke("execute_in_environment", {
						command: `osascript -e "${appleScript}"`,
						environment: "base",
						directory: installDir,
					});
				} else {
					await invoke("execute_in_environment", {
						command: `x-terminal-emulator -e "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && exec openbb && exit"`,
						environment: "base",
						directory: installDir,
					});
				}
			} catch (err) {
				console.error("Failed to start CLI Session:", err);
			}
		},
		[installDir, getPlatformInfo, currentWorkingDir],
	);

	// Start Python session - fix to keep terminal alive
	const startPythonSession = async (envName: string) => {
		if (!envName || !installDir) return;

		const { isWindows, isMac } = getPlatformInfo();
		const condaDir = `${installDir}/conda`;
		const workDir = currentWorkingDir || installDir;

		try {
			let command = "";
			if (isWindows) {
				const pythonPart = `python -i${envName === "openbb" ? ` -c "from openbb import obb; print(obb)"` : ""}`;
				command = `start cmd.exe /k "cd /d "${workDir}" && "${condaDir}\\Scripts\\activate.bat" ${envName} && ${pythonPart} && exit"`;
			} else if (isMac) {
				const pythonPart = `python -i${envName === "openbb" ? ` -c 'from openbb import obb; print(obb)'` : ""}`;
				const hasIterm = await exists("/Applications/iTerm.app", {
					baseDir: BaseDirectory.Home,
				});
				const appleScript = escapeAppleScriptString(
					hasIterm
						? `
tell application "iTerm"
	activate
	delay 0.2
	set newWindow to (create window with default profile)
	tell current session of newWindow
		write text "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && ${pythonPart} && exit"
	end tell
end tell
`
						: `
tell application "Terminal"
	do script "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && ${pythonPart} && exit"
	activate
end tell
`
				);
				console.log("Using AppleScript:", appleScript);
				await invoke("execute_in_environment", {
					command: `osascript -e "${appleScript}"`,
					environment: "base",
					directory: installDir,
				});
			} else {
				const pythonPart = `python -i${envName === "openbb" ? ` -c 'from openbb import obb; print(obb)'` : ""}`;
				command = `x-terminal-emulator -e "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && ${pythonPart} && exit"`;
			}
			await invoke("execute_in_environment", {
				command,
				environment: "base",
				directory: installDir,
			});
		} catch (err) {
			console.error("Failed to start Python session:", err);
			alert(`Failed to start Python session: ${err}`);
		}
	};

	// Start IPython session - fix to keep terminal alive
	const startIPythonSession = async (envName: string) => {
		if (!envName || !installDir) return;

		const { isWindows, isMac } = getPlatformInfo();
		const condaDir = `${installDir}/conda`;
		const workDir = currentWorkingDir || installDir;

		try {
			let command = "";
			if (isWindows) {
				const ipythonPart = `ipython -i${envName === "openbb" ? ` -c "from openbb import obb; obb"` : ""}`;
				command = `start cmd.exe /k "cd /d "${workDir}" && "${condaDir}\\Scripts\\activate.bat" ${envName} && ${ipythonPart} && exit"`;
			} else if (isMac) {
				const ipythonPart = `ipython -i${envName === "openbb" ? ` -c 'from openbb import obb; obb'` : ""}`;
				const hasIterm = await exists("/Applications/iTerm.app", {
					baseDir: BaseDirectory.Home,
				});
				const appleScript = escapeAppleScriptString(
					hasIterm
						? `
tell application "iTerm"
	activate
	delay 0.2
	set newWindow to (create window with default profile)
	tell current session of newWindow
		write text "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && ${ipythonPart} && exit"
	end tell
end tell
`
						: `
tell application "Terminal"
	do script "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && ${ipythonPart} && exit"
	activate
end tell
`
				);
				console.log("Using AppleScript:", appleScript);
				await invoke("execute_in_environment", {
					command: `osascript -e "${appleScript}"`,
					environment: "base",
					directory: installDir,
				});
			} else {
				const ipythonPart = `ipython -i${envName === "openbb" ? ` -c 'from openbb import obb; obb'` : ""}`;
				command = `x-terminal-emulator -e "cd ${workDir} && source ${condaDir}/bin/activate ${envName} && ${ipythonPart} && exit"`;
			}
			await invoke("execute_in_environment", {
				command,
				environment: "base",
				directory: installDir,
			});
		} catch (err) {
			console.error("Failed to start iPython session:", err);
			alert(`Failed to start IPython session: ${err}`);
		}
	};

	// Force refresh environment packages data and UI state
	const refreshEnvironmentUIState = useCallback(
		async (envName: string) => {
			try {
				setExtensionsLoading(true);
				// Get fresh data from backend
				const result = await invoke<{ extensions: Extension[] }>(
					"get_environment_extensions",
					{
						name: envName,
					},
				);

				if (result?.extensions) {
					// Update extensions list and cache
					if (activeEnv === envName) {
						setExtensions(result.extensions);
					}

					// Update package set to refresh button visibility
					const packageSet = new Set<string>(
						result.extensions.map((ext) => ext.package.toLowerCase()),
					);
					setEnvironmentPackages((prev) => ({
						...prev,
						[envName]: packageSet,
					}));

					// Update cache with fresh data
					try {
						const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
						const cache = cachedData ? JSON.parse(cachedData) : {};
						if (!cache[envName]) {
							cache[envName] = {};
						}
						cache[envName].extensions = result.extensions;
						localStorage.setItem(
							ENV_EXTENSIONS_CACHE_KEY,
							JSON.stringify(cache),
						);
					} catch (e) {
						console.error("Error updating extensions cache:", e);
					}

					// Force refresh of environments list to update buttons
					setEnvironments((prev) => [...prev]);
				}
			} catch (err) {
				console.error(`Error refreshing UI state for ${envName}:`, err);
				setExtensionsError(`Failed to refresh extensions: ${err}`);
			} finally {
				setExtensionsLoading(false);
			}
		},
		[activeEnv],
	);

	// Initial load of cached extension data when component mounts
	useEffect(() => {
		const loadOrCreateCache = async () => {
			try {
				const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
				const cache = cachedData ? JSON.parse(cachedData) : {};
				let cacheNeedsUpdate = false;

				// Process existing cache entries first to populate UI quickly
				for (const [envName, envData] of Object.entries(cache)) {
					try {
						// Add a safeguard to handle malformed cache entries
						const extensions = (envData as CacheEntry)?.extensions || [];
						const packageSet = new Set<string>(
							extensions.map((ext) =>
								ext.package.toLowerCase(),
							),
						);
						setEnvironmentPackages((prev) => ({
							...prev,
							[envName]: packageSet,
						}));
					} catch (parseError) {
						console.error(
							`Error parsing cached extensions for ${envName}:`,
							parseError,
						);
					}
				}

				// Check for missing environments and fetch them
				if (environments.length > 0 && installDir) {
					const newCache = { ...cache };
					for (const env of environments) {
						if (!newCache[env.name] || !newCache[env.name].pythonVersion) {
							cacheNeedsUpdate = true;
							console.log(`Fetching extensions for ${env.name} to create/update cache...`);
							try {
								const result = await invoke<{ extensions: Extension[] }>(
									"get_environment_extensions",
									{ name: env.name }
								);

								newCache[env.name] = {
									extensions: result?.extensions || [],
									pythonVersion: env.pythonVersion,
								};

								const packageSet = new Set<string>(
									(result?.extensions || []).map((ext) => ext.package.toLowerCase())
								);
								setEnvironmentPackages((prev) => ({
									...prev,
									[env.name]: packageSet,
								}));
							} catch (error) {
								console.error(`Error fetching extensions for ${env.name}:`, error);
								newCache[env.name] = {
									extensions: [],
									pythonVersion: env.pythonVersion,
								};
							}
						}
					}

					if (cacheNeedsUpdate) {
						localStorage.setItem(ENV_EXTENSIONS_CACHE_KEY, JSON.stringify(newCache));
						console.log("Extensions cache updated and saved to localStorage.");
					}
				}
			} catch (error) {
				console.error("Error in loadOrCreateCache:", error);
			}
		};

		// Only run if we have environments to work with
		if (environments.length > 0) {
			setEnvironmentsLoading(true);
			loadOrCreateCache().finally(() => {
				setEnvironmentsLoading(false);
			});
		} else if (hasLoadedEnvironments.current) {
			setEnvironmentsLoading(false);
		}
	}, [environments, installDir]);


	useEffect(() => {
		// Only load initial data when component mounts
		if (environments && environments.length > 0) {
			// Just set active environment without showing extensions
			setActiveEnv(environments[0].name);
		}
	}, [environments]);

	// Helper functions to check if an environment has required packages
	const hasJupyterSupport = useCallback(
		(envName: string) => {
			// First check in the local memory state
			if (environmentPackages[envName]) {
				return (
					environmentPackages[envName].has("notebook") ||
					environmentPackages[envName].has("jupyter") ||
					environmentPackages[envName].has("jupyterlab")
				);
			}

			// If not in memory, check the localStorage cache
			try {
				const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
				if (cachedData) {
					const cache = JSON.parse(cachedData);
					if (cache?.[envName]?.extensions) {
						const packageNames = cache[envName].extensions.map((ext: Extension) =>
							ext.package.toLowerCase(),
						);
						return packageNames.some((pkg: string) =>
							["notebook", "jupyter", "jupyterlab"].includes(pkg),
						);
					}
				}
			} catch (error) {
				console.error(
					"Error checking cached extensions for Jupyter support:",
					error,
				);
			}

			// If all else fails, default to false
			return false;
		},
		[environmentPackages],
	);

	const hasIPythonSupport = useCallback(
		(envName: string) => {
			// First check in the local memory state
			if (environmentPackages[envName]) {
				return environmentPackages[envName].has("ipython");
			}

			// If not in memory, check the localStorage cache
			try {
				const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
				if (cachedData) {
					const cache = JSON.parse(cachedData);
					if (cache?.[envName]?.extensions) {
						const packageNames = cache[envName].extensions.map((ext: Extension) =>
							ext.package.toLowerCase(),
						);
						return packageNames.includes("ipython");
					}
				}
			} catch (error) {
				console.error(
					"Error checking cached extensions for IPython support:",
					error,
				);
			}

			// If all else fails, default to false
			return false;
		},
		[environmentPackages],
	);

	const hasCliSupport = useCallback(
		(envName: string) => {
			// First check in the local memory state
			if (environmentPackages[envName]) {
				return environmentPackages[envName].has("openbb-cli");
			}

			// If not in memory, check the localStorage cache
			try {
				const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
				if (cachedData) {
					const cache = JSON.parse(cachedData);
					if (cache?.[envName]?.extensions) {
						const packageNames = cache[envName].extensions.map((ext: Extension) =>
							ext.package.toLowerCase(),
						);
						return packageNames.includes("openbb-cli");
					}
				}
			} catch (error) {
				console.error(
					"Error checking cached extensions for OpenBB CLI support:",
					error,
				);
			}

			// If all else fails, default to false
			return false;
		},
		[environmentPackages],
	);

	// Remove environment
	const removeEnvironment = async (envName: string) => {
		if (!installDir) {
			setRemoveEnvironmentError("Installation directory not found");
			return;
		}

		try {
			// First clear UI state if we're viewing this environment
			if (activeEnv === envName) {
				setActiveEnv(null);
			}

			// Add to deletedEnvironments set IMMEDIATELY to prevent any fetch attempts
			deletedEnvironments.current.add(envName);
			console.log(
				`Added ${envName} to deleted environments set to prevent fetches`,
			);
			// Remove from backend
			await invoke("remove_environment", {
				name: envName,
				directory: installDir,
			});

			console.log(`Environment ${envName} removed, cleaning up cache`);

			// Delete this environment's entry from localStorage
			try {
				const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
				if (cachedData) {
					const cache = JSON.parse(cachedData);
					if (cache?.[envName]) {
						delete cache[envName];
						localStorage.setItem(
							ENV_EXTENSIONS_CACHE_KEY,
							JSON.stringify(cache),
						);
						console.log(`Removed ${envName} from localStorage cache`);
					}
				}

				// Also clear from memory state
				setEnvironmentPackages((prev) => {
					const updated = { ...prev };
					delete updated[envName];
					return updated;
				});
			} catch (e) {
				console.error("Error updating localStorage:", e);
			}

			// Update cache and environments list
			await updateCacheAfterBackendOperation();
			deletedEnvironments.current.delete(envName);
		} catch (err) {
			console.error(`Failed to remove environment ${envName}:`, err);
			setRemoveEnvironmentError(`Failed to remove environment: ${err}`);
		} finally {
			setEnvironmentToRemove(null);
			setIsRemoving(false);
		}
	};

	// Install extensions for an existing environment
	const handleInstallExtensions = async (newExtensions: string[]) => {
		if (!installDir || !activeEnv) {
			setExtensionsError("Missing directory or environment information");
			return;
		}

		if (newExtensions.length === 0) {
			return;
		}

		try {
			setInstallExtensionsLoading(true);
			setExtensionsError(null);

			await invoke("install_extensions", {
				extensions: newExtensions,
				environment: activeEnv,
				directory: installDir,
			});

			setActiveTab("manage");

			await refreshEnvironmentUIState(activeEnv);

			setExtensionSelectorKey((prev) => prev + 1);
			setInstallExtensionsLoading(false);
		} catch (err: unknown) {
			const errMsg = String(err);

			if (isPipSubprocessError(errMsg)) {
				console.error("Pip subprocess error during extension installation:", errMsg);
				setExtensionsError(errMsg);
				setInstallExtensionsLoading(false);
			}
			else if (isFutureWarningOnly(errMsg)) {
				try {
					const result = await invoke<{ extensions: Extension[] }>(
						"get_environment_extensions",
						{
							name: activeEnv,
						},
					);

					if (result?.extensions) {
						setExtensions(result.extensions);

						const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
						const cache = cachedData ? JSON.parse(cachedData) : {};
						if (cache[activeEnv]) {
							cache[activeEnv].extensions = result.extensions;
						}
						localStorage.setItem(
							ENV_EXTENSIONS_CACHE_KEY,
							JSON.stringify(cache),
						);
					}
				} catch (refreshErr) {
					console.error("Error fetching extensions after installation:", refreshErr);
				}
				setInstallExtensionsLoading(false);
			} else {
				console.error("Error installing extensions:", errMsg);
				setExtensionsError(errMsg);
				setInstallExtensionsLoading(false);
			}
		}
	};

	// Remove extension with confirmation
	const handleRemoveExtension = async (
		extensionInfo: Extension,
		envName: string,
	) => {
		if (!installDir) {
			setExtensionRemoveError("Missing directory information");
			return;
		}

		const { package: packageName } = extensionInfo;

		try {
			setIsRemovingExtension(true);
			setExtensionRemoveError(null);

			await invoke("remove_extension", {
				package: packageName,
				environment: envName,
				directory: installDir,
			});

			await refreshEnvironmentUIState(envName);
		} catch (err) {
			console.error(`Failed to remove extension ${packageName}:`, err);
			setExtensionRemoveError(`Failed to remove extension: ${err}`);
			await refreshEnvironmentUIState(envName);
		} finally {
			setIsRemovingExtension(false);
		}
	};

	const handleUpdateExtension = async (packageName: string) => {
		if (!installDir || !activeEnv) {
			setUpdateExtensionError("Missing directory or environment information");
			return;
		}

		try {
			setUpdatingExtension(packageName);
			setUpdateExtensionError(null);

			await invoke("update_extension", {
				package: packageName,
				environment: activeEnv,
				directory: installDir,
			});

			// Refresh extensions list after update
			setExtensionsLoading(true);
			try {
				const result = await invoke<{ extensions: Extension[] }>(
					"get_environment_extensions",
					{ name: activeEnv }
				);

				if (result?.extensions) {
					setExtensions(result.extensions);

					// Update cache
					const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
					const cache = cachedData ? JSON.parse(cachedData) : {};
					if (cache[activeEnv]) {
						cache[activeEnv].extensions = result.extensions;
					}
					localStorage.setItem(ENV_EXTENSIONS_CACHE_KEY, JSON.stringify(cache));
				}
			} catch (refreshErr) {
				console.error("Failed to refresh extensions after update:", refreshErr);
			} finally {
				setExtensionsLoading(false);
			}
		} catch (err) {
			console.error("Failed to update extension:", err);
			setUpdateExtensionError(`${err}`);
		} finally {
			setUpdatingExtension(null);
		}
	};

	// Create environment with extensions
	const createEnvironment = async (extensions: string[] = []) => {
		if (!installDir) {
			setCreateEnvironmentError(
				"Installation directory not found. Please complete the OpenBB installation process first by going to the Setup page.",
			);
			return;
		}
		const envNameSnapshot = newEnvName;
		const processId = `create-env-${envNameSnapshot}-${Date.now()}`;

		// Set up event listener for logs
		const unlisten = await listen<{ processId: string; output: string }>(
			"process-output",
			(event) => {
				if (event.payload.processId === processId) {
					setCreationLogs((prevLogs) => {
						const newLog = event.payload.output;
						if (prevLogs.length > 0) {
							const lastLog = prevLogs[prevLogs.length - 1];
							const lastLogColonIndex = lastLog.indexOf(":");
							const newLogColonIndex = newLog.indexOf(":");

							if (lastLogColonIndex !== -1 && newLogColonIndex !== -1) {
								const lastLogPrefix = lastLog.substring(0, lastLogColonIndex);
								const newLogPrefix = newLog.substring(0, newLogColonIndex);

								if (lastLogPrefix === newLogPrefix) {
									const newLogs = [...prevLogs];
									newLogs[newLogs.length - 1] = newLog;
									return newLogs;
								}
							}
						}
						return [...prevLogs, newLog];
					});
				}
			},
		);

		try {
			setCreationLoading(true);
			setCreateEnvironmentError(null);
			setCreationWarning(null);
			setCreationLogs([]); // Clear previous logs

			// Step 1: Create environment with base packages only (no extensions)
			console.log("Step 1: Creating environment with base packages...");
			await invoke("create_environment", {
				name: envNameSnapshot,
				pythonVersion: newEnvPython,
				extensions: [],
				directory: installDir,
				processId,
			});

			// Check if installation was cancelled before continuing
			if (deletedEnvironments.current.has(envNameSnapshot)) {
				return; // The `finally` block will handle cleanup.
			}

			// Step 2: Install extensions if any were selected
			if (extensions.length > 0) {
				console.log("Step 2: Installing selected extensions...", extensions);
				try {
					await invoke("install_extensions", {
						extensions: extensions,
						environment: envNameSnapshot,
						directory: installDir,
					});
					console.log("Extensions installed successfully");
				} catch (extErr) {
					const errorMsg = String(extErr);
					console.error("Error installing extensions:", errorMsg);
					creationWarningRef.current = `Environment '${envNameSnapshot}' created, but some packages failed to install. You can try adding them again from the extensions manager.\n\nDetails: ${extractStderr(
						errorMsg,
					)}`;
				}
			}

			if (deletedEnvironments.current.has(envNameSnapshot)) {
				return; // The `finally` block will handle cleanup.
			}

			// Update cache with extensions if they were installed successfully
			try {
				const result = await invoke<{ extensions: Extension[] }>(
					"get_environment_extensions",
					{ name: envNameSnapshot },
				);

				if (result?.extensions) {
					// Update extensions cache
					const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
					const cache = cachedData ? JSON.parse(cachedData) : {};
					cache[envNameSnapshot] = {
						extensions: result.extensions,
						pythonVersion: newEnvPython,
					};
					localStorage.setItem(ENV_EXTENSIONS_CACHE_KEY, JSON.stringify(cache));

					// Update the environmentPackages state
					const packageSet = new Set(
						result.extensions.map((ext) => ext.package.toLowerCase()),
					);
					setEnvironmentPackages((prev) => ({
						...prev,
						[envNameSnapshot]: packageSet,
					}));
				}
			} catch (e) {
				console.error("Error updating cache after environment creation:", e);
			}

			// Reset creation state
			setNewEnvName("");
			setNewEnvPython("");
			envCreatedRef.current = false; // Reset the flag

			// Update cache and environments list
			await updateCacheAfterBackendOperation();
			setActiveEnv(envNameSnapshot);

			// Load extensions from cache
			try {
				const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
				if (cachedData) {
					const cache = JSON.parse(cachedData);
					if (cache?.[envNameSnapshot]) {
						setExtensions(cache[envNameSnapshot]);
					}
				}
			} catch (e) {
				console.error("Error loading cached extensions:", e);
			}
		} catch (err) {
			const errMsg = String(err);

			if (deletedEnvironments.current.has(envNameSnapshot)) {
				// Error is expected on cancellation, so don't show it to the user.
				return;
			}

			// Handle specific error cases
			if (isFutureWarningOnly(errMsg) || errMsg.includes("is deprecated")) {
				console.log(
					"Non-fatal warning during environment creation - continuing as successful",
				);

				// Continue with the normal success flow
				const envNameFW = newEnvName;
				setNewEnvName("");
				setNewEnvPython("");
				envCreatedRef.current = false; // Reset the flag

				// Update cache and environments list
				await updateCacheAfterBackendOperation();
				setActiveEnv(envNameFW);
			} else {
				setCreateEnvironmentError(errMsg);
				envCreatedRef.current = false; // Reset the flag
				console.error("Error creating environment:", err);
			}
		} finally {
			if (deletedEnvironments.current.has(envNameSnapshot)) {
				console.log(
					`Performing cleanup for cancelled environment: ${envNameSnapshot}`,
				);
				if (installDir) {
					try {
						await invoke("remove_environment", {
							name: envNameSnapshot,
							directory: installDir,
						});
					} catch (cleanupErr) {
						console.error("Failed cleaning up cancelled environment:", cleanupErr);
						setCreateEnvironmentError(
							`Installation was cancelled, but cleanup failed. You may need to manually remove the directory for '${envNameSnapshot}'.`,
						);
					}
				}
				deletedEnvironments.current.delete(envNameSnapshot);
			}

			setCreationLoading(false);
			setCreationComplete(true);
			setIsCancellingCreation(false);
			unlisten();
		}
	};

	// Abort installation
	const handleAbortInstallation = (source: "new" | "requirements") => {
		setIsCancellingCreation(true);
		const envToDelete =
			source === "requirements" ? requirementsEnvName : newEnvName;

		if (envToDelete) {
			console.log(`Request to cancel installation of ${envToDelete}`);
			deletedEnvironments.current.add(envToDelete);
		}

		// Show cancelling message briefly, then close the modal
		setTimeout(() => {
			if (source === "requirements") {
				setCreatingFromRequirements(false);
			} else {
				setIsCreateModalOpen(false);
			}
			setCreationLoading(false);
			setCreationComplete(true);
		}, 5000); // Keep message on screen for 5 seconds
	};

	// Cancels the "installing extensions" modal. Note: this does not stop the
	// backend process, it only hides the modal to unblock the UI.
	// The process will complete and then be cleaned up
	const handleCancelExtensionInstall = () => {
		setInstallExtensionsLoading(false);
	};

	// Show extensions panel for an environment
	const showExtensions = async (envName: string) => {
		try {
			// Toggle extensions visibility
			if (showExtensionsForEnv === envName) {
				setShowExtensionsForEnv(null);
				return;
			}

			// Set active environment and show extensions panel
			setActiveEnv(envName);
			setShowExtensionsForEnv(envName);

			// ALWAYS load from cache ONLY - never call backend automatically
			const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
			if (cachedData) {
				try {
					const cache = JSON.parse(cachedData);
					if (cache?.[envName]) {
						setExtensions(cache[envName].extensions);
						return;
					}
				} catch (parseError) {
					console.error("Error parsing cached extensions:", parseError);
				}
			}

			// If no cache, just show empty state
			setExtensions([]);
		} catch (err) {
			console.error(`Error loading extensions for ${envName}:`, err);
			setExtensions([]);
		}
	};

	// Show create environment panel
	const showCreateEnvironment = () => {
		setCreateStep("name");
		setCreateEnvironmentError(null);
		setNewEnvName("");
		setNewEnvPython("3.12");
		setCreationLoading(false);
		setCreationWarning(null);
		setCreationLogs([]);
		setCreationComplete(false);
		setExtensionSelectorKey((prev) => prev + 1);
		setIsCreateModalOpen(true);
	};

	useEffect(() => {
		const handleEscapeKey = (e: KeyboardEvent) => {
			if (e.key === "Escape" && isCreateModalOpen) {
				setIsCreateModalOpen(false);
			}
		};

		document.addEventListener("keydown", handleEscapeKey);
		return () => document.removeEventListener("keydown", handleEscapeKey);
	}, [isCreateModalOpen]);

	// Check Jupyter server status
	useEffect(() => {
		// Only start polling if there are environments to check
		if (environments.length === 0) return;

		// Track currently polling environments
		const polling = new Map();

		const checkStatus = async () => {
			let shouldContinuePolling = false;

			for (const env of environments) {
				// Only poll environments that are in transition states or unknown
				if (
					jupyterStatus[env.name] === "starting" ||
					jupyterStatus[env.name] === "stopping" ||
					!jupyterStatus[env.name]
				) {
					try {
						const status = await invoke<JupyterStatus>("check_jupyter_server", {
							environment: env.name,
						});

						if (status.running) {
							setJupyterStatus((prev) => ({ ...prev, [env.name]: "running" }));
							jupyterUrlRef.current[env.name] = status.url || null;
							activeServers.current.add(env.name);
						} else if (
							jupyterStatus[env.name] === "running" ||
							jupyterStatus[env.name] === "stopping"
						) {
							setJupyterStatus((prev) => ({ ...prev, [env.name]: "stopped" }));
							jupyterUrlRef.current[env.name] = null;
							activeServers.current.delete(env.name);
						} else if (jupyterStatus[env.name] === "starting") {
							// Check how long we've been polling this environment
							const startTime = polling.get(env.name) || Date.now();
							polling.set(env.name, startTime);

							// If we've been polling for more than 30 seconds, mark as error
							if (Date.now() - startTime > 30000) {
								console.error(
									`Jupyter server for ${env.name} failed to start (timeout)`,
								);
								setJupyterStatus((prev) => ({ ...prev, [env.name]: "error" }));
							} else {
								// Continue polling only for starting state
								shouldContinuePolling = true;
							}
						}
					} catch (err) {
						console.error("Error checking Jupyter server status:", err);
					}
				}
			}

			// If no environments need polling, clear the interval
			if (!shouldContinuePolling) {
				if (intervalIdRef.current) {
					clearInterval(intervalIdRef.current);
					intervalIdRef.current = null;
				}
			}
		};

		// Reference to store interval ID for cleanup - properly typed for both NodeJS.Timeout and null
		const intervalIdRef = { current: null as NodeJS.Timeout | null };

		// Initial check
		checkStatus();

		// Set up interval for polling
		intervalIdRef.current = setInterval(checkStatus, 3000);

		// Clean up interval on unmount
		return () => {
			if (intervalIdRef.current) {
				clearInterval(intervalIdRef.current);
			}
		};
	}, [environments, jupyterStatus]);

	// Log servers that remain active when navigating away
	useEffect(() => {
		return () => {

				const activeServerNames = Array.from(activeServers.current);
				if (activeServerNames.length > 0) {
					console.log("Keeping Jupyter servers running while navigating away:", activeServerNames);
					// Store active servers in sessionStorage to track across page navigation
					try {
						sessionStorage.setItem('active-jupyter-servers', JSON.stringify(activeServerNames));
					} catch (err) {
						console.error("Failed to save active server list to sessionStorage:", err);
					}
				}
			};
	}, []);

	// Start or open Jupyter server
	const startJupyterLab = async (envName: string) => {
		if (
			!installDir ||
			jupyterStatus[envName] === "starting" ||
			jupyterStatus[envName] === "stopping"
		)
			return;

		// If server is already running, open it
		if (
			jupyterStatus[envName] === "running" &&
			jupyterUrlRef.current[envName]
		) {
			const url = jupyterUrlRef.current[envName];
			if (url) {
				openJupyterWindow(url);
			}
			return;
		}

		try {
			setJupyterStatus((prev) => ({ ...prev, [envName]: "starting" }));
			console.log(`Starting Jupyter Lab for environment: ${envName}`);

			// Use the current working directory for Jupyter
			const workDir = currentWorkingDir || installDir;

			// Register for process monitoring
			const processId = `jupyter-${envName}`;
			await invoke("register_process_monitoring", { processId });

			const result = await invoke<JupyterStatus>("start_jupyter_server", {
				environment: envName,
				directory: installDir,
				working: workDir,
			});

			if (result?.url) {
				jupyterUrlRef.current[envName] = result.url;
				setJupyterStatus((prev) => ({ ...prev, [envName]: "running" }));
				activeServers.current.add(envName);

				// Open URL in browser window
				openJupyterWindow(`${result.url}?token=launcher`);
			} else {
				throw new Error("Failed to get Jupyter URL");
			}
		} catch (err) {
			setJupyterStatus((prev) => ({ ...prev, [envName]: "error" }));
			jupyterUrlRef.current[envName] = null;
			alert(`Failed to start Jupyter: ${err}`);
		}
	};

	// Stop Jupyter server
	const stopJupyterServer = async (envName: string) => {
		if (jupyterStatus[envName] !== "running") return;

		try {
			setJupyterStatus((prev) => ({ ...prev, [envName]: "stopping" }));
			await invoke("stop_jupyter_server", { environment: envName });
		} catch (err) {
			try {
				const status = await invoke<JupyterStatus>("check_jupyter_server", {
					environment: envName,
				});

				if (!status.running) {
					setJupyterStatus((prev) => ({ ...prev, [envName]: "stopped" }));
					jupyterUrlRef.current[envName] = null;
					activeServers.current.delete(envName);
				} else {
					setJupyterStatus((prev) => ({ ...prev, [envName]: "running" }));
					alert(`Failed to stop Jupyter server: ${err}`);
				}
			} catch {
				setJupyterStatus((prev) => ({ ...prev, [envName]: "stopped" }));
			}
		}
	};

	// Open Jupyter window
	const openJupyterWindow = async (url: string) => {
		try {
			await invoke("open_url_in_window", { url });
		} catch (err) {
			alert(`Failed to open Jupyter Lab window. Server is running at ${url} -> ${err}`);
		}
	};

	// Function to open Jupyter logs in a new window
	const viewJupyterLogs = async (envName: string) => {
		try {
			// pass the environment parameter
			await invoke("open_jupyter_logs_window", {
				environment: envName,
			});
		} catch (err) {
			alert(`Failed to open logs window: ${err}`);
		}
	};

	useEffect(() => {
		if (environments.length > 0 && installDir) {
			try {
				const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
				if (cachedData) {
					const cache = JSON.parse(cachedData);

					// Process each environment with cached data
					// biome-ignore lint/complexity/noForEach: <explanation>
					environments.forEach((env) => {
						if (cache?.[env.name]?.extensions) {
							// Update the environmentPackages state from cache
							const packageSet = new Set<string>(
								cache[env.name].extensions.map((ext: Extension) =>
									ext.package.toLowerCase(),
								),
							);
							setEnvironmentPackages((prev) => ({
								...prev,
								[env.name]: packageSet,
							}));
						}
					});
				}
			} catch (error) {
				console.error(
					"Error loading cached extensions on initial mount:",
					error,
				);
			}
		}
	}, [environments, installDir]);

	// Register for Jupyter process monitoring directly in the main window
	useEffect(() => {
		// Only proceed if we have environments to monitor
		if (!environments.length) return;

		// Set up monitoring for each environment's Jupyter process
		const unsubscribes = environments.map((env) => {
			const processId = `jupyter-${env.name}`;

			// Register for direct process monitoring
			invoke("register_process_monitoring", { processId })
				.then(() =>
					console.log(
						`Main window: Process ${processId} registered for monitoring`,
					),
				)
				.catch((err) =>
					console.error(`Failed to register process monitoring: ${err}`),
				);

			// Listen for process output events directly
			return listen<{ processId: string; output: string; timestamp: number }>(
				"process-output",
				(event) => {
					const { processId: eventProcessId, output } = event.payload;

					if (
						eventProcessId === processId &&
						output.includes("Shutting down on /api/shutdown request")
					) {
						// Update the Jupyter status
						setJupyterStatus((prev) => {
							if (prev[env.name] === "running") {
								return { ...prev, [env.name]: "stopped" };
							}
							return prev;
						});

						// Also notify the backend to clear port information
						invoke("stop_jupyter_server", { environment: env.name }).catch(
							(err) =>
								console.error(
									`Failed to clear server info for ${env.name}:`,
									err,
								),
						);

						// Remove the environment from active servers
						activeServers.current.delete(env.name);
					}
				},
			);
		});

		// Clean up listeners when component unmounts
		return () => {
			Promise.all(unsubscribes.map((unsub) => unsub.then((fn) => fn()))).catch(
				(err) => console.error("Error unsubscribing from process events:", err),
			);
		};
	}, [environments]);

	// Also keep the storage event listener as a fallback
	useEffect(() => {
		const handleMessage = (event: MessageEvent) => {
			// Verify the message is from our logs window
			if (event.data && event.data.type === "jupyter-status-update") {
				const { environmentName, status } = event.data;

				// Update the Jupyter status for this environment
				if (environmentName && status === "stopped") {
					setJupyterStatus((prev) => ({
						...prev,
						[environmentName]: "stopped",
					}));
					jupyterUrlRef.current[environmentName] = null;
					activeServers.current.delete(environmentName);
				}
			}
		};

		// Handle storage events for cross-window communication
		const handleStorage = (event: StorageEvent) => {
			// Check if this is a Jupyter shutdown event
			if (event.key && event.key.startsWith("jupyter-shutdown-")) {
				const environmentName = event.key.replace("jupyter-shutdown-", "");

				// Update the state
				setJupyterStatus((prev) => {
					if (prev[environmentName] === "running") {
						return { ...prev, [environmentName]: "stopped" };
					}
					return prev;
				});

				jupyterUrlRef.current[environmentName] = null;
				activeServers.current.delete(environmentName);

				// Delete the shutdown event from localStorage immediately after it's processed
				localStorage.removeItem(event.key);
			}
		};

		// Add event listeners
		window.addEventListener("message", handleMessage);
		window.addEventListener("storage", handleStorage);

		// Check for any existing shutdown events that might have happened before this component mounted
		for (const env of environments) {
			const shutdownKey = `jupyter-shutdown-${env.name}`;
			const shutdownTime = localStorage.getItem(shutdownKey);

			if (shutdownTime) {
				// Only process if this is a recent shutdown (within last 60 seconds)
				const timestamp = Number.parseInt(shutdownTime, 10);
				const now = Date.now();

				if (now - timestamp < 60000) {
					// 60 seconds
					setJupyterStatus((prev) => {
						if (prev[env.name] === "running") {
							return { ...prev, [env.name]: "stopped" };
						}
						return prev;
					});

					jupyterUrlRef.current[env.name] = null;
					activeServers.current.delete(env.name);
				}

				// Clean up the item after processing - regardless of whether it was recent or not
				localStorage.removeItem(shutdownKey);
			}
		}

		// Clean up
		return () => {
			window.removeEventListener("message", handleMessage);
			window.removeEventListener("storage", handleStorage);
		};
	}, [environments]);
	const [activeTab, setActiveTab] = useState<"manage" | "add">("manage");

	// Filter out environments marked for deletion
	useEffect(() => {
		// If there are any environments in process of being deleted, filter them out
		if (environments.length > 0 && deletedEnvironments.current.size > 0) {
			const filteredEnvs = environments.filter(
				env => !deletedEnvironments.current.has(env.name)
			);

			// Only update if there's actually a change
			if (filteredEnvs.length !== environments.length) {
				setEnvironments(filteredEnvs);
			}
		}
	}, [environments]);

	const [showExtensionsForEnv, setShowExtensionsForEnv] = useState<string | null>(null);

	// Validate the new environment name with debounce
	useEffect(() => {
		const timeoutId = setTimeout(() => {
			setNewEnvNameInvalid(newEnvName.trim() !== "" && !/^[a-z0-9-]+$/.test(newEnvName));
		}, 300);

		return () => clearTimeout(timeoutId);
	}, [newEnvName]);

	// Store the createEnvironment function in a ref
	useEffect(() => {
		createEnvironmentRef.current = createEnvironment;
	});

	// wrapper function
	const safeCreateEnvironment = useCallback((exts: string[] = []) => {
		if (envCreatedRef.current) return;
		envCreatedRef.current = true;
		createEnvironmentRef.current?.(exts);
	}, []);

	useEffect(() => {
		if (!isCreateModalOpen && creationWarningRef.current) {
			setCreationWarning(creationWarningRef.current);
			creationWarningRef.current = null;
		}
	}, [isCreateModalOpen]);

	// Check for scrollbar when content changes
	useEffect(() => {
		const checkScrollbar = () => {
			const container = scrollContainerRef.current;
			if (container) {
				const hasVerticalScrollbar = container.scrollHeight > container.clientHeight;
				setHasScrollbar(hasVerticalScrollbar);
			}
		};

		checkScrollbar();

		// Use ResizeObserver to detect changes in content size
		const container = scrollContainerRef.current;
		if (container) {
			const resizeObserver = new ResizeObserver(checkScrollbar);
			resizeObserver.observe(container);

			return () => resizeObserver.disconnect();
		}
	}, [filteredEnvironments]);

	// Close extensions panel on Escape key
	useEffect(() => {
		const handleEscapeKey = (e: KeyboardEvent) => {
			if (e.key === "Escape") {
				if (showExtensionsForEnv) {
					setShowExtensionsForEnv(null);
					setActiveTab("manage");
					setExtensionSearchQuery("");
				}
			}
		};

		document.addEventListener("keydown", handleEscapeKey);
		return () => document.removeEventListener("keydown", handleEscapeKey);
	}, [showExtensionsForEnv]);

	return (
		<div className="w-full h-full">
			<div className="flex flex-col">
				<div className="w-full mt-7">
					{/* Add Current Working Directory Section */}
					<div className="bg-theme-secondary mb-5">
						<div className="flex flex-col w-full">
							<div className="flex items-center">
							<label
								htmlFor="current-working-dir"
								className="body-sm-regular text-theme-secondary whitespace-nowrap"
							>
								Current Working Directory:
							</label>
								<div className="flex-1 bg-theme-secondary rounded-md ml-2 body-xs-regular">
									<input
									type="text"
									id="current-working-dir"
									value={workingDirInput}
									onChange={(e) => setWorkingDirInput(e.target.value)}
									onKeyDown={handleDirectoryInputKeyPress}
									onBlur={handleDirectoryInputSubmit}
									placeholder="Enter directory path or select a folder..."
									className={`directory-input w-full py-2 rounded border cursor-text body-xs-regular ${
										!workingDirValid ? "border-red-500" : "border-theme-outline"
									} text-theme-secondary placeholder-muted shadow-sm`}
									/>
								</div>
								<Tooltip
									content="Browse for directory."
									className="tooltip-theme"
								>
									<Button
									onClick={selectWorkingDirectory}
									variant="ghost"
									size="icon"
									className="button-ghost"
									type="button"
									>
									<FolderIcon className="h-5 w-5 ml-4 mr-1.5" />
									</Button>
								</Tooltip>
							</div>
							{!workingDirValid && workingDirInput.trim() && (
							<p className="text-red-500 text-xs mt-1">
								Directory does not exist or is not accessible.
							</p>
							)}
							{workingDirValid && workingDirInput.trim() && workingDirInput !== currentWorkingDir && (
							<p className="text-theme-muted text-xs mt-1">
								Press Enter or click outside to apply changes.
							</p>
							)}
						</div>
					</div>
					<div className="pb-5 flex justify-between items-center">
						{environments.length > 0 && (
							<div className="w-[250px] shrink-0">
								<div className="relative body-xs-regular">
									<input
										type="text"
										placeholder="Search Environments..."
										value={searchQuery}
										spellCheck={false}
										onChange={(e) => setSearchQuery(e.target.value)}
										className="border border-theme body-xs-regular !pl-6 shadow-sm w-full"
									/>
									{searchQuery ? (
										<Tooltip
											content="Clear search query"
											className="tooltip tooltip-theme"
										>
											<button
												type="button"
												onClick={() => setSearchQuery("")}
												className="absolute left-1 top-1/2 -translate-y-1/2 text-theme-muted"
											>
												<CustomIcon id="close" className="h-4 w-4" />
											</button>
										</Tooltip>
									) : (
										<span className="absolute left-1 top-1/2 -translate-y-1/2 text-theme-muted">
											<CustomIcon id="search" className="h-4 w-4 ml-0.5" />
										</span>
									)}
								</div>
							</div>
						)}

						{/* RIGHT SIDE: Action Buttons */}
						{environments.length > 0 && (
							<EnvironmentActionButtons
								showCreateEnvironment={showCreateEnvironment}
								handleRequirementsFileSelect={handleRequirementsFileSelect}
							/>
						)}
					</div>

					{creationWarning && (
						<div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
							<div className="bg-theme-secondary border border-yellow-400/25 rounded-lg shadow-md max-w-2xl w-full pt-6 px-5 pb-4">
								<h2 className="text-yellow-300 body-lg-bold mb-2">Creation Warning</h2>
								<div className="mb-4 mt-4 pl-5 pt-1 pr-1 pb-1 border border-yellow-800 bg-yellow-900/30 text-yellow-300 rounded-md text-xs font-mono">
									<div className="whitespace-pre-wrap overflow-auto max-h-60 mt-0.5 mb-0.5">
										{creationWarning}
									</div>
								</div>
								<div className="flex justify-end">
									<Button
										onClick={() => setCreationWarning(null)}
										variant="outline"
										size="sm"
										className="button-outline px-2 py-1"
									>
										Dismiss
									</Button>
								</div>
							</div>
						</div>
					)}

					{environmentsError && (
						<div className="m-2 p-3 border-theme-accent border-red-500 rounded-lg">
							<p className="body-xs-regular mt-1 text-theme">{environmentsError}</p>
							<Button
								onClick={() => {
									setEnvironmentsError(null);
									if (installDir) {
										invoke<Environment[]>("list_conda_environments", { directory: installDir })
											.then((envs) => {
												const filteredEnvs = envs.filter(
													(env) =>
														env.name.toLowerCase() !== "base" &&
														!deletedEnvironments.current.has(env.name)
												);
												setEnvironments(filteredEnvs);
											})
											.catch((err) => {
												setEnvironmentsError(`Failed to load environments: ${err}`);
											});
									}
								}}
								variant="outline"
								size="sm"
								className="button-secondary"
							>
								<span className="body-xs-medium">Retry</span>
							</Button>
						</div>
					)}

					{environmentsLoading && installDir ? (
						<div className="flex flex-col items-center justify-center p-4">
							<div className="flex items-center space-x-2">
								<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
								<span className="body-xs-regular text-theme-primary">
									Loading environments...
								</span>
							</div>
						</div>
					) : (
						<div className="flex-1 flex flex-col min-h-0 overflow-y-auto">
							<div
								ref={scrollContainerRef}
								className={`flex-1 ${hasScrollbar ? 'pr-3' : ''}`}
								style={{ maxHeight: 'calc(100vh - 18rem)' }}
							>
								<div>


									<ul className="space-y-3">
										{filteredEnvironments.map((env) => (
											<li
												key={env.name}
												className="w-full"
											>

												<div className={`bg-theme-tertiary border border-theme-modal rounded-md relative w-full pl-2 pt-3 pb-3 mb-5 shadow-md group ${
													isUpdatingEnvironment.has(env.name) ? 'pointer-events-none' : ''
												}`}>
													<div className="flex justify-between items-center">
														{/* LEFT: Clickable area for extensions modal */}
														<div
															className="flex items-center"
														>
															<span className="body-lg-bold text-theme whitespace-nowrap mr-3 ml-2">{env.name}</span>
															<span className="body-xs-medium text-theme-primary text-nowrap px-2 py-1 rounded-xl bg-theme-tag shadow-md mr-3">
																Python {env.pythonVersion}
															</span>
														</div>

														{/* RIGHT: Action buttons */}
														<div className="flex items-center gap-2 pr-2">
															<div className="flex flex-row items-center gap-2">
																<Tooltip
																	content="Update all added extensions."
																	className="tooltip-theme"
																>
																	<Button
																		onClick={(e) => { e.stopPropagation(); updateEnvironment(env.name); }}
																		disabled={isUpdatingEnvironment.has(env.name)}
																		variant="ghost"
																		size="icon"
																		className={`button-ghost transition-opacity duration-0 ${isUpdatingEnvironment.has(env.name) ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}
																		aria-label="Update Environment"
																	>
																		{isUpdatingEnvironment.has(env.name) ? (
																			<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
																		) : (
																			<CustomIcon id="refresh" className="h-4 w-4" />
																		)}
																	</Button>
																</Tooltip>
																<Tooltip content="Remove Environment" className="tooltip-theme">
																	<Button
																		onClick={(e) => {
																			e.stopPropagation();
																			setEnvironmentToRemove(env.name);
																			setShowEnvironmentRemoveConfirmation(true);
																		}}
																		variant="ghost"
																		size="icon"
																		className="button-ghost opacity-0 group-hover:opacity-100 transition-opacity duration-0"
																		disabled={isUpdatingEnvironment.has(env.name)}
																		aria-label="Remove Environment"
																	>
																		<CustomIcon id="bin" className="h-4 w-4" />
																	</Button>
																</Tooltip>
															</div>
															<div className="flex flex-row items-center justify-end gap-2 mr-1">
																{jupyterStatus[env.name] === "running" && (
																	<>
																		<Tooltip content="Stop Jupyter Server" className="tooltip-theme">
																			<Button
																				onClick={(e) => { e.preventDefault(); e.stopPropagation(); stopJupyterServer(env.name); }}
																				variant="danger"
																				size="xs"
																				className="button-danger text-nowrap px-2 py-1 h-6"
																				aria-label="Stop Jupyter Server"
																			>
																				Stop Jupyter
																			</Button>
																		</Tooltip>
																	</>
																)}
																{hasJupyterSupport(env.name) && (
																	<Tooltip content="View Jupyter Server Logs" className="tooltip-theme">
																		<Button
																			onClick={(e) => { e.preventDefault(); e.stopPropagation(); viewJupyterLogs(env.name); }}
																			variant="outline"
																			size="xs"
																			className="px-2 py-1 shadow-sm button-outline"
																			aria-label="View Jupyter Server Logs"
																		>
																			Logs
																		</Button>
																	</Tooltip>
																)}
																<EnvironmentActions
																	env={env}
																	isUpdatingEnvironment={isUpdatingEnvironment.has(env.name)}
																	installDir={installDir}
																	hasCliSupport={hasCliSupport}
																	hasIPythonSupport={hasIPythonSupport}
																	hasJupyterSupport={hasJupyterSupport}
																	jupyterStatus={jupyterStatus[env.name]}
																	openSystemTerminal={openSystemTerminal}
																	startCliSession={startCliSession}
																	startPythonSession={startPythonSession}
																	startIPythonSession={startIPythonSession}
																	startJupyterLab={startJupyterLab}
																	openJupyterWindow={openJupyterWindow}
																	jupyterUrl={jupyterUrlRef.current[env.name]}
																/>
																<Tooltip content="Manage environment extensions." className="tooltip-theme">
																	<Button
																		onClick={(e) => { e.stopPropagation(); showExtensions(env.name); }}
																		variant="secondary"
																		size="xs"
																		className="button-secondary px-2 py-1 shadow-sm"
																		aria-label="Manage Extensions"
																	>
																		Extensions
																	</Button>
																</Tooltip>
															</div>
														</div>
													</div>
													{/* Extensions Panel - Nested within environment container */}
													{showExtensionsForEnv === env.name && (
														<div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
															<div className="bg-theme-secondary border border-theme-modal rounded-lg shadow-lg max-w-[90vw] max-h-[90vh] min-w-[60vw] px-3 pt-4">
																{/* Modal Header */}
																<div className="flex items-center justify-between mb-4">
																	<h2 className="body-lg-bold text-theme-primary">
																		Manage Extensions - {env.name}
																	</h2>
																	<Tooltip content="Close extensions panel" className="tooltip-theme">
																		<Button
																			onClick={() => {
																				setShowExtensionsForEnv(null);
																				setActiveTab("manage");
																				setExtensionSearchQuery("");
																			}}
																			onKeyDown={(e) => {
																				if (e.key === "Escape") {
																					setShowExtensionsForEnv(null);
																					setActiveTab("manage");
																					setExtensionSearchQuery("");
																				}
																			}}
																			variant="ghost"
																			size="icon"
																			className="button-ghost"
																		>
																			<CustomIcon id="close" className="h-6 w-6" />
																		</Button>
																	</Tooltip>
																</div>

																{/* Modal Content - Scrollable */}
																<div className="flex-1 overflow-y-auto flex">
																	{activeTab === "add" ? (
																		<div>
																			<AddExtensionSelector
																				key={extensionSelectorKey}
																				onInstallExtensions={handleInstallExtensions}
																				installedPackages={environmentPackages[env.name] || new Set()}
																				onCancel={() => setActiveTab("manage")}
																			/>
																		</div>
																	) : (
																		<div className="w-full">
																			{/* Search and Add Section */}
																			<div className="flex items-center mb-5 gap-2">
																				<div className="flex-1 relative">
																					<span className="absolute inset-y-0 left-0 flex items-center pl-2 text-theme-muted">
																						<CustomIcon id="search" className="h-4 w-4" />
																					</span>
																					<input
																						id="extension-search"
																						type="text"
																						placeholder="Search Extensions..."
																						value={extensionSearchQuery}
																						onChange={(e) => setExtensionSearchQuery(e.target.value)}
																						className="!pl-[30px]"
																						disabled={!env.name || extensionsLoading}
																					/>
																				</div>
																				<Tooltip content="Install additional packages in the environment." className="tooltip-theme">
																					<Button
																						onClick={() => setActiveTab("add")}
																						variant="primary"
																						size="xs"
																						className="button-primary shadow-s px-2 py-1"
																					>
																						Add Extension
																					</Button>
																				</Tooltip>
																			</div>

																			{extensionsLoading ? (
																				<div className="flex justify-center py-6">
																					<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
																				</div>
																			) : extensionsError ? (
																				<div className="p-3 bg-theme-secondary border border-red-500 rounded-md">
																					<p className="text-theme-secondary mt-1 mb-2 text-sm whitespace-pre-wrap overflow-auto max-h-[calc(100vh-10rem)]">
																						{extensionsError}
																					</p>
																					<div className="flex justify-between mt-3">
																						<Button
																							onClick={() => setExtensionsError(null)}
																							variant="outline"
																							size="sm"
																							className="button-outline"
																						>
																							<span className="body-xs-medium">Dismiss</span>
																						</Button>
																						<Button
																							onClick={() => {
																								setExtensionsError(null);
																								if (env.name) {
																									setExtensionsLoading(true);
																									invoke<{ extensions: Extension[] }>("get_environment_extensions", { name: env.name })
																										.then((result) => {
																											if (result?.extensions) {
																												setExtensions(result.extensions);
																												// Update cache
																												const cachedData = localStorage.getItem(ENV_EXTENSIONS_CACHE_KEY);
																												const cache = cachedData ? JSON.parse(cachedData) : {};
																												cache[env.name] = result.extensions;
																												localStorage.setItem(ENV_EXTENSIONS_CACHE_KEY, JSON.stringify(cache));
																											}
																										})
																										.catch((err) => setExtensionsError(`Failed to refresh: ${err}`))
																										.finally(() => setExtensionsLoading(false));
																								}
																							}}
																							variant="primary"
																							size="sm"
																							className="button-primary"
																						>
																							<span className="body-xs-medium text-theme">Retry</span>
																						</Button>
																					</div>
																				</div>
																			) : extensionRemoveError ? (
																				<div className="p-3 bg-red-900/30 text-red-300 rounded-md mb-4">
																					<p className="text-theme-secondary text-xs mt-1 mb-2">{extensionRemoveError}</p>
																					<Button
																						onClick={() => setExtensionRemoveError(null)}
																						variant="outline"
																						size="sm"
																						className="button-outline"
																					>
																						<span className="body-xs-medium">Dismiss</span>
																					</Button>
																				</div>
																			) : updateExtensionError ? (
																				<div className="p-3 bg-red-900/30 text-red-300 rounded-md mb-4">
																					<p className="text-theme-secondary text-xs mt-1 mb-2">{updateExtensionError}</p>
																					<Button
																						onClick={() => setUpdateExtensionError(null)}
																						variant="outline"
																						size="sm"
																						className="button-outline"
																					>
																						<span className="body-xs-medium">Dismiss</span>
																					</Button>
																				</div>
																			) : (
																				<div className="pl-0 pr-3 mb-3 w-full">
																					{(() => {
																						const filteredExtensions = getFilteredExtensions();
																						return filteredExtensions.length > 0 ? (
																							<div className="max-h-[60vh] overflow-y-auto -mr-2 pr-2">
																								{filteredExtensions.map((ext) => (
																									<ExtensionRow
																										key={ext.package}
																										ext={ext}
																										updatingExtension={updatingExtension}
																										installExtensionsLoading={installExtensionsLoading}
																										handleUpdateExtension={handleUpdateExtension}
																										setExtensionToRemove={setExtensionToRemove}
																										setShowRemoveConfirmation={setShowRemoveConfirmation}
																									/>
																								))}
																							</div>
																						) : extensions.length > 0 ? (
																							<div className="text-center p-6">
																								<p className="body-xs-regular text-theme-primary mt-1">
																									No extensions match your search
																								</p>
																							</div>
																						) : (
																							<div className="text-center p-6">
																								<p className="body-xs-regular text-theme-primary mt-1">
																									No extensions installed. Click "Add Extensions" to get started.
																								</p>
																							</div>
																						);
																					})()}
																				</div>
																			)}
																		</div>
																	)}
																</div>
															</div>
														</div>
													)}
												</div>
											</li>
										))}
									{filteredEnvironments.length === 0 && !environmentsError && !environmentsLoading && (
										<div className="flex flex-col items-center justify-center">
											<div className="text-center">
												<CustomIcon
													id="search"
													className="h-12 w-12 text-theme-muted mb-2 mx-auto"
												/>
												<h3 className="body-md-bold text-theme-secondary mb-2">
													No environments found
												</h3>
												<p className="body-sm-regular text-theme-muted mb-4">
													No environments match your search for "{searchQuery}"
												</p>
												<Button
													onClick={() => setSearchQuery("")}
													variant="outline"
													size="sm"
													className="button-outline"
												>
													<span className="body-xs-medium">Clear Search</span>
												</Button>
											</div>
										</div>
									)}
									</ul>
								</div>
							</div>

							{updateEnvironmentError && (
								<div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
									<div className="bg-theme-secondary border border-red-800 rounded-lg shadow-md max-w-2xl w-full p-6">
										<h2 className="text-red-600 text-lg font-bold mb-2">Update Environment Error</h2>
										<div className="mb-4 mt-4 pl-5 pt-1 pr-1 pb-1 border border-red-800 bg-red-900/30 text-red-300 rounded-md text-xs font-mono">
											<div className="whitespace-pre-wrap overflow-auto max-h-60 mt-0.5 mb-0.5">
												{extractStderr(updateEnvironmentError)}
											</div>
										</div>
										<div className="flex justify-end">
											<Button
												onClick={() => setUpdateEnvironmentError(null)}
												variant="outline"
												size="sm"
												className="button-outline"
											>
												<span className="body-xs-medium">Dismiss</span>
											</Button>
										</div>
									</div>
								</div>
							)}

							{removeEnvironmentError && (
								<div className="m-2 p-3 bg-theme-primary border-red-500 rounded-md">
									<p className="text-theme-primary body-xs-regular mt-1">{removeEnvironmentError}</p>
									<Button
										onClick={() => setRemoveEnvironmentError(null)}
										variant="outline"
										size="sm"
										className="button-outline"
									>
										<span className="body-xs-medium">Dismiss</span>
									</Button>
								</div>
							)}
						</div>
					)}
				</div>
				{/* Remove Extension Confirmation Modal */}
				{showRemoveConfirmation && extensionToRemove && (
					<div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center">
						<div className="bg-theme-secondary border border-theme-modal rounded-lg shadow-lg w-[400px] pl-4 pr-2 pt-2 pb-5">
							<div className="flex items-center justify-between mb-4">
								<h2 className="body-md-bold text-theme">
									Delete Extension
								</h2>
								<Button
									variant="ghost"
									onClick={() => {
										setShowRemoveConfirmation(false);
										setExtensionToRemove(null);
									}}
									className="button-ghost"
									size="sm"
									disabled={isRemovingExtension}
								>
									<CustomIcon id="close" className="h-6 w-6" />
								</Button>
							</div>
							<p className="mt-3 mb-7 body-sm-regular text-theme">
								Are you sure you want to remove{" "}
								<span className="font-bold">
									{extensionToRemove.install_method === "conda"
										? extensionToRemove.package.split(":")[1]
										: extensionToRemove.package}
								</span>{" "}
								from <span className="font-bold">{activeEnv}</span>?
							</p>
							<div className="flex justify-center">
								<Button
									variant="danger"
									className="button-danger"
									onClick={async () => {
										if (extensionToRemove && activeEnv) {
											await handleRemoveExtension(extensionToRemove, activeEnv);
											setShowRemoveConfirmation(false);
											setExtensionToRemove(null);
										}
									}}
									size="sm"
									disabled={isRemovingExtension}
								>
									{isRemovingExtension ? (
										<div className="flex items-center">
											<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-theme-contrast mr-2" />
											<span className="body-xs-medium">Removing...</span>
										</div>
									) : (
										<span className="body-xs-medium">Remove Extension</span>
									)}
								</Button>
							</div>
						</div>
					</div>
				)}

				{showEnvironmentRemoveConfirmation && environmentToRemove && (
					<div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
						<div className="bg-theme-secondary border border-theme-modal rounded-lg shadow-lg max-w-[75vw] p-5">
							<div className="flex items-center justify-between mb-7">
								<h2 className="body-lg-bold text-theme-primary">
									Delete Environment
								</h2>
								<Button
									onClick={() => {
										setShowEnvironmentRemoveConfirmation(false);
										setEnvironmentToRemove(null);
									}}
									variant="ghost"
									size="icon"
									className="button-ghost"
								>
									<CustomIcon id="close" className="h-6 w-6" />
								</Button>
							</div>
							<p className="mb-2 body-md-medium text-theme-primary flex justify-start">
								Are you sure you want to remove, {environmentToRemove}?
							</p>
							<p className="mb-7 body-md-medium text-theme-primary flex justify-start">
								This action cannot be undone.
							</p>
							<div className="flex justify-end gap-2">
								<Button
									variant="outline"
									onClick={() => {
										setShowEnvironmentRemoveConfirmation(false);
										setEnvironmentToRemove(null);
										setIsRemoving(false);
										setRemoveEnvironmentError(null);
									}}
									className="button-outline px-2 py-1"
									size="sm"
								>
									<span className="body-xs-medium">Cancel</span>
								</Button>
								<Button
									variant="danger"
									className="button-danger px-2 py-1"
									onClick={() => {
										if (environmentToRemove) {
											setIsRemoving(true);
											setRemoveEnvironmentError(null);
											setShowEnvironmentRemoveConfirmation(false);
											setEnvironmentToRemove(null);
											removeEnvironment(environmentToRemove);
										}
									}}
									disabled={isRemoving}
									size="sm"
								>
									{isRemoving ? (
										<div className="flex items-center">
											<div className="bg-theme-primary border border-theme-accent rounded-lg shadow-dark-2 w-full max-w-md p-5">
												<div className="animate-spin h-4 w-4 border-b-2 border-theme rounded-full mr-2" />
												<span className="body-xs-medium">Removing...</span>
											</div>
										</div>
									) : (
										<span className="body-xs-medium">Delete</span>
									)}
								</Button>
							</div>
						</div>
					</div>
				)}

				{/* Add blocking overlay when removing environment */}
				{isRemoving && (
					<div className="fixed inset-0 z-[9999] bg-black/90 flex items-center justify-center cursor-not-allowed">
						<div className="bg-theme-secondary border border-theme-modal rounded-lg shadow-md p-8 max-w-xs w-full flex flex-col items-center">
							<div className="flex flex-col items-center">
								<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-theme-accent mb-4" />
								<span className="body-md-bold text-theme-primary mb-2">Removing environment...</span>
								{removeEnvironmentError && (
									<div className="w-full p-3 bg-red-900/30 text-red-300 rounded-md mt-4">
										<h4 className="text-sm font-medium text-theme mb-2">Removal Error</h4>
										<div className="mt-1 bg-red-900/20 p-2 rounded overflow-auto max-h-32 text-xs font-mono whitespace-pre-wrap text-red-200">
											{extractStderr(removeEnvironmentError)}
										</div>
									</div>
								)}
							</div>
						</div>
					</div>
				)}
			</div>
			{/* Requirements File Modal */}
			{creatingFromRequirements && (
				<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90">
					<div className="flex flex-col p-6 bg-theme-secondary rounded-lg border border-theme-modal shadow-lg max-w-[90vw] w-full max-h-[90vh]">
						<div className="flex items-center justify-between mb-4">
							<p className="body-lg-bold text-theme-primary">
								Create Environment from {requirementsFileName}
							</p>
							<Tooltip
								content="Cancel and go back."
								className="tooltip-theme"
							>
								<Button
									className={`button-ghost ${creationLoading ? 'opacity-0 cursor-not-allowed' : ''}`}
									onClick={() => {
										setCreatingFromRequirements(false);
										setRequirementsFileName(null);
										setRequirementsEnvName("");
										setRequirementsError(null);
										setRequirementsLogs([]);
										setRequirementsComplete(false);
										setRequirementsWarning(null);
									}}
									variant="ghost"
									size="icon"
									disabled={creationLoading}
								>
									<CustomIcon id="close" className="h-7 w-7" />
								</Button>
							</Tooltip>
						</div>

						<div className="flex flex-col flex-1 overflow-y-auto pr-2">
						{requirementsError && (
							<div className="mb-4 p-3 bg-red-900/30 text-red-300 rounded-md">
								<p className="text-theme-secondary mt-1 mb-2 font-mono whitespace-pre-wrap overflow-auto max-h-[60px]">
									{extractStderr(requirementsError)}
								</p>
							</div>
						)}

						{requirementsWarning && (
							<div className="mb-4 p-3 bg-yellow-900/30 text-yellow-300 rounded-md">
								<p className="text-theme-secondary mt-1 mb-2 font-mono whitespace-pre-wrap overflow-auto max-h-60">
									{extractStderr(requirementsWarning)}
								</p>
							</div>
						)}

						{creationLoading ? (
							<div className="flex flex-col items-center justify-center">
								<div className="flex justify-center mb-1">
									<div className="animate-spin rounded-full h-5 w-5 border-b-2 border-theme-accent" />
								</div>
								<p className="text-theme-muted body-sm-regular mt-1 text-center mb-4">
									Creating environment from requirements file...
								</p>
								{/* Log viewer */}
								{requirementsLogs.length > 0 && (
									<div className="w-full p-2 border border-theme-accent rounded-md bg-theme-secondary mb-4">
										<pre className="body-xs-regular text-theme-secondary whitespace-pre-wrap overflow-auto max-h-[50vh]">
											{requirementsLogs.join("\n")}
										</pre>
									</div>
								)}
								<div className="flex justify-center w-full">
									<Button
										onClick={() => handleAbortInstallation("requirements")}
										variant="danger"
										className="button-danger"
										disabled={isCancellingCreation}
										size="sm"
									>
										{isCancellingCreation ? (
											<span className="flex items-center">
												<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-theme-contrast mr-2" />
												Cleanup will continue in the background...
											</span>
										) : (
											<span className="body-xs-bold text-theme">Cancel Installation</span>
										)}
									</Button>
								</div>
							</div>
						) : requirementsComplete ? (
							<div>
								{requirementsLogs.length > 0 && (
									<div className="w-full p-2 border border-theme-accent rounded-md bg-theme-secondary">
										<pre className="text-xs text-theme-secondary whitespace-pre-wrap overflow-auto max-h-[50vh]">
											{requirementsLogs.join("\n")}
										</pre>
									</div>
								)}
								<div className="flex justify-center mt-6">
									<Button
										onClick={() => {
											setCreatingFromRequirements(false);
											setRequirementsFileName(null);
											setRequirementsEnvName("");
											setRequirementsError(null);
											setRequirementsLogs([]);
											setRequirementsComplete(false);
											setRequirementsWarning(null);
										}}
										variant="primary"
										className="button-primary px-2 py-1"
										size="sm"
									>
										Done
									</Button>
								</div>
							</div>
						) : (
							<div className="flex flex-col h-full">
								<div className="flex-1">
									<div className="mb-2">
										<label
											htmlFor="requirements-env-name"
											className="text-theme-secondary body-md-bold"
										>
											Environment Name
										</label>
										<input
											type="text"
											id="requirements-env-name"
											value={requirementsEnvName}
											onChange={(e) => setRequirementsEnvName(e.target.value)}
											placeholder="my-environment"
											spellCheck="false"
											className={`w-full p-2 border rounded-md bg-theme-secondary text-theme-primary mt-2 ${
												requirementsEnvName.trim() !== "" && !/^[a-z0-9-]+$/.test(requirementsEnvName)
													? "border-red-500 focus:border-red-500"
													: "border-theme"
											}`}
										/>
										<p className={`text-xs mt-1 ml-1 ${
											requirementsEnvName.trim() !== "" && !/^[a-z0-9-]+$/.test(requirementsEnvName)
												? "text-red-500"
												: "text-theme-muted"
											}`}>
											Use lowercase letters, numbers, and hyphens. No spaces.
										</p>
									</div>
								</div>
								<div className="flex justify-end mt-2 items-center">
									<Button
										onClick={createEnvironmentFromRequirements}
										variant="primary"
										disabled={
											!/^[a-z0-9-]+$/.test(requirementsEnvName) ||
											!requirementsEnvName.trim()
										}
										className="button-primary px-2 py-1"
										size="sm"
									>
										Create Environment
									</Button>
								</div>
							</div>
						)}
						</div>
					</div>
				</div>
			)}
			{/* Create Environment Modal - Fullscreen & Scrollable */}
			{isCreateModalOpen && (
				<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
					<div className="flex flex-col pl-3 pr-2 pt-3 pb-2 bg-theme-secondary rounded-lg border border-theme-modal shadow-md max-w-[90vw] max-h-[90vh]">
						<div className="flex items-center justify-between mb-3">
							{(createStep === "name") && (
								<div>
									<p className="text-theme-secondary body-sm-medium">
										STEP <span className="text-theme-accent">1</span> OF <span className="text-theme-accent">3</span>
									</p>
								</div>
							)}
							{(createStep === "python") && (
								<div>
									<p className="text-theme-secondary body-sm-medium">
										STEP <span className="text-theme-accent">2</span> OF <span className="text-theme-accent">3</span>
									</p>
								</div>
							)}
							{createStep !== "extensions" && (
								<div className="flex items-center justify-end mr-2">
									<Tooltip
										content="Cancel and go back."
										className="tooltip-theme"
									>
										<Button
											className="button-ghost"
											onClick={() => setIsCreateModalOpen(false)}
											variant="ghost"
											size="icon"
											disabled={creationLoading}
										>
											<CustomIcon id="close" className="h-6 w-6" />
										</Button>
									</Tooltip>
								</div>
							)}
						</div>

						<div className="flex-grow overflow-y-auto mb-2 pr-1">
							{/* Name input step */}
							{createStep === "name" && (
							<div>
								<div className="px-1">
									<p className="body-md-bold text-theme-secondary mb-2">
										Environment Name
									</p>
									<input
										type="text"
										id="env-name-modal"
										value={newEnvName}
										onChange={(e) => setNewEnvName(e.target.value)}
										placeholder="my-environment"
										spellCheck="false"
										className={`w-full p-2 text-theme rounded-md border ${
											newEnvNameInvalid ? "!border-red-500 focus:!border-red-500" : "border-theme-accent"
										} shadow-md`}
									/>
									<p className={`body-xs-regular mt-2 ml-2 ${
										newEnvNameInvalid ? "text-red-500" : "text-theme-muted"
									}`}>
										Do not use whitespaces. Only lowercase letters, numbers, and hyphens.
									</p>
								</div>
								<div className="flex justify-end gap-2 mt-5">
									<Button
										onClick={() => setCreateStep("python")}
										variant="primary"
										size="sm"
										className="button-primary px-2 py-1"
										disabled={newEnvNameInvalid || !newEnvName.trim()}
									>
										Next
									</Button>
								</div>
							</div>
							)}

							{/* Python version selection */}
							{createStep === "python" && (
							<div>
								<div className="pt-1 pb-5 bg-theme-tertiary rounded-md">
									<p className="pl-2 body-md-bold text-theme-secondary">
										Python Version
									</p>
									<div className="flex flex-col mt-5 px-5">
										<PythonVersionSelector
											onSelectVersion={setNewEnvPython}
										/>
									</div>
								</div>
								<div className="flex gap-2 justify-end mt-7">
									<Button
									className="button-outline px-2 py-1"
									variant="outline"
									onClick={() => setCreateStep("name")}
									size="sm"
									>
									Back
									</Button>
									<Button
									className="button-primary px-2 py-1"
									variant="primary"
									onClick={() => setCreateStep("extensions")}
									size="sm"
									>
									Next
									</Button>
								</div>
							</div>
							)}

							{/* Extensions selection */}
							{createStep === "extensions" && (
								<div className="flex flex-1">
									{creationLoading ? (
										<div className="bg-theme-secondary w-full h-full rounded-md flex flex-col items-center">
											<div className="w-full flex justify-center">
												<p className="text-theme-muted body-xs-regular text-center mb-2">
													This may take several minutes..
												</p>
												<div className="flex justify-center ml-5">
													<div className="animate-spin rounded-full h-5 w-5 border-b-2 border-theme-accent" />
												</div>
											</div>
											{/* Log viewer */}
											{creationLogs.length > 0 && (
												<div className="w-full pr-1 pt-1 pb-1 mb-4 border border-theme-accent rounded-md">
													<div className="p-4 max-h-[50vh] min-w-[85vw] overflow-y-auto">
														<pre className="body-xs-regular text-theme-secondary whitespace-pre-wrap font-mono">
															{creationLogs.join("\n")}
														</pre>
													</div>
												</div>
											)}
											<div className="flex justify-center">
												<Button
													onClick={() => handleAbortInstallation("new")}
													variant="danger"
													className="button-danger px-2 py-1"
													disabled={isCancellingCreation}
													size="sm"
												>
													{isCancellingCreation ? (
														<span className="flex items-center">
															<div className="animate-spin rounded-full h-4 w-4 border-b-2 border-theme-contrast mr-2" />
															Cleanup will continue in the background...
														</span>
													) : (
														<span> Cancel</span>
													)}
												</Button>
											</div>
										</div>
									) : createEnvironmentError ? (
										<div>
											<h3 className="text-theme-primary body-xs-medium mt-1 mb-4">
												Environment Creation Error
											</h3>
											<div className="p-3 bg-theme-secondary border border-red-500 rounded-md">
												<p className="text-theme-secondary body-xs-regular mt-1 mb-2 font-mono whitespace-pre-wrap overflow-auto max-h-[50vh]">
													{extractStderr(createEnvironmentError)}
												</p>
												<div className="flex justify-between mt-3">
													<Button
														onClick={() => setCreateEnvironmentError(null)}
														variant="outline"
														size="sm"
														className="button-outline px-2 py-1"
													>
														Dismiss
													</Button>
													<Button
														onClick={() => createEnvironment([])}
														variant="primary"
														size="sm"
														className="button-primary px-2 py-1"
													>
														Retry
													</Button>
												</div>
											</div>
										</div>
									) : creationComplete ? (
										<div className="relative bottom-1">
											<div className="flex justify-between">
											<span className="text-theme-primary body-md-medium">
												Environment Created Successfully!
											</span>
											<span className="text-theme-primary justify-between items-end">
												<Button
													onClick={() => {
														setIsCreateModalOpen(false);
														setCreationLogs([]);
														setCreateStep("name");
													}}
													variant="ghost"
													className="button-ghost"
													size="icon"
												>
													<CustomIcon id="close" className="h-6 w-6" />
												</Button>
											</span>
											</div>

											{/* Log viewer */}
											{creationLogs.length > 0 && (
												<div className="border border-theme-accent rounded-md bg-theme-secondary p-2">
													<div className="w-full p-2 max-h-[50vh] overflow-auto">
														<pre className="body-xs-regular text-theme-secondary whitespace-pre-wrap font-mono overflow-hidden">
															{creationLogs.join("\n")}
														</pre>
													</div>
												</div>
											)}
											<div className="flex justify-center mt-6">
												<Button
													onClick={() => {
														setIsCreateModalOpen(false);
														setCreationLogs([]);
														setCreateStep("name");
													}}
													variant="primary"
													className="button-primary px-2 py-1"
													size="sm"
												>
													Done
												</Button>
											</div>
										</div>
									) : (
										<div className="w-full">
											<ExtensionSelector
												key={extensionSelectorKey}
												onInstallExtensions={safeCreateEnvironment}
												onCancel={() => setCreateStep("python")}
											/>
										</div>
									)}
								</div>
							)}
						</div>
					</div>
				</div>
			)}
			{installExtensionsLoading && (
				<div className="fixed inset-0 z-[9999] bg-black/90 flex items-center justify-center">
					<div className="p-6 max-w-2xl w-full">
						{extensionsError ? (
							<div>
								<h2 className="text-red-600 text-lg font-bold mb-2">Extension Installation Error</h2>
								<div className="mb-4 mt-4 pl-5 pt-1 pr-1 pb-1 border border-red-800 bg-red-900/30 text-red-300 rounded-md text-xs font-mono">
									<div className="whitespace-pre-wrap overflow-auto max-h-60 mt-0.5 mb-0.5">
										{extractStderr(extensionsError)}
									</div>
								</div>
								<div className="flex justify-end">
									<Button
										onClick={() => {
											setExtensionsError(null);
											setInstallExtensionsLoading(false);
										}}
										variant="outline"
										size="sm"
										className="button-outline px-2 py-1"
									>
										Dismiss
									</Button>
								</div>
							</div>
						) : (
							<div className="flex flex-col items-center bg-theme-secondary rounded-lg p-4 border border-theme-accent">
								<div className="flex items-center justify-center p-4 mb-4">
									<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-theme-accent mr-3" />
									<span className="text-theme body-sm-regular">Installing extensions...</span>
								</div>
								<Button
									onClick={handleCancelExtensionInstall}
									variant="danger"
									className="button-danger px-2 py-1"
									size="sm"
								>
									Cancel Installation
								</Button>
							</div>
						)}
					</div>
				</div>
			)}
			{!environmentsLoading && environments.length === 0 && installDir && !installExtensionsLoading ? (
			<div className="text-center m-2 p-4">
				<p className="text-theme-primary body-md-strong">No environments found. <br /><br /><span className="text-theme-primary">Create a new environment to get started.</span></p>
				<div className="flex justify-center mt-5">
					<EnvironmentActionButtons
						showCreateEnvironment={showCreateEnvironment}
						handleRequirementsFileSelect={
							handleRequirementsFileSelect
						}
					/>
				</div>
			</div>
			) : null}
		</div>
	);
}

export const Route = createFileRoute("/environments")({
	component: EnvironmentsPage,
	validateSearch: (search: Record<string, unknown>) => {
		return {
			directory: search.directory as string | undefined,
			userDataDir: search.userDataDir as string | undefined,
		};
	},
});
