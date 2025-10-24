import { Button, Tooltip } from "@openbb/ui-pro";
import { createFileRoute } from "@tanstack/react-router";
import { invoke } from "@tauri-apps/api/core";
import { openPath, openUrl } from "@tauri-apps/plugin-opener";
import { listen } from "@tauri-apps/api/event";
import React, {
	type ReactNode,
	useState,
	useEffect,
	useCallback,
	useRef,
	memo,
} from "react";
import Select, { components } from 'react-select';
import { CopyIcon, DocumentationIcon, FileIcon, FolderIcon, HelpIcon, SettingsIcon } from "../components/Icon";

import CustomIcon from "~/components/Icon";
import Toast from "../components/Toast";

// ============== TYPES ==============

// Core domain types
interface BackendService {
	id: string;
	name: string;
	command: string;
	host?: string;
	port?: number;
	envFile?: string;
	env_file?: string;
	envVars?: Record<string, string>;
	environment: string;
	autoStart: boolean;
	auto_start: boolean;
	status: "running" | "stopped" | "starting" | "stopping" | "error";
	pid?: number;
	startedAt?: string;
	error?: string;
	apiUrl?: string;
	url?: string;
	working_directory?: string;
}

interface Environment {
	name: string;
	path: string;
}

// Form data interface
interface BackendFormData {
	id: string;
	name: string;
	command: string;
	envFile?: string;
	envVars?: Record<string, string>;
	host?: string;
	port?: number;
	environment: string;
	autoStart: boolean;
	status: string;
	working_directory?: string;
	apiUrl?: string;
	pid?: number;
}


interface DeleteConfirmationModalProps {
	onCancel: () => void;
	onConfirm: () => void;
	isLoading: boolean;
}

interface CertificateGenerationModalProps {
	onClose: () => void;
	onDirectorySelect: (callback: (path: string) => void) => void;
}

interface BackendServiceItemProps {
	backend: BackendService;
	onSelect: (id: string | null) => void;
	onStartStop: (id: string, action: "start" | "stop") => void;
	onDelete: (id: string) => void;
	isSelected: boolean;
	isProcessing: boolean;
	onEdit: (id: string) => void;
	onViewLogs: (id: string) => void;
	environments: Environment[];
	isEnvLoading: boolean;
	onStatusUpdate?: (id: string, updates: Partial<BackendService>) => void;
}

interface EnvironmentSelectorProps {
	environments: Environment[];
	selectedEnv: string;
	onChange: (env: string) => void;
	loading: boolean;
}


interface BasicFormFieldsProps {
	formData: {
		name: string;
		command: string;
		working_directory?: string;
		envFile?: string;
		envVars?: Record<string, string>;
		host?: string;
		port?: number;
		apiUrl?: string;
		autoStart: boolean;
		pid?: number;
	};
	onUpdate: (
		updates: Partial<{
			name: string;
			command: string;
			working_directory?: string;
			envFile?: string;
			envVars?: Record<string, string>;
			host?: string;
			port?: number;
			apiUrl?: string;
			auto_start: boolean;
			pid?: number;
		}>,
	) => void;
	onDirectorySelect: () => void;
}

interface AutoStartToggleProps {
	autoStart: boolean;
	onChange: (value: boolean) => void;
	onCancel?: () => void;
	onSubmit?: () => void;
	isUpdate?: boolean;
    formData?: {
        name?: string;
        command?: string;
        environment?: string;
    };
}

interface FormActionsProps {
	onCancel: (e: React.MouseEvent<Element, MouseEvent>) => void;
	onSubmit: () => void;
	isUpdate: boolean;
	formData?: {
		name?: string;
		command?: string;
		environment?: string;
	};
}

interface BackendFormProps {
	formData: BackendFormData;
	formError: string | null;
	onSubmit: () => void;
	onCancel: () => void;
	onUpdateForm: (updates: Partial<BackendFormData>) => void;
	onSelectWorkingDirectory: () => void;
	onSelectEnvFile: () => void;
	environments: Environment[];
	isEnvLoading: boolean;
	isEditMode: boolean;
}

interface HeaderBarProps {
	title: string;
	children?: ReactNode;
	onClose?: () => void;
}

interface BackendListPanelProps {
	backends: BackendService[];
	selectedBackend: string | null;
	processingId: string | null;
	loading: boolean;
	error: string | null;
	deleteError: string | null;
	onRefresh: () => void;
	onCreate: () => void;
	onClearError: () => void;
	onClearDeleteError: () => void;
	onSelect: (id: string | null) => void;
	onStartStop: (id: string, action: "start" | "stop") => void;
	onDelete: (id: string) => void;
	onEdit: (id: string) => void;
	onViewLogs: (id: string) => void;
	environments: Environment[];
	isEnvLoading: boolean;
	onStatusUpdate?: (id: string, updates: Partial<BackendService>) => void;
    onGenerateCertificate: () => void;
    searchQuery: string;
    onSearchChange: (query: string) => void;
}

// ============== COMPONENTS ==============

/**
 * HeaderBar - Displays a title and optional children elements in a header bar
 */
const HeaderBar: React.FC<HeaderBarProps> = React.memo(
	({ title, children }) => (
		<div className="h-[49px] px-3 py-2 border-b border-theme-outline flex justify-between items-center">
			<h2 className="body-lg-medium text-theme-primary">{title}</h2>
			<div className="flex items-center gap-2">{children}</div>
		</div>
	),
);

HeaderBar.displayName = "HeaderBar";


/**
 * DeleteConfirmationModal - Confirmation modal for backend deletion
 */
const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> =
	React.memo(({ onCancel, onConfirm, isLoading }) => {
		useEffect(() => {
			const handleKeyDown = (event: KeyboardEvent) => {
				if (event.key === "Escape") {
					onCancel();
				}
			};
			window.addEventListener("keydown", handleKeyDown);
			return () => window.removeEventListener("keydown", handleKeyDown);
		}, [onCancel]);

		return (
			<div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center">
				<div className="bg-theme-secondary border border-theme-modal rounded-lg shadow-dark-2 w-full max-w-md px-5 py-3">
					<div className="flex justify-between items-center mb-7">
						<h2 className="body-lg-bold text-theme-primary">
							Delete Backend
						</h2>
						<Button
							onClick={onCancel}
							variant="ghost"
							size="icon"
							className="button-ghost"
						>
							<CustomIcon id="close" className="h-6 w-6" />
						</Button>
					</div>
					<p className="mb-1 body-md-medium text-theme-primary flex justify-start">
						Are you sure you want to remove this backend?
					</p>
					<p className="mb-5 body-md-medium text-theme-primary flex justify-start">
						This action cannot be undone.
					</p>
					<div className="flex justify-end gap-2">
						<Button
							variant="outline"
							onClick={onCancel}
							className="button-outline px-2 py-1"
							size="sm"
						>
							<span className="body-xs-medium">Cancel</span>
						</Button>
						<Button
							variant="danger"
							className="button-danger px-2 py-1"
							onClick={onConfirm}
							disabled={isLoading}
							size="sm"
						>
							{isLoading ? (
								<div className="flex items-center">
									<div className="animate-spin h-4 w-4 border-b-2 border-theme-accent rounded-full mr-2" />
									<span className="body-xs-medium">Deleting...</span>
								</div>
							) : (
								<span className="body-xs-medium">Delete</span>
							)}
						</Button>
					</div>
				</div>
			</div>
		);
	});

DeleteConfirmationModal.displayName = "DeleteConfirmationModal";

const CertificateGenerationModal: React.FC<
	CertificateGenerationModalProps
> = ({ onClose, onDirectorySelect }) => {
	useEffect(() => {
		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === "Escape") {
				onClose();
			}
		};
		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, [onClose]);
	const [commonName, setCommonName] = useState("");
	const [orgName, setOrgName] = useState("");
	const [altNames, setAltNames] = useState("");
	const [outputDir, setOutputDir] = useState("");
	const [daysValid, setDaysValid] = useState(365);
	const [password, setPassword] = useState("");
	const [addToTrustStore, setAddToTrustStore] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [successMessage, setSuccessMessage] = useState<string | null>(null);

	const handleGenerate = async () => {
		if (!commonName) {
			setError("Common Name is required.");
			return;
		}
		if (!orgName) {
			setError("Organization Name is required.");
			return;
		}
		if (!outputDir) {
			setError("Output directory is required.");
			return;
		}

		setIsLoading(true);
		setError(null);
		setSuccessMessage(null);

		try {
			const altNamesArray = altNames.split(",").map((s) => s.trim());
			await invoke("generate_self_signed_cert", {
				commonName,
				orgName,
				altNames: altNamesArray,
				outputDir,
				daysValid,
				password: password || null,
				installInTrustStore: addToTrustStore,
			});
			setSuccessMessage("Certificate generated successfully!");
		} catch (err) {
			setError(`Failed to generate certificate: ${err}`);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
			<div className="bg-theme-secondary rounded-lg p-5 max-h-[95vh] w-full max-w-xl overflow-y-auto">
				<div className="flex justify-between items-center mb-3">
					<h2 className="body-lg-bold">
						Generate Self-Signed Certificate
					</h2>
					<Tooltip
						content="Cancel and go back."
						className="tooltip-theme"
					>
						<Button
							variant="ghost"
							onClick={onClose}
							className="button-ghost"
							size="icon"
						>
							<CustomIcon id="close" className="h-6 w-6" />
						</Button>
					</Tooltip>
				</div>
				<div className="bg-theme-primary rounded-sm pb-3 pt-2 pl-5 shadow-md">
					<span className="body-xs-regular text-theme-secondary">
						Fill in the details below to generate files via OpenSSL.
						<div className="mt-1 ml-5">
							<ul className="list-disc list-inside">
								<li>Certificate (.pem)</li>
								<li>Private Key (.key)</li>
								<li>PKCS#12 Bundle (.p12)</li>
							</ul>
						</div>
					</span>
				</div>
				<br />

				{error && (
					<div className="p-3 bg-theme-secondary border border-red-500/50 rounded text-red-500 body-xs-bold mb-4">
						<p>{error}</p>
					</div>
				)}
				{successMessage && (
					<div className="p-3 bg-theme-secondary border border-green-500 rounded text-green-500 body-xs-regular mb-4 flex justify-between items-center">
						<p>{successMessage}</p>
						<Button
							variant="secondary"
							size="sm"
							onClick={async () => await openPath(outputDir)}
							className="button-secondary"
						>
							Open Folder
						</Button>
					</div>
				)}

				<div className="space-y-2">
					<div className="flex justify-between gap-5">
						<div className="flex-1">
							<label className="block body-sm-medium mb-1 text-theme-primary">
								Common Name <span className="text-red-400">*</span>
								<span className="body-xs-regular text-theme-muted ml-1">(IP address or domain)</span>
							</label>
							<input
								type="text"
								value={commonName}
								placeholder="127.0.0.1"
								onChange={(e) => setCommonName(e.target.value)}
								className="body-xs-regular text-theme-secondary w-full p-2 border rounded-md shadow-md"
								style={{
									borderColor: !commonName.trim() ? '#ef444475' : ''
								}}
							/>
						</div>
						<div className="flex-1">
							<label className="block body-sm-medium mb-1 text-theme-primary">
								Organization Name <span className="text-red-400">*</span>
							</label>
							<input
								type="text"
								placeholder="OpenBB"
								value={orgName}
								onChange={(e) => setOrgName(e.target.value)}
								className="body-xs-regular text-theme-secondary w-full p-2 rounded-md shadow-md bg-theme-secondary"
								style={{
									borderColor: !orgName.trim() ? '#ef444475' : ''
								}}
							/>
						</div>
					</div>
					<div className="flex justify-between gap-5">
						<div className="flex-1">
							<label className="block body-sm-medium mb-1 text-theme-primary">
								Alternative Names
								<span className="body-xs-regular text-theme-muted ml-1">(comma-separated)</span>
							</label>
							<input
								type="text"
								value={altNames}
								placeholder="localhost,127.0.0.1,0.0.0.0"
								onChange={(e) => setAltNames(e.target.value)}
								className="body-xs-regular text-theme-secondary w-full p-2 border rounded-md shadow-md"
							/>
						</div>
						<div className="flex-1">
							<label className="block body-sm-medium mb-1 text-theme-primary">
								Password <span className="body-xs-regular text-theme-muted ml-1">(optional)</span>
							</label>
							<input
								type="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								className="body-xs-regular text-theme-secondary w-full p-2 border rounded-md shadow-md"
							/>
						</div>
					</div>
					<div className="flex justify-between gap-5">
						<div className="flex-1">
							<label className="block body-sm-medium mb-1 text-theme-primary">
								Days Valid
							</label>
							<div className="relative flex items-center">
								<input
									type="number"
									value={daysValid}
									onChange={(e) =>
										setDaysValid(Number.parseInt(e.target.value, 10))
									}
									className="body-xs-regular text-theme-secondary w-full p-2 border border-theme-accent rounded-md bg-theme-secondary shadow-sm focus:ring-0 focus:outline-none pr-8"
								/>
								<div className="absolute right-0 mr-2 flex flex-col items-center">
									<button
										type="button"
										onClick={() => setDaysValid(daysValid + 1)}
										className="text-theme-muted hover:text-theme-primary"
									>
										<CustomIcon id="chevron-down" className="h-3 w-3 rotate-180" />
									</button>
									<button
										type="button"
										onClick={() => setDaysValid(daysValid - 1)}
										className="text-theme-muted hover:text-theme-primary"
									>
										<CustomIcon id="chevron-down" className="h-3 w-3" />
									</button>
								</div>
							</div>
						</div>
						<div className="flex-1">
							<label className="block body-sm-medium mb-1 text-theme-primary">
								Output Directory <span className="text-red-400">*</span>
							</label>
							<div className="flex justify-between w-full items-center">
								<input
									type="text"
									value={outputDir}
									onChange={(e) => setOutputDir(e.target.value)}
									placeholder="Select directory"
									className="body-xs-regular text-theme-secondary w-full p-2 focus:ring-0 focus:outline-none rounded-md shadow-md bg-theme-secondary focus-within:border-theme-accent"
									style={{
										borderColor: !outputDir.trim() ? '#ef444475' : ''
									}}
								/>
								<Tooltip
									content="Select output directory"
									className="tooltip-theme"
								>
									<Button
										onClick={() => onDirectorySelect(setOutputDir)}
										variant="ghost"
										size="icon"
										className="button-ghost text-theme-accent pl-2"
										type="button"
									>
										<FolderIcon className="h-5 w-5" />
									</Button>
								</Tooltip>
							</div>
						</div>
					</div>
					<div className="flex-between items-center gap-2">
						<input
							id="trust-store-checkbox"
							type="checkbox"
							checked={addToTrustStore}
							onChange={(e) => setAddToTrustStore(e.target.checked)}
							className="checkbox h-5 w-5 mr-2 mt-5 relative top-1"
						/>
						<label
							htmlFor="trust-store-checkbox"
							className="body-sm-regular text-theme-primary cursor-pointer"
						>
							Add to user key chain (trust store)
						</label>
						<div className="flex justify-end space-x-2 -mt-7">
							<Button
								variant="primary"
								className="button-primary shadow-sm"
								onClick={handleGenerate}
								disabled={outputDir.trim() === "" || commonName.trim() === "" || orgName.trim() === ""}
								size="xs"
							>
								{isLoading ? (
									<div className="flex items-center">
										<div className="animate-spin h-4 w-4 border-b-2 border-theme-accent rounded-full mr-2" />
										<span className="body-xs-medium">Generating...</span>
									</div>
								) : (
									<span className="body-sm-medium">Generate</span>
								)}
							</Button>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};
/**
 * BackendServiceItem - Item in the backend list with actions
 */
const BackendServiceItem: React.FC<BackendServiceItemProps> = React.memo(
    ({
        backend,
        onSelect,
        onStartStop,
        onDelete,
        isSelected,
        isProcessing,
        onViewLogs,
        environments,
        isEnvLoading,
		onStatusUpdate,
    }) => {
        const isRunning = backend.status === "running";
        const canDelete = !isRunning && !isProcessing;

        // Form data state
        const [formData, setFormData] = useState<BackendFormData>({
            id: backend.id,
            name: backend.name,
            command: backend.command,
            host: backend.host,
            port: backend.port,
            pid: backend.pid,
            environment: backend.environment,
            envFile: backend.envFile || "",
            envVars: backend.envVars,
            autoStart: backend.auto_start ?? backend.autoStart ?? false,
            status: backend.status,
            working_directory: backend.working_directory,
            apiUrl: backend.apiUrl || ""
        });
        const [formError, setFormError] = useState<string | null>(null);

        // Runtime state for URL and PID detection
        const [apiUrl, setApiUrl] = useState<string>(backend.apiUrl || backend.url || "");
        const [copied, setCopied] = useState(false);
        const [extractedPid, setExtractedPid] = useState<number | undefined>(backend.pid);
        const [urlConfirmed, setUrlConfirmed] = useState<boolean>(!!backend.apiUrl);

		useEffect(() => {
			const handleKeyDown = (event: KeyboardEvent) => {
				if (event.key === "Escape" && isSelected) {
					onSelect(null);
				}
			};
			window.addEventListener("keydown", handleKeyDown);
			return () => window.removeEventListener("keydown", handleKeyDown);
		}, [isSelected, onSelect]);

        // Display text - show command when not running or URL not confirmed, otherwise show URL
        const displayText = (isRunning && urlConfirmed && apiUrl) ? apiUrl : backend.command;
        const isUrlDisplay = isRunning && urlConfirmed && apiUrl;

        // Helper function to clean ANSI escape codes from a string
        const cleanAnsiCodes = (str: string) => {
            return str.replace(/\u001b\[[0-9;]*m/g, "");
        };

        const copyToClipboard = (e: React.MouseEvent) => {
            e.stopPropagation();
            navigator.clipboard
                .writeText(displayText)
                .then(() => {
                    setCopied(true);
                    setTimeout(() => setCopied(false), 1500);
                })
                .catch((err) => console.error("Failed to copy text:", err));
        };

        // Initialize state based on backend status and existing data
        useEffect(() => {
            if (backend.status === "running") {
                // If backend is running and has a URL, confirm it immediately
                if (backend.apiUrl) {
                    setApiUrl(backend.apiUrl);
                    setUrlConfirmed(true);
                }
                // If backend has a PID, use it
                if (backend.pid) {
                    setExtractedPid(backend.pid);
                }
            } else {
                // Reset state when backend is stopped
                setUrlConfirmed(false);
                setExtractedPid(undefined);
                setApiUrl("");
            }
        }, [backend.status, backend.apiUrl, backend.pid]);

		const tracebackBuffer = useRef<string | null>(null);
		const tracebackTimeout = useRef<NodeJS.Timeout | null>(null);
        // Monitor logs to extract PID and URL for newly started backends
		useEffect(() => {
            if (backend.status === "running" && backend.id && !urlConfirmed) {
                console.log(`Setting up log listener for backend ${backend.id}`);
                const processId = `backend-${backend.id}`;

                const logListenerPromise = listen<{
                    processId: string;
                    output: string;
                    timestamp: number;
                }>("process-output", async (event) => {
                    const { processId: eventProcessId, output } = event.payload;
                    if (eventProcessId === processId) {
                        const cleanOutput = cleanAnsiCodes(output);
						if (cleanOutput.includes("ERROR:") || cleanOutput.includes("address already in use")) {
							console.error(`Backend ${backend.id} error detected: ${cleanOutput}`);
							// Set URL confirmed to stop the spinner
							setUrlConfirmed(true);
							// Stop the backend process immediately
							await invoke("stop_backend_service", { id: backend.id }).catch(console.error);
							// Update backend status to error
							await invoke("update_backend_service", {
								backend: {
									...backend,
									status: "error",
									error: cleanOutput.trim(),
								}
							}).catch(console.error);
							// Notify parent component
							if (onStatusUpdate) {
								onStatusUpdate(backend.id, {
									status: "error",
									error: cleanOutput.trim(),
								});
							}
							// Show error in UI
							setFormError(`${cleanOutput.trim()}`);
							return;
						}

						if (tracebackBuffer.current !== null) {
							tracebackBuffer.current += cleanOutput + "\n";
							// Heuristic: end of traceback is a blank line or prompt
							if (/^\s*$/.test(cleanOutput) || cleanOutput.startsWith(">") || cleanOutput.startsWith("$")) {
								// Stop backend and update error
								setUrlConfirmed(true);
								// Stop the backend process
								await invoke("stop_backend_service", { id: backend.id }).catch(console.error);
								// Save the full traceback as error
								await invoke("update_backend_service", {
									backend: {
										...backend,
										status: "error",
										error: tracebackBuffer.current.trim(),
									}
								}).catch(console.error);

								if (onStatusUpdate) {
									onStatusUpdate(backend.id, {
										status: "error",
										error: tracebackBuffer.current.trim(),
									});
								}
								tracebackBuffer.current = null;
							} else {
								// Reset timeout on every new line
								if (tracebackTimeout.current) clearTimeout(tracebackTimeout.current);
								tracebackTimeout.current = setTimeout(async () => {
									setFormError("Backend failed to start. See logs for details.");
									setUrlConfirmed(true);
									await invoke("stop_backend_service", { id: backend.id }).catch(console.error);
									await invoke("update_backend_service", {
										backend: {
											...backend,
											status: "error",
											error: tracebackBuffer.current?.trim()  || "",
										}
									}).catch(console.error);

									if (onStatusUpdate) {
										onStatusUpdate(backend.id, {
											status: "error",
											error: tracebackBuffer.current?.trim() || "",
										});
									}
									tracebackBuffer.current = null;
								}, 2000); // 2s after last line, flush
							}
							return;
						}
						if (cleanOutput.includes("Traceback")) {
							// Start collecting traceback
							tracebackBuffer.current = cleanOutput + "\n";
							// Set a timeout in case traceback is short
							if (tracebackTimeout.current) clearTimeout(tracebackTimeout.current);
							tracebackTimeout.current = setTimeout(async () => {
								setFormError("Backend failed to start. See logs for details.");
								setUrlConfirmed(true);
								await invoke("stop_backend_service", { id: backend.id }).catch(console.error);
								await invoke("update_backend_service", {
									backend: {
										...backend,
										status: "error",
										error: tracebackBuffer.current?.trim() || "",
									}
								}).catch(console.error);

								if (onStatusUpdate) {
									onStatusUpdate(backend.id, {
										status: "error",
										error: tracebackBuffer.current?.trim() || "",
									});
								}
								tracebackBuffer.current = null;
							}, 2000);
							return;
						}

                        // Extract PID from server startup message
                        if (cleanOutput.includes("Started server process")) {
                            const pidMatch = cleanOutput.match(/\[(\d+)\]/);
                            if (pidMatch?.[1]) {
                                const pid = Number.parseInt(pidMatch[1], 10);
                                console.log(`Found PID: ${pid}`);
                                setExtractedPid(pid);

                                // Update backend with PID immediately
                                invoke("update_backend_service", {
                                    backend: {
                                        ...backend,
                                        pid
                                    }
                                }).catch(console.error);
                            }
                        }
                    }
                });

				return () => {
					if (tracebackTimeout.current) {
						clearTimeout(tracebackTimeout.current);
						tracebackTimeout.current = null;
					}
					logListenerPromise.then((unlisten) => unlisten()).catch(console.error);
				};
            }
        }, [backend.status, backend.id, urlConfirmed, onStatusUpdate]);

        // Failsafe: Stop spinner after 45 seconds if URL is never confirmed
        useEffect(() => {
            if (isRunning && !urlConfirmed) {
                const failsafeTimeout = setTimeout(() => {
                    console.log(`Failsafe: Setting urlConfirmed to true for backend ${backend.id} after 30s`);
                    setUrlConfirmed(true);
                }, 45000);

                return () => clearTimeout(failsafeTimeout);
            }
        }, [isRunning, urlConfirmed, backend.id]);

        const handleFormSubmit = () => {
			if (!formData.name || !formData.name.trim()) {
				setFormError("Backend Name is required");
				return;
			}

			if (!formData.command || !formData.command.trim()) {
				setFormError("Executable is required");
				return;
			}

			if (!formData.environment) {
				setFormError("Environment selection is required");
				return;
			}

            const backendToSave = {
                id: backend.id,
                environment: formData.environment,
                name: formData.name,
                command: formData.command,
                host: formData.host,
                port: formData.port,
                apiUrl: apiUrl || formData.apiUrl || "",
				envFile: formData.envFile || "",
				envVars: formData.envVars,
                working_directory: formData.working_directory,
                auto_start: formData.autoStart ?? false,
                status: backend.status,
                pid: extractedPid || formData.pid,
            };

            invoke("update_backend_service", { backend: backendToSave })
                .then(() => {
                    window.location.reload();
                })
                .catch((err) => {
                    console.error("Failed to update backend:", err);
                    setFormError(`Failed to update backend: ${err}`);
                });
        };

		useEffect(() => {
            console.log(`Backend ${backend.id} status updated to: ${backend.status}`);
        }, [backend.status]);

        return (
            <li className="bg-theme-tertiary border border-theme-modal rounded-md px-3 pt-3 pb-3 mb-5 shadow-md group">
                <div className="w-full">
                    <div className="flex justify-between items-center">
						{/* Backend name and status indicator */}
                        <div className="body-md-bold flex items-center">
                            <div className="text-theme-primary">
                                {backend.name}
                            </div>
                            <div className="flex items-center flex-wrap gap-1">
                                <span className="body-sm-medium px-2 py-0.5 rounded-full bg-theme-tag text-theme ml-3 shadow-md">
                                    {backend.environment}
                                </span>
                                {backend.autoStart && (
                                    <span className="body-xs-regular px-1.5 py-0.5 rounded-full bg-green-500/40 text-theme-secondary border-theme-accent ml-2 shadow-md">
                                        Auto-Start
                                    </span>
                                )}
                            </div>
                        </div>
						{/* Action Buttons */}
						<div className="flex items-center">
							{/* Delete Button - Only shown when backend is stopped and on hover */}
							{canDelete && (
								<Tooltip
									content="Remove the backend configuration."
									className="tooltip-theme"
								>
									<Button
										onClick={(e) => {
											e.stopPropagation();
											onDelete(backend.id);
										}}
										variant="ghost"
										size="icon"
										className="button-ghost opacity-0 group-hover:opacity-100 transition-opacity duration-0"
										aria-label="delete backend"
									>
										<CustomIcon id="bin" className="h-4 w-4" />
									</Button>
								</Tooltip>
							)}

							<Tooltip
								content={isSelected ? "Hide Configuration" : "Show backend configuration panel."}
								className="tooltip-theme"
							>
								<Button
									variant="ghost"
									size="icon"
									onClick={(e) => {
										e.stopPropagation();
										onSelect(isSelected ? null : backend.id);
									}}
									className="button-ghost opacity-0 group-hover:opacity-100 transition-opacity duration-0"
								>
									<SettingsIcon className="w-7 h-7" />
								</Button>
							</Tooltip>

							{/* View logs button */}
							<Tooltip content="View the console logs for this backend." className="tooltip-theme">
								<Button
									onClick={(e) => {
										e.stopPropagation();
										onViewLogs(backend.id);
									}}
									variant="outline"
									size="xs"
									className="button-outline py-1 px-2 mr-2 ml-1"
								>
									<span className="body-xs-medium">Logs</span>
								</Button>
							</Tooltip>

							{/* Start/Stop button */}
							<Tooltip
								content={isRunning ? "Stop Backend" : "Start Backend"}
								className="tooltip-theme"
							>
								<Button
									variant="primary"
									size="xs"
									onClick={(e) => {
										e.stopPropagation();
										onStartStop(backend.id, isRunning ? "stop" : "start");
									}}
									disabled={isProcessing}
									className={`button-startstop py-1 px-2 ${isRunning ? "running" : "stopped"}${isProcessing ? " processing" : ""}`}
								>
									{isProcessing ? (
										<div className="flex items-center">
											<div className="animate-spin h-4 w-4 border-2 accent-color border-t-transparent rounded-full mr-1" />
											<span className="body-xs-medium whitespace-nowrap">
												{backend.status === "starting"
													? "Starting..."
													: "Stopping..."}
											</span>
										</div>
									) : isRunning ? (
										<span>Stop</span>
									) : (
										<span>Start</span>
									)}
								</Button>
							</Tooltip>
						</div>
                    </div>

                    {/* Backend details */}
                    <div className="flex flex-col pt-3">
                        {backend.status === "error" && backend.error && (
                            <div className="border border-red-500 rounded m-2 mb-5 overflow-hidden p-2 relative">
                                <div className="p-2 bg-theme-primary text-red-500 body-xs-regular whitespace-pre-wrap overflow-auto max-h-40">
                                    {backend.error}
							</div>
							<Tooltip
								content="Dismiss error."
								className="tooltip-theme"
							>
								<Button
									onClick={() => {
										// Clear the error by updating the backend status
										if (onStatusUpdate) {
											onStatusUpdate(backend.id, {
												status: "stopped",
												error: undefined
											});
										}
										// Also update the backend in the database
										invoke("update_backend_service", {
											backend: {
												...backend,
												status: "stopped",
												error: undefined
											}
										}).catch(console.error);
									}}
									variant="ghost"
									className="button-ghost absolute top-1 right-1 p-1"
									size="icon"
								>
									<CustomIcon id="close" className="h-4 w-4" />
								</Button>
							</Tooltip>
                        </div>
                        )}

						{/* Copyable URL/command display */}
						<div
							className="body-xs-regular flex items-center"
						>
							<span className="body-xs-bold text-theme-secondary pr-1">{displayText}</span>
							{copied ? (
								<Tooltip
									content={`${isUrlDisplay ? 'URL' : 'Command'} copied to clipboard.`}
									className="tooltip-theme"
								>
								<Button
									variant="ghost"
									className="flex items-center justify-center w-8 h-8 p-0"
									aria-label="success icon"
								>
									<CustomIcon
										id="success"
										className="h-6 w-6 text-green-500"
									/>
								</Button>
							</Tooltip>
						) : (
							<Tooltip
								content={`Click to copy ${isUrlDisplay ? 'URL' : 'command'}`}
								className="tooltip-theme"
							>
								<Button
									variant="ghost"
									onClick={copyToClipboard}
									className="button-ghost flex items-center justify-center w-5 h-5 p-1 ml-1"
									aria-label="copy icon"
									size="lg"
								>
									<CopyIcon
										className="h-4 w-4"
									/>
								</Button>
							</Tooltip>
						)}
						</div>

						{(extractedPid && isRunning) || (isRunning && !urlConfirmed) ? (
						<div className="flex flex-col">
							{isRunning && !urlConfirmed && (
							<div className="body-xs-regular text-theme-secondary mt-1 flex items-center">
								<div className="animate-spin h-3 w-3 border-b-2 accent-color rounded-full mr-1" />
								<span>Waiting for service to initialize...</span>
							</div>
							)}
							{extractedPid && isRunning && (
							<div className="body-xs-regular text-theme-secondary mt-1">
								<span className="body-xs-bold">Process ID:</span> {extractedPid}
							</div>
							)}
						</div>
						) : null}

                        {/* Backend Configuration Panel*/}
                        {isSelected && (
							<div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center overflow-auto" role="dialog">
								<div className="bg-theme-secondary border border-theme-modal rounded-lg px-5 pt-3 pb-5 max-h-[90vh] w-full max-w-xl overflow-y-auto">
									{/* Header */}
									<div className="flex justify-between items-center mb-2">
										<p className="body-lg-medium text-theme-primary">Backend Configuration</p>
										<Tooltip
											content="Cancel and go back."
											className="tooltip-theme"
										>
											<Button
												type="button"
												variant="ghost"
												onClick={(e) => {
													e.stopPropagation();
													onSelect(null);
												}}
												className="button-ghost"
												title="Close details"
												size="icon"
											>
												<CustomIcon
													id="close"
													className="h-6 w-6"
												/>
											</Button>
										</Tooltip>
                                    </div>

                                    <div className="flex-1 space-y-1">
                                        {formError && (
                                            <div className="p-3 border-red-500/50 rounded text-red-500 body-xs-regular">
                                                <p>{formError}</p>
                                            </div>
                                        )}
										<div>
											<EnvironmentSelector
												environments={environments}
												selectedEnv={formData.environment}
												onChange={(env) => setFormData(prev => ({ ...prev, environment: env }))}
												loading={isEnvLoading}
											/>
										</div>
                                        <BasicFormFields
                                            formData={{
                                                name: formData.name,
                                                command: formData.command,
                                                working_directory: formData.working_directory,
                                                envFile: formData.envFile,
                                                envVars: formData.envVars,
                                                host: formData.host ?? undefined,
                                                port: formData.port ?? undefined,
                                                apiUrl: formData.apiUrl,
                                                autoStart: formData.autoStart ?? false,
                                                pid: extractedPid,
                                            }}
                                            onUpdate={(updates) => setFormData(prev => ({ ...prev, ...updates }))}
                                            onDirectorySelect={() => {
                                                invoke<string>("select_directory", {
                                                    prompt: "Select Working Directory for Backend",
                                                })
                                                    .then((directory) => setFormData(prev => ({
                                                        ...prev,
                                                        working_directory: directory,
                                                    })))
                                                    .catch((err) => console.error("Failed to select working directory:", err));
                                            }}
                                        />
										<div className="pt-3">
											<AutoStartToggle
												autoStart={formData.autoStart}
												onChange={(value) => setFormData(prev => ({ ...prev, autoStart: value }))}
												onCancel={() => {
													setFormError(null);
													onSelect(null);
												}}
												onSubmit={handleFormSubmit}
												isUpdate={true}
												formData={formData}
											/>
										</div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </li>
        );
    }
);

BackendServiceItem.displayName = "BackendServiceItem";

/* eslint-disable @typescript-eslint/no-explicit-any */
const selectStyles = {
  container: (provided: any) => ({
    ...provided,
    width: '100%',
	cursor: 'pointer'
  }),
  control: (provided: any, state: any) => ({
    ...provided,
    backgroundColor: 'var(--bg-theme-secondary)',
    color: 'var(--text-primary)',
    borderColor: state.isFocused
      ? 'var(--border-accent)'
      : 'var(--border-color)',
    boxShadow: 'none',
    minHeight: '1.9rem',
    fontSize: '0.875rem',
    borderRadius: '0.375rem',
    padding: '0 0.25rem',
	width: '100%',
    '&:hover': {
      borderColor: 'var(--border-accent)',
    },
  }),
  menu: (provided: any) => ({
    ...provided,
	backgroundColor: 'var(--dropdown-bg)',
	marginTop: 0,
	borderRadius: '4px',
	padding: '2px',
	boxShadow: '0 2 10 0 rgba(0, 0, 0, 0.4)',
	zIndex: 100,
	borderColor: 'var(--button-secondary-bg)'
  }),
  menuPortal: (provided: any) => ({
    ...provided,
    backgroundColor: 'var(--dropdown-bg)',
    opacity: 1,
	marginTop: 5,
    zIndex: 99999,
  }),
  option: (provided: any) => ({
    ...provided,
    backgroundColor: 'var(--dropdown-bg)',
    color: 'var(--text-primary)',
    cursor: 'pointer',
    fontSize: '0.825rem',
    padding: '0.1rem 0.75rem',
    opacity: 1,
    ':active': {
      backgroundColor: 'var(--dropdown-bg)',
    },
  }),
  singleValue: (provided: any) => ({
    ...provided,
    fontSize: '0.875rem',
	color: 'var(--text-primary)',
  }),
  input: (provided: any) => ({
    ...provided,
    color: 'var(--text-primary)',
    fontSize: '0.875rem',
	cursor: 'pointer',
  }),
  placeholder: (provided: any) => ({
    ...provided,
    color: 'var(--text-muted)',
    fontSize: '0.875rem',
  }),
  dropdownIndicator: (provided: any) => ({
    ...provided,
    color: 'var(--text-muted)',
    padding: '0 4px',
	cursor: 'pointer',
    '&:hover': { color: 'var(--text-primary)' },
  }),
  indicatorSeparator: () => ({
    display: 'none',
  }),
};

const CustomOption = (props: any) => {
  const { isSelected, children } = props;
  return (
    <components.Option {...props}>
      <div className="flex flex-row items-start">
        {isSelected ? (
          <CustomIcon id="check" className="w-4 h-4 text-theme-primary mr-2" />
        ) : (
          <span className="w-4 h-4 mr-2" />
        )}
        <span>{children}</span>
      </div>
    </components.Option>
  );
};
/* eslint-enable @typescript-eslint/no-explicit-any */
/**
 * EnvironmentSelector - Displays available conda environments for selection
 */
const EnvironmentSelector: React.FC<EnvironmentSelectorProps> = React.memo(
	({ environments, selectedEnv, onChange, loading }) => (
		<div className="space-y-5">
			<div>
				<label
					htmlFor="environment-select"
					className="body-sm-bold mb-1 text-theme-secondary"
				>
					Environment <span className="text-red-400">*</span>
				</label>
				{loading && environments.length === 0 ? (
					<div className="flex items-center">
						<div className="animate-spin rounded-full h-4 w-4 border-b-2 accent-color" />
						<span className="body-xs-regular text-theme-primary">
							Loading environments...
						</span>
					</div>
				) : environments.length === 0 ? (
					<div className="body-xs-regular text-theme-primary">No environments found</div>
				) : (
					<Select
						id="environment-select"
						className="mt-1 w-full"
						styles={selectStyles}
						menuPortalTarget={document.body}
						options={environments.map(env => ({ value: env.name, label: env.name }))}
						value={environments
						.map(env => ({ value: env.name, label: env.name }))
						.find(option => option.value === selectedEnv) || null}
						onChange={option => onChange(option ? option.value : "")}
						components={{ Option: CustomOption }}
					/>
				)}
			</div>
		</div>
	),
);

EnvironmentSelector.displayName = "EnvironmentSelector";


const validateCommandInput = (command: string): { isValid: boolean; error?: string } => {
    if (!command.trim()) {
        return { isValid: false, error: "Command cannot be empty" };
    }

    // Check for dangerous characters and patterns
    const dangerousPatterns = [
		// Bash/Zsh specific patterns
        /\.\./,
        /rm\s+-/,
        /sudo/,
        /chmod/,
        /chown/,
        /curl.*\|/,
        /wget.*\|/,
		/apt.*/,
		/yum.*/,
		/dnf.*/,
        /eval/,
        /exec/,
		/mkfs/,
		/echo/,
		/grep/,
		// PowerShell specific patterns
        /Invoke-Expression/i,
        /IEX\s+/i,
        /Invoke-Command/i,
        /Start-Process/i,
        /New-Object.*Net\.WebClient/i,
        /DownloadString/i,
        /DownloadFile/i,
        /powershell.*-c/i,
        /pwsh.*-c/i,
        /Remove-Item/i,
        /rm\s+/i,
        /del\s+/i,
        /Delete-Item/i,
        /Clear-Content/i,
        /Remove-ItemProperty/i,
        // CMD specific patterns
        /cmd.*\/c/i,
        /cmd.*\/k/i,
        /call\s+/i,
        /start\s+/i,
        /for\s+.*\s+in\s+.*do/i,
        /if\s+.*\s+then/i,
        /goto\s+/i,
        /echo\s+.*>\s*/i,
        /del\s+.*\*/i,
        /erase\s+/i,
        /rd\s+/i,
        /rmdir\s+/i,
        /deltree\s+/i,
        /format\s+/i,
        /fdisk\s+/i,
    ];

    for (const pattern of dangerousPatterns) {
        if (pattern.test(command)) {
            return {
                isValid: false,
                error: "Command contains potentially dangerous characters or patterns."
            };
        }
    }

    const allowedCharsPattern = /^[a-zA-Z0-9\s.\-_/:'",[\]{}]+$/;
    if (!allowedCharsPattern.test(command)) {
        return {
            isValid: false,
            error: "Command containls invalid characters."
        };
    }

    return { isValid: true };
};


/**
 * BasicFormFields - Common form fields for backend configuration
 */
const BasicFormFields: React.FC<BasicFormFieldsProps> = React.memo(
    ({ formData, onUpdate, onDirectorySelect }) => {
		const [envVarsText, setEnvVarsText] = useState(
			Object.entries(formData.envVars || {})
				.map(([key, value]) => `${key}=${value}`)
				.join("\n")
		);

        const [commandError, setCommandError] = useState<string | null>(null);

        const handleCommandChange = (value: string) => {
            const validation = validateCommandInput(value);
            setCommandError(validation.isValid ? null : validation.error || null);
            onUpdate({ command: value });
        };

		useEffect(() => {
			const propVars = formData.envVars || {};
			const lines = envVarsText.split('\n');
			const textVars: Record<string, string> = {};
			for (const line of lines) {
				const trimmed = line.trim();
				if (!trimmed) continue;
				const idx = trimmed.indexOf('=');
				if (idx > 0) {
					const key = trimmed.slice(0, idx).trim();
					const value = trimmed.slice(idx + 1).trim();
					if (key) textVars[key] = value;
				}
			}

			if (JSON.stringify(propVars) !== JSON.stringify(textVars)) {
				setEnvVarsText(
					Object.entries(propVars)
						.map(([key, value]) => `${key}=${value}`)
						.join("\n")
				);
			}
		}, [formData.envVars, envVarsText]);

        // --- Working Directory State and Validation ---
        const [currentWorkingDir, setCurrentWorkingDir] = useState<string | null>(
            formData.working_directory || null
        );
        const [workingDirInput, setWorkingDirInput] = useState(formData.working_directory || "");
        const [workingDirValid, setWorkingDirValid] = useState(true);
        const [checkingDirectory, setCheckingDirectory] = useState(false);
		const [envFileValid, setEnvFileValid] = useState<boolean | undefined>(undefined);

        useEffect(() => {
            if (formData.working_directory !== currentWorkingDir) {
                setCurrentWorkingDir(formData.working_directory || null);
                setWorkingDirInput(formData.working_directory || "");
            }
        }, [formData.working_directory]);

        // Validate directory when input changes
        useEffect(() => {
            const validateDirectory = async () => {
                if (!workingDirInput.trim()) {
                    setWorkingDirValid(true);
                    return;
                }
                setCheckingDirectory(true);
                try {
                    const exists = await invoke<boolean>("check_directory_exists", {
                        path: workingDirInput.trim()
                    });
                    setWorkingDirValid(exists);
                } catch (err) {
                    console.error("Error checking directory:", err);
                    setWorkingDirValid(false);
                } finally {
                    setCheckingDirectory(false);
                }
            };
            const timeoutId = setTimeout(validateDirectory, 500); // Debounce validation
            return () => clearTimeout(timeoutId);
        }, [workingDirInput]);

        // Handle directory input submission
        const handleDirectoryInputSubmit = () => {
            if (workingDirValid && workingDirInput.trim()) {
                setCurrentWorkingDir(workingDirInput.trim());
                onUpdate({ working_directory: workingDirInput.trim() });
            }
        };

        // Handle Enter key press in input
        const handleDirectoryInputKeyPress = (e: React.KeyboardEvent) => {
            if (e.key === "Enter") {
                handleDirectoryInputSubmit();
            }
        };

        return (
            <div className="flex-1">
                <div>
                    <label
                        htmlFor="name-input"
                        className="body-sm-medium mb-2 text-theme-primary"
                    >
                        Backend Name <span className="text-red-400">*</span>
                    </label>
                    <input
                        id="name-input"
                        type="text"
                        value={formData.name || ""}
                        onChange={(e) => onUpdate({ name: e.target.value })}
                        placeholder="My Backend Service"
						className="body-xs-regular mt-1 text-theme-secondary w-full rounded-md shadow-md bg-theme-secondary focus:ring-0 focus:outline-none border-1"
						style={{
							borderColor: !formData.name.trim() ? '#ef444475' : ''
						}}
                        autoCorrect="off"
                        autoCapitalize="off"
                        spellCheck="false"
                        required
                    />
                </div>

                <div>
                    <label
                        htmlFor="command-input"
                        className="body-sm-medium mb-2 mt-2 text-theme-primary flex items-center gap-1"
                    >
                        <span>Executable</span><span className="text-red-400 mr-1">*</span>
                        <HelpIcon tooltip="Command line executable - i.e. 'python script.py'. Include any arguments or flags needed to run the script." />
                    </label>
					<div className={`rounded-md ${
                            commandError ? 'border border-red-500/50' : 'border border-theme-accent'
                        }`}>
						<input
							id="command-input"
							type="text"
							value={formData.command || ""}
							onChange={(e) => handleCommandChange(e.target.value)}
							placeholder="openbb-api"
							className="body-xs-regular border-none shadow-sm w-full"
							autoCorrect="off"
							autoCapitalize="off"
							spellCheck="false"
						/>
					</div>
                    {commandError && (
                        <span className="body-xs-medium text-red-500 mt-1 block">{commandError}</span>
                    )}
                </div>

                {/* Working Directory Selection */}
                <div className="flex flex-col gap-2 mb-2">
					<label
						htmlFor="working-dir-input"
						className="body-sm-medium text-theme-primary flex items-center gap-2 mt-1"
					>
						<span>Working Directory</span>
						<HelpIcon tooltip="The directory from where the executable will be run. Defaults to the installation directory + '/backends'" />
					</label>
					<div className="flex items-center">
						<input
							id="working-dir-input"
							type="text"
							value={workingDirInput}
							onChange={e => setWorkingDirInput(e.target.value)}
							onBlur={handleDirectoryInputSubmit}
							onKeyDown={handleDirectoryInputKeyPress}
							placeholder="Select or enter path (defaults to '{installation_directory}/backends')"
							className="body-xs-regular text-theme-secondary w-full bg-transparent border border-theme-accent rounded-md focus:ring-0 focus:outline-none"
							autoCorrect="off"
							autoCapitalize="off"
							spellCheck="false"
						/>
						<Tooltip
								content="Select working directory"
								className="tooltip-theme"
							>
								<Button
									onClick={async () => {onDirectorySelect()}}
									variant="ghost"
									size="icon"
									className="button-ghost"
									type="button"
								>
									<FolderIcon className="ml-3 h-6 w-6" />
								</Button>
							</Tooltip>
					</div>
					{checkingDirectory && (
						<span className="body-xs-medium text-theme-muted mt-1">Checking directory...</span>
					)}
					{!workingDirValid && (
						<span className="body-xs-medium text-red-500 ml-3">Directory does not exist.</span>
					)}
				</div>
				<label
					htmlFor="env-file-input"
					className="body-sm-medium text-theme-primary flex items-center gap-2"
				>
					<span>Environment File</span>
					<HelpIcon tooltip="Add a `.env` file to export environment variables." />
				</label>
				<div className="flex items-center border-none mt-2">
					<input
						id="env-file-input"
						type="text"
						value={formData.envFile || ""}
						onChange={async (e) => {
							const file = e.target.value;
							onUpdate({ envFile: file });
							// Only validate if something is entered
							if (file.trim() !== "") {
								try {
									const exists = await invoke<boolean>("check_file_exists", { path: file });
									setEnvFileValid(exists);
								} catch {
									setEnvFileValid(false);
								}
							} else {
								setEnvFileValid(undefined);
							}
						}}
						placeholder="Select or enter path to .env file"
						className="body-xs-regular text-theme-secondary w-full bg-transparent border border-theme-accent focus:ring-0 focus:outline-none"
						autoCorrect="off"
						autoCapitalize="off"
						spellCheck="false"
					/>
						<Tooltip
							content="Select .env file"
							className="tooltip-theme"
						>
							<Button
								onClick={async () => {
									const file = await invoke<string>("select_file", { filter: ".env" });
									if (file) {
										onUpdate({ envFile: file });
										try {
											const exists = await invoke<boolean>("check_file_exists", { path: file });
											setEnvFileValid(exists);
										} catch {
											setEnvFileValid(false);
										}
									}
								}}
								variant="ghost"
								size="icon"
								className="button-ghost"
								type="button"
							>
								<FileIcon className="h-5 w-5 ml-3" />
							</Button>
						</Tooltip>
				</div>
				{envFileValid === false && formData.envFile && formData.envFile.trim() !== "" && (
					<span className="text-xs text-red-500 ml-3">File does not exist.</span>
				)}
				{/* Environment Variables */}
				<div className="flex flex-col">
					<label className="body-sm-medium mb-2 mt-2 text-theme-primary flex items-center gap-2">
						<span>Environment Variables</span>
						<HelpIcon tooltip="Equivalent to an `.env` file. Each line will be split on the first '='. Variables are exported after loading the optional environment file." />
					</label>
					<div className="flex flex-col">
						<textarea
							placeholder={"KEY=VALUE\nANOTHER_KEY=ANOTHER_VALUE"}
							value={envVarsText}
							onChange={(e) => {
								const newText = e.target.value;
								setEnvVarsText(newText);
								const lines = newText.split("\n");
								const envVars: Record<string, string> = {};
								for (const line of lines) {
									const trimmed = line.trim();
									if (!trimmed) continue;
									const idx = trimmed.indexOf("=");
									if (idx > 0) {
										const key = trimmed.slice(0, idx).trim();
										const value = trimmed.slice(idx + 1).trim();
										if (key) envVars[key] = value;
									}
								}
								onUpdate({ envVars });
							}}
							style={{
								lineHeight: "1.5",
								fontFamily: "monospace",
								minHeight: "80px",
								resize: "vertical",
							}}
							className="rounded-md shadow-sm"
							autoCorrect="off"
							autoCapitalize="off"
							spellCheck="false"
						/>
					</div>
				</div>
            </div>
        );
    }
);
/**
 * AutoStartToggle - Toggle for auto-starting backends with action buttons
 */
const AutoStartToggle: React.FC<AutoStartToggleProps> = React.memo(
    ({ autoStart, onChange, onCancel, onSubmit, isUpdate, formData }) => {
        // Check if command is valid (same validation as FormActions)
        const commandValidation = formData?.command ? validateCommandInput(formData.command) : { isValid: false };
        const isFormValid = formData?.name?.trim() &&
                           formData?.command?.trim() &&
                           formData?.environment?.trim() &&
                           commandValidation.isValid;

        return (
            <div className="flex justify-between items-right">
                <div>
                    <label
                        htmlFor="auto-start-toggle"
                        className="flex items-center cursor-pointer w-full relative top-3"
                    >
                        <Tooltip
                            content="Automatically start this backend service on application launch. To start on system boot, select 'Start at Login' from the Tray Icon menu."
                            className="tooltip-theme"
                        >
                            <div className="flex items-center">
                                <input
                                    id="auto-start-toggle"
                                    type="checkbox"
                                    checked={autoStart}
                                    onChange={() => onChange(!autoStart)}
                                    className="checkbox mr-2 ml-1"
                                />
                                <span className="body-sm-medium text-theme-primary">
                                    Start Automatically
                                </span>
                            </div>
                        </Tooltip>
                    </label>
                </div>
                {onCancel && onSubmit && (
                    <div className="flex justify-end gap-2">
                        <Tooltip
                            content="Cancel changes"
                            className="tooltip-theme"
                        >
                            <Button
                                type="button"
                                variant="outline"
                                onClick={onCancel}
                                className="button-outline shadow-sm"
                                size="sm"
                            >
                                <span className="text-xs-bold">Cancel</span>
                            </Button>
                        </Tooltip>
                        <Tooltip
                            content={isUpdate ? "Save changes" : "Create new backend"}
                            className="tooltip-theme"
                        >
                            <Button
                                type="button"
                                variant="primary"
                                onClick={onSubmit}
                                className="button-primary shadow-sm"
                                size="sm"
                                disabled={!isFormValid}
                            >
                                <span className="body-xs-bold">{isUpdate ? "Save" : "Create"}</span>
                            </Button>
                        </Tooltip>
                    </div>
                )}
            </div>
        );
    },
);

AutoStartToggle.displayName = "AutoStartToggle";

/**
 * FormActions - Submit/Cancel buttons for forms with proper update/create state handling
 */
const FormActions: React.FC<FormActionsProps> = React.memo(
    ({ onCancel, onSubmit, isUpdate, formData }) => {
        // Check if required fields are filled
		const commandValidation = formData?.command ? validateCommandInput(formData.command) : { isValid: false };
        const isFormValid = formData?.name?.trim() &&
                           formData?.command?.trim() &&
                           formData?.environment?.trim() &&
						   commandValidation.isValid;

        return (
            <div
                className="flex justify-end gap-2"
                style={{ marginTop: "-15px" }}
            >
                <Tooltip
                    content="Cancel changes"
                    className="tooltip-theme"
                >
                    <Button
                        type="button"
                        variant="outline"
                        onClick={onCancel}
                        className="button-outline shadow-sm"
                        size="sm"
                    >
                        <span className="body-xs-medium">Cancel</span>
                    </Button>
                </Tooltip>
                <Tooltip
                    content={isUpdate ? "Save changes" : "Create new backend"}
                    className="tooltip-theme"
                >
                    <Button
                        type="button"
                        variant="primary"
                        onClick={onSubmit}
                        className="button-primary shadow-sm"
                        size="sm"
                        disabled={!isFormValid}
                    >
                        <span className="body-xs-medium">{isUpdate ? "Save" : "Create"}</span>
                    </Button>
                </Tooltip>
            </div>
        );
    },
);

FormActions.displayName = "FormActions";

/**
 * BackendForm - Form for creating/editing backend services
 */
const BackendForm: React.FC<BackendFormProps> = React.memo(
	({
		formData,
		formError,
		onSubmit,
		onCancel,
		onUpdateForm,
		environments,
		isEnvLoading,
		isEditMode,
	}) => {

		return (
			<div className="flex-1 overflow-y-auto">
				<div className="space-y-2">
					{formError && (
						<div className="p-3 bg-theme-secondary border border-red-500/50 rounded text-red-500 body-xs-bold">
							<p>{formError}</p>
						</div>
					)}

					<EnvironmentSelector
						environments={environments}
						selectedEnv={formData.environment}
						onChange={(env) => onUpdateForm({ environment: env })}
						loading={isEnvLoading}
					/>

					<div className="rounded-md">
						<BasicFormFields
							formData={{
								name: formData.name,
								command: formData.command,
								working_directory: formData.working_directory,
								envFile: formData.envFile,
								envVars: formData.envVars,
								host: formData.host,
								port: formData.port,
								apiUrl: formData.apiUrl,
								autoStart: formData.autoStart ?? false,
							}}
							onUpdate={(updates) => onUpdateForm(updates)}
							onDirectorySelect={() => {
								invoke<string>("select_directory", {
									prompt: "Select Working Directory for Backend",
								})
									.then((directory) =>
										onUpdateForm({ working_directory: directory }),
									)
									.catch((err) =>
										console.error("Failed to select working directory:", err),
									);
							}}
						/>
					</div>

					<AutoStartToggle
						autoStart={formData.autoStart ?? false}
						onChange={(value) => onUpdateForm({ autoStart: value })}
					/>

					<FormActions
						onCancel={onCancel}
						onSubmit={onSubmit}
						isUpdate={isEditMode}
						formData={formData}
					/>
				</div>
			</div>
		);
	},
);

const openDocumentation = async () => {
	try {
		// Open documentation URL in a new window
		await invoke("open_url_in_window", {
			url: "https://docs.openbb.co/desktop/backends",
			title: "Open Data Platform Documentation",
		});
	} catch (err) {
		console.error("Failed to open documentation:", err);
	}
};

const BackendListPanel = memo(
    ({
        backends,
        selectedBackend,
        processingId,
        loading,
        deleteError,
        onCreate,
        onClearDeleteError,
        onSelect,
        onStartStop,
        onDelete,
        onEdit,
        onViewLogs,
        onStatusUpdate,
        environments,
        isEnvLoading,
        onGenerateCertificate,
        searchQuery,
        onSearchChange,
    }: BackendListPanelProps) => {
        // Filter backends based on search query
        const filteredBackends = backends.filter(backend => {
            if (!searchQuery.trim()) return true;

            const query = searchQuery.toLowerCase();
            return (
                backend.name.toLowerCase().includes(query) ||
                backend.command.toLowerCase().includes(query) ||
                backend.environment.toLowerCase().includes(query) ||
                (backend.apiUrl && backend.apiUrl.toLowerCase().includes(query)) ||
                (backend.url && backend.url.toLowerCase().includes(query))
            );
        });

        const [hasScrollbar, setHasScrollbar] = useState(false);
        const scrollContainerRef = useRef<HTMLDivElement>(null);

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
        }, [filteredBackends]);

        return (
            <div className="w-full overflow-hidden">
                <div className="flex-1 overflow-y-auto">
                    <>
                        {loading && backends.length === 0 ? (
                            <div className="flex flex-col items-center justify-center p-4">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-theme-accent mb-3" />
                                <p className="body-xs-regular text-theme-secondary">Loading backend services...</p>
                            </div>
                        ) : !loading && backends.length > 0 ? (
                            // Show header and backends list only when backends exist
                            <div>
                                <div className="mb-3 mt-2">
                                    <div className="flex justify-between items-center">
                                        {/* Search Box */}
                                        <div className="mt-5 w-[250px] shrink-0">
                                            <div className="relative">
                                                <input
                                                    type="text"
                                                    placeholder="Search Backends..."
                                                    value={searchQuery || ""}
                                                    spellCheck={false}
                                                    onChange={(e) => onSearchChange(e.target.value)}
                                                    className="border border-theme text-xs !pl-6 shadow-sm w-full"
                                                />
                                                {searchQuery ? (
                                                    <Tooltip
                                                        content="Clear search query"
                                                        className="tooltip tooltip-theme"
                                                    >
                                                        <button
                                                            type="button"
                                                            onClick={() => onSearchChange("")}
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
                                        <div className="flex items-center gap-2 justify-end relative top-2">
                                            <Tooltip
                                                content="Create a new backend service"
                                                className="tooltip-theme"
                                            >
                                                <Button
                                                    onClick={onCreate}
                                                    variant="secondary"
                                                    className="button-neutral shadow-sm"
                                                    size="sm"
                                                >
                                                    <span className="body-xs-medium text-theme-primary whitespace-nowrap justify-center">New Backend</span>
                                                </Button>
                                            </Tooltip>
                                            <Tooltip
                                                content="Generate a self-signed certificate using OpenSSL."
                                                className="tooltip-theme"
                                            >
                                                <Button
                                                    onClick={onGenerateCertificate}
                                                    variant="secondary"
                                                    className="button button-secondary shadow-sm"
                                                    size="sm"
                                                >
                                                    <span className="body-xs-medium text-theme-primary whitespace-nowrap">Generate Certificate </span>
                                                </Button>
                                            </Tooltip>
                                            <Tooltip
                                                content="Open the documentation for this screen."
                                                className="tooltip-theme"
                                            >
                                                <Button
                                                    onClick={openDocumentation}
                                                    variant="secondary"
                                                    className="button-secondary shadow-sm px-2 py-2 group"
                                                    size="sm"
                                                    data-testid="documentation-button"
                                                >
                                                    <DocumentationIcon className="h-4 w-4 text-[var(--ghost-icon)] group-hover:text-[var(--ghost-icon-hover)]" />
                                                </Button>
                                            </Tooltip>
                                        </div>
                                    </div>
                                </div>

                                {/* Show filtered results or "no results found" message */}
                                {filteredBackends.length === 0 && searchQuery.trim() ? (
                                    <div className="flex flex-col items-center justify-center mt-4">
                                        <div className="text-center">
                                            <CustomIcon
                                                id="search"
                                                className="h-12 w-12 text-theme-muted mb-2 mx-auto"
                                            />
                                            <h3 className="body-md-bold text-theme-secondary mb-2">
                                                No backends found
                                            </h3>
                                            <p className="body-sm-regular text-theme-muted mb-4">
                                                No backend services match your search for "{searchQuery}"
                                            </p>
                                            <Button
                                                onClick={() => onSearchChange("")}
                                                variant="outline"
                                                size="sm"
                                                className="button-outline"
                                            >
                                                <span className="body-xs-medium">Clear Search</span>
                                            </Button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex flex-col justify-between">
                                        <div
                                            ref={scrollContainerRef}
                                            className={`overflow-y-auto max-h-[calc(100vh-13rem)] ${hasScrollbar ? 'pr-2' : ''}`}
                                        >
                                            <div className={`flex-1 gap-0 ${hasScrollbar ? 'mr-2' : ''}`}>
                                                <ul>
                                                    {filteredBackends.map((backend) => (
                                                        <BackendServiceItem
                                                            key={backend.id}
                                                            backend={backend}
                                                            onSelect={onSelect}
                                                            onStartStop={onStartStop}
                                                            onDelete={onDelete}
                                                            isSelected={selectedBackend === backend.id}
                                                            isProcessing={processingId === backend.id}
                                                            onEdit={onEdit}
                                                            onViewLogs={onViewLogs}
                                                            environments={environments}
                                                            isEnvLoading={isEnvLoading}
                                                            onStatusUpdate={onStatusUpdate}
                                                        />
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : backends.length === 0 && !loading ? (
                            // Empty state - no header section - ONLY show when definitely done loading
                            <div className="flex flex-col items-center justify-center p-8 mt-8">
                                <div className="text-center">
                                    <CustomIcon
                                        id="server"
                                        className="h-16 w-16 text-theme-primary mb-4 mx-auto"
                                    />
                                    <h3 className="body-lg-bold text-theme-secondary mb-2">
                                        No backend services found
                                    </h3>
                                    <p className="body-sm-regular text-theme-muted mb-6">
                                        Create your first backend service to get started with running server applications.
                                    </p>
                                    <Tooltip content="Create your first backend service">
                                        <Button
                                            onClick={onCreate}
                                            variant="neutral"
                                            className="button-neutral shadow-sm"
                                            size="md"
                                        >
                                            <span className=" text-nowrap">Create First Backend</span>
                                        </Button>
                                    </Tooltip>
                                </div>
                            </div>
                        ) : null}

                        {deleteError && (
                            <div className="p-3 bg-theme-secondary border border-red-500 rounded text-red-500 body-xs-regular">
                                <p className="mb-2">{deleteError}</p>
                                <Button
                                    onClick={onClearDeleteError}
                                    variant="secondary"
                                    className="button-secondary shadow-sm"
                                >
                                    <span className="body-xs-medium">Dismiss</span>
                                </Button>
                            </div>
                        )}
                    </>
                </div>
            </div>
        );
    }
);

BackendListPanel.displayName = "BackendListPanel";


function loadEnvironmentsFromCache(): Environment[] {
    const cached = localStorage.getItem("env-extensions-cache");
    if (!cached) return [];
    try {
        const cache = JSON.parse(cached);
        return Object.keys(cache).map((name) => ({
            name,
			path: cache[name].path || "",
        }));
    } catch {
        return [];
    }
}


// ============== MAIN COMPONENT ==============
export default function BackendsPage() {
	const isMounted = useRef(true);

	const [showToast, setShowToast] = useState(false);
	const [toastContent, setToastContent] = useState<{
		title: string;
		content: React.ReactNode;
		buttonText: string;
	}>({ title: "", content: <></>, buttonText: "" });

	// Core state
	const [backends, setBackends] = useState<BackendService[]>([]);
	const [selectedBackend, setSelectedBackend] = useState<string | null>(null);
	const [environments, setEnvironments] = useState<Environment[]>([]);

	// UI state
	const [loading, setLoading] = useState(true);
	const [envLoading, setEnvLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [backendToDelete, setBackendToDelete] = useState<string | null>(null);
	const [isDeleting, setIsDeleting] = useState(false);
	const [deleteError, setDeleteError] = useState<string | null>(null);
	const [isCreating, setIsCreating] = useState(false);
	const [isGeneratingCert, setIsGeneratingCert] = useState(false);
	const [processingId, setProcessingId] = useState<string | null>(null);
	const [isEditing, setIsEditing] = useState(false);
	const [searchQuery, setSearchQuery] = useState("");

	// Form data state
	const [formData, setFormData] = useState<BackendFormData>({
		id: "",
		name: "",
		command: "openbb-api",
		envFile: undefined,
		envVars: {},
		apiUrl: "",
		host: "127.0.0.1",
		port: undefined,
		pid: undefined,
		environment: "",
		autoStart: false,
		status: "stopped",
	});

	const [formError, setFormError] = useState<string | null>(null);

	useEffect(() => {
		const unlistenPromise = listen<{ id: string; url: string }>(
			"backend-url-discovered",
			(event) => {
				const { id, url: finalUrl } = event.payload;
				console.log(`Received URL for backend ${id}: ${finalUrl}`);
				setBackends((prevBackends) => {
					const backend = prevBackends.find((b) => b.id === id);
					if (backend) {
						if (
							backend.name === "OpenBB API" &&
							!localStorage.getItem("platform-api-run-once")
						) {
							localStorage.setItem("platform-api-run-once", "true");
							setToastContent({
								title: "Connect Backend with OpenBB Workspace",
								content: (
									<ol className="list-decimal list-inside">
										<li>Sign in to your OpenBB Workspace account.</li>
										<li>Go to the "Apps" tab in the top menu.</li>
										<li>Click on "Connect backend".</li>
										<li>
											Fill in the connection form with the following details:
											<ul className="list-disc list-inside ml-4">
												<li>Name: OpenBB Platform</li>
												<li>URL: {finalUrl}</li>
											</ul>
										</li>
										<li>Click "Test".</li>
										<li>Click "Add" to finalize the integration.</li>
									</ol>
								),
								buttonText: "Check Documentation",
							});
							setShowToast(true);
						}
						if (
							backend.name === "OpenBB MCP" &&
							!localStorage.getItem("platform-mcp-run-once")
						) {
							localStorage.setItem("platform-mcp-run-once", "true");
							setToastContent({
								title: "Connect MCP with OpenBB Workspace",
								content: (
									<ol className="list-decimal list-inside">
										<li>Sign in to your OpenBB Workspace account.</li>
										<li>Go to the Chat on the right side.</li>
										<li>Click on "MCP Tools" button above the chat input.</li>
										<li>Click on "+" in the top-right to open the configuration panel.</li>
										<li>Click on "Add Server".</li>
										<li>
											Fill in the connection form with the following details:
											<ul className="list-disc list-inside ml-4">
												<li>Name: OpenBB MCP</li>
												<li>URL: {finalUrl}</li>
											</ul>
										</li>
										<li>Check the box "Local Server".</li>
										<li>Click "Add" to finalize the integration.</li>
									</ol>
								),
								buttonText: "Check Documentation",
							});
							setShowToast(true);
						}
					}
					return prevBackends.map((b) =>
						b.id === id ? { ...b, apiUrl: finalUrl, url: finalUrl } : b,
					);
				});
			},
		);
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	}, []);

	useEffect(() => {
		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === "Escape" && (isCreating || isEditing)) {
				setIsCreating(false);
				setIsEditing(false);
				setFormError(null);
			}
		};
		window.addEventListener("keydown", handleKeyDown);
		return () => {
			window.removeEventListener("keydown", handleKeyDown);
		};
	}, [isCreating, isEditing]);

	const fetchBackends = useCallback(() => {
		if (!isMounted.current) return;

		// Don't refresh if user is editing
		if (isEditing) return;

		setLoading(true);
		setError(null);

		invoke<BackendService[]>("list_backend_services")
			.then((backendServices) => {
				if (!isMounted.current) return;
				if (backendServices) {
					setBackends(
						backendServices.map((b) => ({
							...b,
							autoStart: b.auto_start ?? b.autoStart ?? false,
							envFile: b.env_file ?? b.envFile,
							envVars: b.envVars,
							apiUrl: b.url ?? b.apiUrl,
						})),
					);
				} else {
					setBackends([]);
				}
			})
			.catch((err) => {
				if (!isMounted.current) return;

				console.error("Failed to fetch backends:", err);
				setError(
					`Failed to load backend services: ${err instanceof Error ? err.message : String(err)}`,
				);
			})
			.finally(() => {
				if (isMounted.current) {
					setLoading(false);
				}
			});
	}, [isEditing]);


	useEffect(() => {
		isMounted.current = true;

		const initialFetch = async () => {
			try {
				setLoading(true);

				// 1. Load environments from localStorage cache
				const cachedEnvs = loadEnvironmentsFromCache();
				setEnvironments(cachedEnvs);

				// 2. Always fetch backends from backend
				const backendServices = await invoke<BackendService[]>("list_backend_services");
				if (!isMounted.current) return;
				setBackends(
					backendServices.map((b) => ({
						...b,
						autoStart: b.auto_start ?? b.autoStart ?? false,
						envFile: b.env_file ?? b.envFile,
						envVars: b.envVars,
						apiUrl: b.url ?? b.apiUrl,
					}))
				);

				// 3. If no environments in cache, fallback to backend (optional)
				if (cachedEnvs.length === 0) {
					const envs = await invoke<Environment[]>("list_conda_environments");
					if (!isMounted.current) return;
					if (Array.isArray(envs)) {
						const filteredEnvs = envs.filter((env) => env.name !== "base");
						setEnvironments(filteredEnvs);
					}
				}
			} catch (err) {
				console.error("Failed to fetch initial data:", err);
				setError(
					`Failed to load initial data: ${err instanceof Error ? err.message : String(err)}`
				);
			} finally {
				if (isMounted.current) {
					setLoading(false);
					setEnvLoading(false);
				}
			}
		};

		initialFetch();

		return () => {
			isMounted.current = false;
		};
	}, []);

	// View logs for a backend service
	const viewBackendLogs = useCallback((id: string) => {
		try {
			console.log(`Opening logs window for backend: ${id}`);

			// Register the process for monitoring
			const processId = `backend-${id}`;
			invoke("register_process_monitoring", { processId })
				.then(() => {
					// Only pass the id parameter - nothing else
					return invoke("open_backend_logs_window", { id });
				})
				.catch((err) => console.error("Failed to view backend logs:", err));
		} catch (err) {
			console.error("Failed to view backend logs:", err);
		}
	}, []);

	// Delete backend
	const handleDeleteBackend = useCallback(
		async (id: string) => {
			if (!id) return;

			try {
				setIsDeleting(true);
				setDeleteError(null);

				await invoke("delete_backend_service", { id });

				setBackendToDelete(null);

				if (selectedBackend === id) {
					setSelectedBackend(null);
				}

				// Refresh the list
				fetchBackends();
			} catch (err) {
				console.error(`Failed to delete backend ${id}:`, err);
				setDeleteError(`Failed to delete backend: ${err}`);
			} finally {
				setIsDeleting(false);
			}
		},
		[fetchBackends, selectedBackend],
	);

	// Start or stop backend service
	const handleStartStop = useCallback(
		async (id: string, action: "start" | "stop") => {
			if (!id) return;

			try {
				setProcessingId(id);

				// If starting a backend, validate the command first
				if (action === "start") {
					const backend = backends.find(b => b.id === id);
					if (backend?.command) {
						const commandValidation = validateCommandInput(backend.command);
						if (!commandValidation.isValid) {
							// Set backend to error state without starting
							setBackends((prevBackends) =>
								prevBackends.map((b) => {
									if (b.id === id) {
										return {
											...b,
											status: "error",
											error: `Dangerous command detected: ${commandValidation.error}`,
										};
									}
									return b;
								}),
							);

							// Update backend in database with error status
							await invoke("update_backend_service", {
								backend: {
									...backend,
									status: "error",
									error: `Dangerous command detected: ${commandValidation.error}`,
								}
							});

							setError(`Cannot start backend: ${commandValidation.error}`);
							return; // Exit early, don't start the backend
						}
					}
				}

				// Update the local state immediately to show the status as "stopping" or "starting"
				setBackends((prevBackends) =>
					prevBackends.map((backend) => {
						if (backend.id === id) {
							return {
								...backend,
								status: action === "start" ? "starting" : "stopping",
							};
						}
						return backend;
					}),
				);

				await invoke(
					action === "start" ? "start_backend_service" : "stop_backend_service",
					{ id },
				);

				// Refresh backends after start/stop
				fetchBackends();
			} catch (err) {
				console.error(`Failed to ${action} backend ${id}:`, err);
				setError(`Failed to ${action} backend service: ${err}`);

				// If there's an error, revert the status by fetching fresh data
				fetchBackends();
			} finally {
				setProcessingId(null); // Ensure processing state is cleared regardless of success/failure
			}
		},
		[backends, fetchBackends],
	);

	// Edit backend
	const onEdit = (id: string) => {
		const backend = backends.find((b) => b.id === id);
		if (backend) {
			setFormData({
				...backend,
				autoStart: backend.auto_start,
			});
			setIsEditing(true);
		}
	};

	const handleStatusUpdate = useCallback((id: string, updates: Partial<BackendService>) => {
		setBackends(prev =>
			prev.map(b =>
				b.id === id ? { ...b, ...updates } : b
			)
		);
	    if (updates.status === "error") {
			setProcessingId(null); // Clear any processing state
			setSelectedBackend(null); // Ensure no backend is selected
		}
	}, []);

	return (
		<div className="w-full h-full">
			{showToast && (
				<div className="fixed top-3 right-3 z-50">
					<Toast
						title={toastContent.title}
						onClose={() => setShowToast(false)}
						buttonText={toastContent.buttonText}
						onButtonClick={() => {
							const url = toastContent.title.includes("MCP")
								? "https://docs.openbb.co/python/quickstart/mcp"
								: "https://docs.openbb.co/python/quickstart/workspace";
							openUrl(url).catch(console.error);
							setShowToast(false);
						}}
					>
						{toastContent.content}
					</Toast>
				</div>
			)}
			{isCreating || isEditing ? (
				// Form View
				<div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center overflow-auto" role="dialog">
					<div className="bg-theme-secondary border border-theme-modal rounded-lg px-5 pt-3 pb-5 max-h-[90vh] w-full max-w-xl overflow-y-auto">
						{/* Header */}
						<div className="flex justify-between items-center mb-2">
							<p className="body-lg-medium text-theme-primary">
								Create New Backend
							</p>
							<Tooltip
								content="Cancel and go back."
								className="tooltip-theme"
							>
								<Button
									variant="ghost"
									onClick={() => {
										setIsCreating(false);
										setIsEditing(false);
										setFormError(null);
									}}
									className="button-ghost"
									size="icon"
								>
									<CustomIcon id="close" className="h-6 w-6" />
								</Button>
							</Tooltip>
						</div>

						{/* Form Content */}
						<div className="flex justify-between items-center">
							<BackendForm
								formData={formData}
								formError={formError}
								onSubmit={() => {
									const backendToSave = {
										id: formData.id,
										name: formData.name,
										command: formData.command,
										host: formData.host,
										port: formData.port,
										envFile: formData.envFile,
										envVars: formData.envVars,
										environment: formData.environment,
										auto_start: formData.autoStart,
										status: formData.status,
										working_directory: formData.working_directory,
										pid: formData.pid,
									};

									const action = isEditing
										? "update_backend_service"
										: "create_backend_service";

									invoke(action, { backend: backendToSave })
										.then(() => {
											window.location.reload();
										})
										.catch((err) => {
											console.error(
												`Failed to ${isEditing ? "update" : "create"} backend:`,
												err,
											);
											setFormError(
												`Failed to ${isEditing ? "update" : "create"} backend: ${err}`,
											);
										});
								}}
								onCancel={() => {
									setIsCreating(false);
									setIsEditing(false);
									setFormError(null);
								}}
								onUpdateForm={(updates) =>
									setFormData((prev) => ({ ...prev, ...updates }))
								}
								onSelectEnvFile={() => {
									invoke<string>("select_file", { filter: "env" })
										.then((file) => setFormData(prev => ({ ...prev, envFile: file })))
										.catch((err) => console.error("Failed to select environment file:", err));
								}}
								onSelectWorkingDirectory={() => {
									invoke<string>("select_directory", {
										prompt: "Select Working Directory for Backend",
									})
										.then((directory) =>
											setFormData((prev) => ({
												...prev,
												working_directory: directory,
											})),
										)
										.catch((err) =>
											console.error("Failed to select working directory:", err),
										);
								}}
								environments={environments}
								isEnvLoading={envLoading}
								isEditMode={isEditing}
							/>
						</div>
					</div>
				</div>
			) : (
				// List View
				<div className="flex flex-col h-full">
					<div>
						<BackendListPanel
							backends={backends}
							selectedBackend={selectedBackend}
							processingId={processingId}
							loading={loading}
							error={error}
							deleteError={deleteError}
							onRefresh={() => fetchBackends()}
							onCreate={() => {
								setFormData(prev => ({
									...prev,
									environment: environments.length > 0 ? environments[0].name : "",
								}));
								setIsCreating(true);
							}}
							onClearError={() => {
								setError(null);
								fetchBackends();
							}}
							onClearDeleteError={() => setDeleteError(null)}
							onSelect={setSelectedBackend}
							onStartStop={handleStartStop}
							onDelete={setBackendToDelete}
							onEdit={onEdit}
							onViewLogs={viewBackendLogs}
							environments={environments}
							isEnvLoading={envLoading}
							onStatusUpdate={handleStatusUpdate}
							onGenerateCertificate={() => setIsGeneratingCert(true)}
							searchQuery={searchQuery}
                            onSearchChange={setSearchQuery}
						/>
					</div>
				</div>
			)}

			{/* Delete Confirmation Modal */}
			{backendToDelete && (
				<DeleteConfirmationModal
					onCancel={() => setBackendToDelete(null)}
					onConfirm={() => handleDeleteBackend(backendToDelete)}
					isLoading={isDeleting}
				/>
			)}

			{isGeneratingCert && (
				<CertificateGenerationModal
					onClose={() => setIsGeneratingCert(false)}
					onDirectorySelect={(callback) => {
						invoke<string>("select_directory", {
							prompt: "Select Output Directory",
						})
							.then((directory) => callback(directory))
							.catch((err) =>
								console.error("Failed to select directory:", err),
							);
					}}
				/>
			)}
		</div>
	);
}

export const Route = createFileRoute("/backends")({
	component: BackendsPage,
});
