import { Button, Tooltip } from "@openbb/ui-pro";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import CustomIcon from "../components/Icon";
import { PythonVersionSelector } from "../components/InstallComponents";

// Installation phase types
type InstallationPhase =
	| "preparing"
	| "downloading"
	| "installing"
	| "version_select"
	| "extension_select"
	| "configuring"
	| "complete"
	| "failed"
	| "cancelling"
	| "cancelled";

interface ExtensionSource {
  packageName: string;
  reprName?: string;
  description?: string;
  credentials?: string[] | [];
  instructions?: string | null;
}

// Helper function to check if an error is just a FutureWarning
const isFutureWarningOnly = (errorMsg: string): boolean => {
	if (!errorMsg) return false;

	// Standard warning patterns that should not be treated as errors
	const warningPatterns = [
		"FutureWarning:",
		"remote_definition` is deprecated",
		"DeprecationWarning:",
		"UserWarning:",
		"PendingDeprecationWarning:",
	];

	// Error patterns that indicate is actually an error, not just a warning
	const errorPatterns = [
		"Error:",
		"ERROR:",
		"failed",
		"Failed to",
		"exit code",
		"Exception:",
		"Could not find",
		"command not found",
	];

	// Check if message contains any warning pattern
	const containsWarning = warningPatterns.some((pattern) =>
		errorMsg.includes(pattern),
	);

	// Check if message contains any error pattern
	const containsError = errorPatterns.some((pattern) =>
		errorMsg.includes(pattern),
	);

	// If message contains warning pattern but no error pattern, it's just a warning
	return containsWarning && !containsError;
};

interface InstallProgress {
	step: string;
	progress: number;
	message: string;
}

interface InstallationStatus {
	phase: string;
	isDownloading: boolean;
	isInstalling: boolean;
	isConfiguring: boolean;
	isComplete: boolean;
	message: string;
}

interface ExtensionCategory {
	id: string;
	name: string;
	description: string;
}

interface Extension {
	id: string;
	name: string;
	description: string;
	category: string;
	credentials?: string[];
	instructions?: string | null;
}

const ExtensionSelector = ({
	searchQuery,
	onSearchQueryChange,
	selectedExtensions,
	setSelectedExtensions,
	customPackages,
	setCustomPackages,
}: {
	searchQuery: string;
	onSearchQueryChange: (query: string) => void;
	selectedExtensions: string[];
	setSelectedExtensions: (extensions: string[] | ((prev: string[]) => string[])) => void;
	customPackages: string[];
	setCustomPackages: (packages: string[] | ((prev: string[]) => string[])) => void;
}) => {
	const [extensions, setExtensions] = useState<Extension[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [activeCategoryTab, setActiveCategoryTab] = useState("provider");

	// Track custom packages
	const [customPackage, setCustomPackage] = useState("");

	// Categories
	const categories: ExtensionCategory[] = [
		{
			id: "provider",
			name: "Data Providers",
			description:
				"Data providers implementing the OpenBB provider interface.",
		},
		{
			id: "router",
			name: "Routers",
			description:
				"API paths and endpoints implementing the OpenBB command interface.",
		},
		{
			id: "other-openbb",
			name: "Others",
			description:
				"Additional OpenBB extensions, including OBBject extensions, that enhance the functionality of the OpenBB platform.",
		},
		{
			id: "extras",
			name: "PyPI Packages",
			description:
				"Add other Python packages to the environment.",
		},
	];

	const extrasExtensions = [
		{
			id: "openbb-cli",
			name: "OpenBB CLI",
			description: "Command line interface for OpenBB",
			category: "other-openbb",
			credentials: [],
		},
		{
			id: "openbb-cookiecutter",
			name: "OpenBB Cookiecutter",
			description: "Template for creating new OpenBB extension projects.",
			category: "other-openbb",
			credentials: [],
		}
	];

	// Add a custom package
	const addCustomPackage = () => {
		if (!customPackage.trim()) return;

		// Avoid duplicates
		if (!customPackages.includes(customPackage.trim())) {
			setCustomPackages((prev) => [...prev, customPackage.trim()]);
		}

		setCustomPackage("");
	};

	// Remove a custom package
	const removeCustomPackage = (pkg: string) => {
		setCustomPackages((prev) => prev.filter((p) => p !== pkg));
	};

	// Load extensions from GitHub
	useEffect(() => {
		const fetchExtensions = async () => {
			setLoading(true);
			try {
				const [providersRes, routersRes, obbjectsRes] = await Promise.all([
					fetch(
						"https://raw.githubusercontent.com/OpenBB-finance/OpenBB/refs/heads/main/assets/extensions/provider.json",
					),
					fetch(
						"https://raw.githubusercontent.com/OpenBB-finance/OpenBB/refs/heads/main/assets/extensions/router.json",
					),
					fetch(
						"https://raw.githubusercontent.com/OpenBB-finance/OpenBB/refs/heads/main/assets/extensions/obbject.json",
					),
				]);

				if (!providersRes.ok || !routersRes.ok || !obbjectsRes.ok) {
					throw new Error("Failed to fetch extensions data");
				}

				const providers = await providersRes.json();
				const routers = await routersRes.json();
				const obbjects = await obbjectsRes.json();

				// Map to common format with categories
				const mappedExtensions: Extension[] = [
					...providers.map((item: ExtensionSource) => ({
						id: item.packageName,
						name: item.reprName || item.packageName,
						description: item.description || "No description available",
						category: "provider",
						credentials: item.credentials || [],
						instructions: item.instructions || null,
					})),
					...routers.map((item: ExtensionSource) => ({
						id: item.packageName,
						name: item.reprName || item.packageName,
						description: item.description || "No description available",
						category: "router",
						credentials: item.credentials || [],
						instructions: item.instructions || null,
					})),
					...obbjects.map((item: ExtensionSource) => ({
						id: item.packageName,
						name: item.reprName || item.packageName,
						description: item.description || "No description available",
						category: "other-openbb",
						credentials: item.credentials || [],
						instructions: item.instructions || null,
					})),
					...extrasExtensions,
				];

				const alwaysInclude = [
					"openbb-fred",
					"openbb-bls",
					"openbb-us-eia",
					"openbb-nasdaq",
					"openbb-fmp",
					"openbb-econdb",
					"openbb-cftc",
					"openbb-congress-gov",
				];

				const defaultIds = Array.from(
					new Set([
						...mappedExtensions
							.filter(
								(ext) =>
									(!ext.credentials || ext.credentials.length === 0) &&
									ext.category !== "extras" && ext.id !== "openbb-cli",
							)
							.map((ext) => ext.id),
						...alwaysInclude,
					]),
				);
				setExtensions(mappedExtensions);
				setSelectedExtensions(defaultIds);
			} catch (err) {
				console.error("Error fetching extensions:", err);
				setError(
					"Failed to load extensions. Please try again or continue without extensions.",
				);
			} finally {
				setLoading(false);
			}
		};

		fetchExtensions();
	}, []);

	// Toggle an extension selection
	const toggleExtension = (id: string) => {
		setSelectedExtensions((prev) =>
			prev.includes(id) ? prev.filter((extId) => extId !== id) : [...prev, id],
		);
	};

	// Select all in a category
	const selectCategory = (categoryId: string) => {
		const categoryExtensionIds = extensions
			.filter((ext) => ext.category === categoryId)
			.map((ext) => ext.id);

		setSelectedExtensions((prev) => {
			// Remove any existing ones from this category
			const filtered = prev.filter((id) => !categoryExtensionIds.includes(id));
			// Add all from this category
			return [...filtered, ...categoryExtensionIds];
		});
	};

	// Clear all in a category
	const clearCategory = (categoryId: string) => {
		const categoryExtensionIds = extensions
			.filter((ext) => ext.category === categoryId)
			.map((ext) => ext.id);

		setSelectedExtensions((prev) =>
			prev.filter((id) => !categoryExtensionIds.includes(id)),
		);
	};

	// Get extensions for a specific category
	const getExtensionsByCategory = (categoryId: string) => {
		return extensions.filter((ext) => ext.category === categoryId);
	};

	// Count selected extensions in a category
	const countSelectedInCategory = (categoryId: string) => {
		const categoryExtensions = getExtensionsByCategory(categoryId);
		const categoryExtensionIds = categoryExtensions.map((ext) => ext.id);

		return selectedExtensions.filter((id) => categoryExtensionIds.includes(id))
			.length;
	};

	const getFilteredExtensions = (categoryId: string) => {
		const categoryExtensions = extensions.filter(
			(ext) => ext.category === categoryId,
		);

		if (!searchQuery.trim()) {
			return categoryExtensions;
		}

		const query = searchQuery.toLowerCase();
		return categoryExtensions.filter(
			(ext) =>
				ext.id.toLowerCase().includes(query) ||
				ext.name.toLowerCase().includes(query) ||
				ext.description.toLowerCase().includes(query),
		);
	};

	const hasMatchingExtensions = (
		extensions: Extension[],
		categoryId: string,
		query: string,
	): boolean => {
		if (!query.trim()) return true; // Always show all tabs when no search
		const categoryExtensions = extensions.filter(
			(ext) => ext.category === categoryId,
		);

		const queryLower = query.toLowerCase();
		return categoryExtensions.some(
			(ext) =>
				ext.id.toLowerCase().includes(queryLower) ||
				ext.name.toLowerCase().includes(queryLower) ||
				ext.description.toLowerCase().includes(queryLower),
		);
	};

	const getCheckboxState = (categoryId: string) => {
		const categoryExtensions = getExtensionsByCategory(categoryId);
		const totalCount = categoryExtensions.length;
		const selectedCount = countSelectedInCategory(categoryId);

		if (selectedCount === 0) return 'checked';
		if (selectedCount === totalCount) return 'indeterminate';
		return 'indeterminate';
	};

	useEffect(() => {
		// If current active tab has no matches, switch to first available tab
		if (
			!hasMatchingExtensions(extensions, activeCategoryTab, searchQuery)
		) {
			const firstMatchingCategory = categories.find((category) =>
				hasMatchingExtensions(extensions, category.id, searchQuery),
			);
			if (firstMatchingCategory) {
				setActiveCategoryTab(firstMatchingCategory.id);
			}
		}
	}, [searchQuery, activeCategoryTab, extensions]);

	return (
		<div className="w-full mt-3 flex flex-col h-full">
			{loading ? (
				<div className="flex justify-center items-center p-8 text-theme-primary">
					<div className="animate-spin rounded-full h-8 w-8 border-theme-color" />
					<span className="ml-2 body-xs-regular text-theme-primary">
						Loading extensions...
					</span>
				</div>
			) : (
				<div className="flex flex-col h-full overflow-auto">
					{/* Tab bar for categories */}
					<div className="flex gap-4 whitespace-nowrap mb-5 border-b-2 border-theme-accent flex-shrink-0">
						{categories
							.filter((category) =>
								hasMatchingExtensions(extensions, category.id, searchQuery),
							)
							.map((category, idx) => (
								<div key={category.id} className="flex items-center">
									<button
										type="button"
										className={`py-1 text-theme transition-colors
                        					${idx === 0 ? "pl-0" : "px-0"}
                        					${
												activeCategoryTab === category.id
													? "body-sm-bold border-b tab-border-active text-theme-accent relative -bottom-0.5"
													: "body-sm-medium text-theme-muted relative -bottom-0.5 "
											}
                        					focus:outline-none
                      					`}
										onClick={() => setActiveCategoryTab(category.id)}
										aria-selected={activeCategoryTab === category.id}
										role="tab"
									>
										{category.name}
									</button>
								</div>
							))}
					</div>

					{/* Category description and select/clear all button */}
					<div className="mb-5 flex justify-between items-center flex-shrink-0">
						<p className="body-sm-regular text-theme-secondary">
							{categories.find((c) => c.id === activeCategoryTab)?.description}
						</p>
					</div>

					{/* Search input */}
					{activeCategoryTab !== "extras" && (
						<div>
							<div className="flex items-center gap-2 flex-shrink-0">
								<div className="flex-1 relative">
									<span className="absolute inset-y-0 left-0 flex items-center pl-2 text-theme-muted">
										<CustomIcon id="search" className="h-4 w-4" />
									</span>
									<input
										id="extension-search"
										type="text"
										placeholder="Search extensions..."
										value={searchQuery}
										onChange={(e) => onSearchQueryChange(e.target.value)}
										className="!pl-[30px] w-full text-xs p-2 bg-theme-secondary rounded overflow-hidden text-ellipsis whitespace-nowrap"
										disabled={loading}
										spellCheck="false"
									/>
								</div>
							</div>
							<div className="mt-3 flex items-center">
								<Tooltip
									content="Deselect all extensions in this category"
									className="tooltip tooltip-theme"
								>
									<input
										type="checkbox"
										checked={(getCheckboxState(activeCategoryTab) === 'checked')}
										onChange={() => {
											if (
												countSelectedInCategory(activeCategoryTab) > 0
											) {
												clearCategory(activeCategoryTab);
											} else {
												selectCategory(activeCategoryTab);
											}
										}}
										className={`checkbox ${getCheckboxState(activeCategoryTab) === 'indeterminate' ? 'indeterminate' : ''}`}
									/>
								</Tooltip>
								{/* Horizontal line inside the checkbox when checked */}
								{/* Select All Button */}
								<Tooltip
									content="Select all extensions in this category."
									className="tooltip tooltip-theme"
								>
									<Button
										variant="ghost"
										onClick={() => selectCategory(activeCategoryTab)}
										className="button-ghost ml-0 body-sm-medium relative -top-0.5"
										size="xs"
									>
										Select All
									</Button>
								</Tooltip>
							</div>
						</div>
					)}

					{/* Only show the active tab's category content */}
					<div className="flex-1 min-h-0 flex flex-col mt-2">
						<div className="flex-1 overflow-y-auto">
							{categories.map((category) => {
								if (category.id !== activeCategoryTab) return null;

								const categoryExtensions = getFilteredExtensions(category.id);

								return (
									<div key={category.id} className="h-full flex flex-col">
										{/* All rows for applicable categories */}
										{category.id === "extras" && (
											<div className="space-y-4 p-1">
												<div className="flex items-end gap-4">
													<div className="flex-1">
														<label
															htmlFor="custom-package"
															className="body-sm-bold text-theme-secondary mb-1 block"
														>
															Package
														</label>
														<input
															id="custom-package"
															type="text"
															placeholder="PyPI Package Name"
															className="form-input text-sm border-theme-accent rounded p-1 w-full body-sm-regular text-theme-primary shadow-md"
															value={customPackage}
															onChange={(e) => setCustomPackage(e.target.value)}
															spellCheck="false"
															onKeyDown={(e) => {
																if (
																	e.key === "Enter" &&
																	customPackage.trim()
																) {
																	e.preventDefault();
																	addCustomPackage();
																}
															}}
														/>
													</div>
													<Button
														type="button"
														onClick={addCustomPackage}
														disabled={!customPackage.trim()}
														variant="primary"
														size="sm"
														className="button-primary"
													>
														Add
													</Button>
												</div>
												{customPackages.length === 0 && (
													<div className="w-full bg-theme-quartary flex flex-1 h-full items-center justify-center rounded-sm shadow-sm border border-theme-modal">
														<div className="body-sm-regular text-theme-muted">
															No PyPI packages added.
														</div>
													</div>
												)}
												{customPackages.length > 0 && (
													<div className="pt-4">
														<div className="flex flex-col space-y-2 max-h-64 overflow-y-auto pr-1">
															{customPackages.map((pkg) => (
																<div
																	key={pkg}
																	className="flex items-center justify-between bg-theme-quartary rounded-sm p-3"
																>
																	<span className="body-sm-regular text-theme-primary">
																		{pkg}
																	</span>
																	<Tooltip
																		content={`Remove ${pkg}`}
																		className="tooltip tooltip-theme"
																	>
																		<Button
																			type="button"
																			variant="ghost"
																			onClick={() => removeCustomPackage(pkg)}
																			className="button-ghost h-5 w-5 p-0"
																			aria-label={`Remove ${pkg}`}
																		>
																			<CustomIcon
																				id="close"
																				className="h-4 w-4 text-theme"
																			/>
																		</Button>
																	</Tooltip>
																</div>
															))}
														</div>
													</div>
												)}
											</div>
										)}
										{categoryExtensions.length === 0 ? (
											category.id !== "extras" && (
												<div className="p-3 body-xs-regular text-theme-muted bg-theme-quartary rounded-sm shadow-sm border border-theme-modal w-full min-h-[65px] flex items-center justify-center">
													{searchQuery.trim()
														? "No extensions in this category match the search."
														: "No extensions available in this category. If they have already been installed, they will not appear here."}
												</div>
											)
										) : (
											<div className="flex flex-col space-y-2 mr-2 pb-4">
												{categoryExtensions.map((extension) => (
													<div
														key={extension.id}
														className="flex items-start justify-between p-2 rounded-sm bg-theme-quartary text-theme-primary relative border border-theme-modal flex-shrink-0"
													>
														<input
															type="checkbox"
															id={`ext-${extension.id}`}
															checked={selectedExtensions.includes(
																extension.id,
															)}
															onChange={() =>
																toggleExtension(extension.id)
															}
															className="checkbox mt-1 h-4 w-4 text-theme-accent flex-shrink-0"
														/>
														<div className="ml-3 w-full min-w-0">
															<div className="flex flex-wrap items-center justify-start gap-4 w-full">
																<label
																	htmlFor={`ext-${extension.id}`}
																	className="text-theme-primary body-md-regular cursor-pointer"
																>
																	{extension.id}
																</label>
																{extension.credentials &&
																	extension.credentials.length > 0 && (
																		<div className="relative inline-block group">
																			<span
																				className="px-2 py-0.5 bg-theme-accent text-theme-accent body-xs-medium rounded-full"
																				title="API key required"
																			>
																				{extension.credentials.join(", ")}
																			</span>
																		</div>
																	)}
															</div>
															<p className="text-theme-secondary body-xs-regular mt-2">
																{extension.description}
															</p>
															{extension.instructions && (
																<div className="bg-theme-primary p-2 mt-2 body-xs-regular text-theme-secondary rounded-sm shadow-sm">
																	<details>
																		<summary className="cursor-pointer text-theme-primary body-xs-medium">
																			Setup instructions
																		</summary>
																		<div className="mt-2 p-2">
																			<ReactMarkdown
																				className="markdown-content whitespace-pre-line"
																				components={{
																					img: ({ ...props }) => (
																						<img
																							{...props}
																							className="max-w-full h-auto border border-theme rounded-md"
																							style={{
																								maxHeight: "300px",
																							}}
																							loading="lazy"
																							alt={
																								props.alt ||
																								"Setup instruction image"
																							}
																						/>
																					),
																					a: ({ ...props }) => (
																						<a
																							{...props}
																							className="text-blue-500 underline"
																							target="_blank"
																							rel="noreferrer noopener"
																						/>
																					),
																					p: ({ ...props }) => (
																						<p
																							{...props}
																							className="my-2 text-theme-secondary"
																						/>
																					),
																					code: ({
																						...props
																					}) => (
																						<code
																							{...props}
																							className="bg-theme-tertiary px-1 py-0.5 rounded text-theme-primary"
																						/>
																					),
																					div: ({ ...props }) => (
																						<div {...props} />
																					),
																				}}
																			>
																				{extension.instructions}
																			</ReactMarkdown>
																		</div>
																	</details>
																</div>
															)}
														</div>
													</div>
												))}
											</div>
										)}
									</div>
								);
							})}
						</div>
					</div>

					{/* Global Summary */}
					<div className="flex items-center justify-between flex-shrink-0 mt-3 pt-4 border-t border-theme-accent">
						<div className="flex items-center gap-2">
							<span className="body-xs-regular text-theme-muted flex items-center mb-5">
								{customPackages.length} PyPI + {selectedExtensions.length}{" "}
								OpenBB extensions selected
							</span>
						</div>
					</div>
				</div>
			)}
			{error && (
				<div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center">
					<div className="bg-theme-secondary border-red-800 rounded-lg shadow-lg max-w-2xl w-full p-6">
						<h2 className="text-red-600 text-lg font-bold mb-2">
							Extension Error
						</h2>
						<div className="mb-4 mt-4 pl-5 pt-1 pr-1 pb-1 border-red-800 bg-red-900/30 text-red-300 rounded-md text-xs font-mono">
							<div className="whitespace-pre-wrap overflow-auto max-h-60 mt-0.5 mb-0.5">
								{error}
							</div>
						</div>
						<div className="flex justify-end">
							<Button
								onClick={() => setError(null)}
								variant="outline"
								size="sm"
								className="button-outline shadow-md"
							>
								<span className="body-xs-bold text-theme">Dismiss</span>
							</Button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
};

export default function InstallationProgress() {
	const navigate = useNavigate();

	const params = new URLSearchParams(window.location.search);
	const directory = params.get("directory") || undefined;
	const userDataDir = params.get("userDataDir") || undefined;

	// Track the current installation phase
	const [phase, setPhase] = useState<InstallationPhase>("preparing");
	const [message, setMessage] = useState("Preparing installation");
	const [ellipsis, setEllipsis] = useState("");
	const [isComplete, setIsComplete] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [isCancelling, setIsCancelling] = useState(false);
	const [selectedVersion, setSelectedVersion] = useState<string | null>(null);
	const [isContinuing, setIsContinuing] = useState(false);

	// State for extension selection
	const [selectedExtensions, setSelectedExtensions] = useState<string[]>([]);
	const [customPackages, setCustomPackages] = useState<string[]>([]);

	// Reference for the interval timer
	const ellipsisTimerRef = useRef<NodeJS.Timeout | null>(null);
	const statusCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
	const installationStartedRef = useRef(false);
	const [extensionSearchQuery, setExtensionSearchQuery] = useState("");

	// Animate the ellipsis
	useEffect(() => {
		if (
			phase !== "complete" &&
			phase !== "failed" &&
			phase !== "cancelled" &&
			phase !== "version_select" &&
			phase !== "extension_select" &&
			!error
		) {
			// Clear any existing interval first to prevent multiple intervals
			if (ellipsisTimerRef.current) {
				clearInterval(ellipsisTimerRef.current);
			}

			// Start with empty ellipsis
			setEllipsis("");

			// Create a new interval
			ellipsisTimerRef.current = setInterval(() => {
				setEllipsis((prev) => {
					// Ensure we have proper cycling between states
					switch (prev) {
						case "":
							return ".";
						case ".":
							return "..";
						case "..":
							return "...";
						case "...":
							return ""; // Reset to empty instead of adding more dots
						default:
							return ""; // Safety case to reset if we get in a bad state
					}
				});
			}, 500);
		} else if (ellipsisTimerRef.current) {
			clearInterval(ellipsisTimerRef.current);
		}

		return () => {
			if (ellipsisTimerRef.current) {
				clearInterval(ellipsisTimerRef.current);
			}
		};
	}, [phase, error]);

	// Listen for progress updates from the backend
	useEffect(() => {
		let unlistenFunc: (() => void) | undefined;

		const installConda = async () => {
			try {
				// Set up event listener for progress updates
				try {
					unlistenFunc = await listen<InstallProgress>(
						"install-progress",
						(event) => {
							console.log("Installation progress update:", event);

							// Don't update the UI if we're cancelling
							if (isCancelling) return;

							const payload = event.payload;

							// Update phase based on the step from backend
							const step = payload.step.toLowerCase();
							const message = payload.message || "";

							if (
								step.includes("install") &&
								(message.includes("Miniforge installation completed") ||
									(message.includes("completed") && phase === "installing"))
							) {
								console.log(
									"Miniforge installation finished, moving to Python version selection",
								);
								setPhase("version_select");
								setMessage("Select Python version");

								// Pause status checks until version is selected and Next is clicked
								if (statusCheckIntervalRef.current) {
									clearInterval(statusCheckIntervalRef.current);
									statusCheckIntervalRef.current = null;
								}

								return;
							}

							if (
								step.includes("config") &&
								message.includes("environment set up successfully")
							) {
								console.log(
									"Python environment setup completed, moving to extension selection",
								);
								setPhase("extension_select");
								setMessage("Select extensions to install");

								// Pause status checks until extensions are selected
								if (statusCheckIntervalRef.current) {
									clearInterval(statusCheckIntervalRef.current);
									statusCheckIntervalRef.current = null;
								}

								return;
							}

							if (step.includes("download")) {
								setPhase("downloading");
								setMessage(payload.message || "Downloading Miniforge");
							} else if (step.includes("install")) {
								setPhase("installing");
								setMessage(payload.message || "Installing Miniforge");
							} else if (step.includes("config")) {
								setPhase("configuring");
								setMessage(payload.message || "Configuring OpenBB environment");
							} else if (step.includes("complete")) {
								const fullProcessComplete =
									message.includes("Installation completed successfully") ||
									message
										.toLowerCase()
										.includes("openbb installation complete");

								if (fullProcessComplete) {
									setPhase("complete");
									setMessage(
										payload.message || "Installation completed successfully",
									);
									setIsComplete(true);
									if (ellipsisTimerRef.current) {
										clearInterval(ellipsisTimerRef.current);
									}
									if (statusCheckIntervalRef.current) {
										clearInterval(statusCheckIntervalRef.current);
										statusCheckIntervalRef.current = null;
									}
								} else {
									// This is just a sub-component completion, don't mark the whole process as complete
									console.log(
										"Sub-component completion detected, not marking as fully complete",
									);
									setMessage(payload.message || "Installation in progress");
								}
							}
						},
					);
					console.log("Successfully set up event listener");
				} catch (eventError) {
					console.error("Failed to set up event listener:", eventError);
					// Continue without event updates, will rely on status checks
				}

				// Start with downloading phase
				setPhase("downloading");
				setMessage("Downloading Miniforge");

				// Set up status check interval
				if (statusCheckIntervalRef.current) {
					clearInterval(statusCheckIntervalRef.current);
				}
				statusCheckIntervalRef.current = setInterval(
					checkInstallationStatus,
					2000,
				);

				try {
					console.log(
						"Starting Conda installation with invoke at:",
						new Date().toISOString(),
					);
					// Start the actual installation
					await invoke("install_conda", {
						directory,
						userDataDir,
					});

					console.log(
						"Conda installation completed at:",
						new Date().toISOString(),
					);

					// Don't update the UI if we're cancelling
					if (isCancelling) return;

					// If no event was fired to trigger version selection, do it now
					if (
						phase !== "version_select" &&
						phase !== "configuring" &&
						phase !== "complete"
					) {
						console.log(
							"No version selection event detected, moving to version selection now",
						);
						setPhase("version_select");
						setMessage("Select Python version");

						// Pause status checks until version is selected
						if (statusCheckIntervalRef.current) {
							clearInterval(statusCheckIntervalRef.current);
							statusCheckIntervalRef.current = null;
						}
					}
				} catch (invokeError) {
					console.error("Invoke error:", invokeError);
					let errorMsg = "";
					if (typeof invokeError === "string") {
						errorMsg = invokeError;
					} else if (invokeError instanceof Error) {
						errorMsg = invokeError.message;
					} else {
						errorMsg = String(invokeError);
					}

					// Handle "already in progress" error
					if (errorMsg.includes("already in progress")) {
						console.log(
							"Installation already in progress, switching to monitoring mode",
						);
						// Continue monitoring instead of showing an error
						return;
					}

					// Clear any intervals/timeouts
					if (ellipsisTimerRef.current) {
						clearInterval(ellipsisTimerRef.current);
					}
					if (statusCheckIntervalRef.current) {
						clearInterval(statusCheckIntervalRef.current);
						statusCheckIntervalRef.current = null;
					}

					// Don't update the UI if we're cancelling
					if (isCancelling) return;

					setError(`Installation failed: ${errorMsg}`);
					setPhase("failed");
				}
			} catch (error) {
				console.error("General error:", error);
				if (ellipsisTimerRef.current) {
					clearInterval(ellipsisTimerRef.current);
				}
				if (statusCheckIntervalRef.current) {
					clearInterval(statusCheckIntervalRef.current);
					statusCheckIntervalRef.current = null;
				}

				// Don't update the UI if we're cancelling
				if (isCancelling) return;

				console.error("Installation failed:", error);
				setError(`Installation failed: ${error}`);
				setPhase("failed");
			}
		};

		if (directory && !installationStartedRef.current) {
			installationStartedRef.current = true;
			installConda();
		} else if (directory) {
			// If installation was already started, just set up status checking
			if (statusCheckIntervalRef.current) {
				clearInterval(statusCheckIntervalRef.current);
			}
			statusCheckIntervalRef.current = setInterval(
				checkInstallationStatus,
				2000,
			);
			// Run status check once immediately
			checkInstallationStatus();
		}

		// Cleanup the event listener when component unmounts
		return () => {
			if (unlistenFunc) {
				unlistenFunc();
			}
			if (ellipsisTimerRef.current) {
				clearInterval(ellipsisTimerRef.current);
			}
			if (statusCheckIntervalRef.current) {
				clearInterval(statusCheckIntervalRef.current);
				statusCheckIntervalRef.current = null;
			}
		};
	}, [directory, userDataDir, isCancelling]);

	// Function to check installation status
	const checkInstallationStatus = async () => {
		if (isCancelling) return;

		try {
			const status: InstallationStatus = await invoke(
				"get_installation_status",
			);
			console.log("Installation status check:", status);

			// Don't update UI if waiting for user input
			if (phase === "version_select" || phase === "extension_select") return;

			// Update UI based on actual installation status
			if (status.isComplete) {
				// Only show complete if the message indicates full installation completion
				const fullProcessComplete =
					status.message.includes("Installation completed successfully") ||
					status.message.toLowerCase().includes("openbb installation complete");

				if (fullProcessComplete) {
					setPhase("complete");
					setMessage(status.message || "Installation completed successfully");
					setIsComplete(true);

					// Clear interval since installation is complete
					if (statusCheckIntervalRef.current) {
						clearInterval(statusCheckIntervalRef.current);
						statusCheckIntervalRef.current = null;
					}
				} else {
					// This might be a sub-component completion - continue showing progress
					// For example, "Miniforge installation completed" shouldn't mark the whole process as complete
					console.log(
						"Sub-component completion detected in status check, continuing installation",
					);
				}
			} else if (status.isConfiguring) {
				setPhase("configuring");
				setMessage(status.message || "Configuring OpenBB environment");
			} else if (status.isInstalling) {
				setPhase("installing");
				setMessage(status.message || "Installing Miniforge");
			} else if (status.isDownloading) {
				setPhase("downloading");
				setMessage(status.message || "Downloading Miniforge");
			}
		} catch (error) {
			console.error("Failed to check installation status:", error);
		}
	};

	// Handle Python version selection
	const handleVersionSelect = async (version: string) => {
		setSelectedVersion(version);
	};

	const handleVersionNext = async () => {
		if (selectedVersion) {
			setPhase("configuring");
			setMessage(`Configuring OpenBB with Python ${selectedVersion}`);

			try {
				// Call the backend to continue installation
				await invoke("setup_python_environment", {
					directory,
					pythonVersion: selectedVersion,
				});

				// After Python environment setup, show extension selection
				setPhase("extension_select");
				setMessage("Select extensions to install");

			// Don't resume status checks until extensions are selected
			} catch (error) {
				console.error("Failed to set up Python environment:", error);
				setError(`Failed to set up Python ${selectedVersion}: ${error}`);
				setPhase("failed");
			}
		}
	};

	// Handle extension installation
	const handleInstallExtensions = async () => {
		const allPackages = [...selectedExtensions, ...customPackages];
		if (allPackages.length === 0) {
			// If no extensions selected, just mark as complete
			setPhase("complete");
			setMessage("Installation completed successfully");
			setIsComplete(true);
			return;
		}

		setPhase("configuring");
		setMessage(`Installing ${allPackages.length} extensions`);

		try {
			// Call the backend to install the selected extensions
			await invoke("install_extensions", {
				extensions: allPackages,
				environment: "openbb",
				directory: directory,
			});
		    await invoke("execute_in_environment", {
				command: "openbb-build",
				environment: "openbb",
				directory: directory,
			});
			await invoke("update_openbb_settings", {
				condaDir: directory,
				environment: "openbb",
			});

			// After extensions are installed, mark as complete
			setPhase("complete");
			setMessage("Installation completed successfully");
			setIsComplete(true);
		} catch (err) {
			const errMsg = String(err);
			// Use the isFutureWarningOnly helper function to check if this is just a warning
			if (!isFutureWarningOnly(errMsg)) {
				setError(`Failed to install extensions: ${errMsg}`);
				setPhase("failed");
			} else {
				// Only warnings (e.g. FutureWarning), treat as success
				setPhase("complete");
				setMessage("Installation completed successfully");
				setIsComplete(true);
			}
		}
	};

	// Handle skip extensions
	const handleSkipExtensions = () => {
		setSelectedExtensions([]);
		setCustomPackages([]);
		setPhase("complete");
		setMessage("Installation completed successfully");
		setIsComplete(true);
	};

	// Handle completion - continue to app (only for successful installations)
	const handleContinue = async () => {
		setIsContinuing(true);
		// Instead of using navigate, use window.location to force a full page reload
		// This ensures the installation state is properly recognized
		const searchParams = new URLSearchParams();
		if (directory) searchParams.append("directory", directory);
		if (userDataDir) searchParams.append("userDataDir", userDataDir);

		const queryString = searchParams.toString();

		try {
			await invoke("update_openbb_settings", {
				condaDir: directory,
				environment: "openbb",
			});
		} catch (error) {
			console.error("Failed to update OpenBB settings:", error);
			// Proceed to app even if this fails
		}

		// Create default backend services only on successful installation
		try {
			await invoke("create_default_backend_services");
		} catch (error) {
			console.error("Failed to create default backend services:", error);
			// Proceed to app even if this fails
		}

		window.localStorage.setItem("environments-first-load-done", "true");
		window.location.href = `/environments${queryString ? `?${queryString}` : ""}`;
	};

	// Handle "Continue Anyway" when installation has failed
	// This skips settings updates since the environment may be incomplete
	const handleContinueAnyway = () => {
		setIsContinuing(true);
		const searchParams = new URLSearchParams();
		if (directory) searchParams.append("directory", directory);
		if (userDataDir) searchParams.append("userDataDir", userDataDir);

		const queryString = searchParams.toString();

		// Don't update settings or create backend configs for failed installations
		// Just navigate to environments so user can see what's available
		console.warn("Continuing after failed installation - settings not updated");
		window.localStorage.setItem("environments-first-load-done", "true");
		window.location.href = `/environments${queryString ? `?${queryString}` : ""}`;
	};

	// Handle error - try again
	const handleTryAgain = () => {
		setPhase("preparing");
		window.localStorage.clear();
		window.location.href = "/setup";
	};

	// Handle cancellation
	const handleCancel = async () => {
		try {
			// Set cancelling state to prevent UI updates from the installation process
			setIsCancelling(true);
			setPhase("cancelling");
			setMessage("Cancelling installation");

			console.log("Cancelling installation at:", new Date().toISOString());

			// Clear status check interval
			if (statusCheckIntervalRef.current) {
				clearInterval(statusCheckIntervalRef.current);
				statusCheckIntervalRef.current = null;
			}

			// Call the backend to abort the installation and clean up
			await invoke("abort_installation", { directory });

			console.log("Installation cancelled at:", new Date().toISOString());

			// Update UI to show cancelled state
			setPhase("cancelled");
			setMessage("Installation cancelled");
			setError(null);
			setIsCancelling(false);

		} catch (error) {
			console.error("Failed to cancel installation:", error);
			// Still try to navigate back to setup
			handleTryAgain();
		}
	};

	const handleCancelExtensionInstall = () => {
		// Stop the current installation process and return to extension selection
		setPhase("extension_select");
		setMessage("Select extensions to install");
		setError(null); // Clear any error state
		setIsCancelling(false);
	};


	return (
		<div className="pt-6 w-full flex flex-col h-full">
			{(
				phase === "version_select"
				|| message.includes("Updating")
				|| message.includes("Initializing")
				|| message.includes("OpenBB package")
			) && !error && (
				<div>
					<p className="text-theme-secondary body-xs-regular">
						STEP <span className="text-theme-accent">2</span> OF <span className="text-theme-accent">3</span>
					</p>
				</div>
			)}

			{(phase === "extension_select" || (phase ==="configuring" && message.includes("extensions"))) && !error && (
				<div>
					<p className="text-theme-secondary body-xs-regular">
						STEP <span className="text-theme-accent">3</span> OF <span className="text-theme-accent">3</span>
					</p>
				</div>
			)}

			{(message.includes("Miniforge") || message.includes("architecture") || message.includes("Conda")) && !isComplete && !error && (
				<div>
					<p className="text-theme-secondary body-xs-regular">
						STEP <span className="text-theme-accent">1</span> OF <span className="text-theme-accent">3</span>
					</p>
				</div>
			)}
          	<h1 className="body-xl-bold mb-5 text-theme-primary">Installation & Setup</h1>

			{(phase !== "extension_select" &&phase !== "cancelled") && (
				<div>
					<div className="justify-left flex items-left body-sm-regular text-theme-primary">
						<p>Initial installation includes the following components:</p><br />
					</div>
					<div className="ml-2 body-sm-regular justify-left flex items-left pb-7">
						<ul className="list-disc list-inside mt-1 mb-1 ml-3">
							<li>Miniforge (Python environment manager)</li>
							<li>OpenBB environment with core libraries & dependencies</li>
							<li>iPython & Jupyter Lab</li>
						</ul>
					</div>
				</div>
			)}

			{phase === "extension_select" && !error && (
				<div>
					<div className="flex items-center justify-between gap-4">
				<div className="flex-1">
					<p className="mb-5 body-md-regular text-theme-secondary">
						Select OpenBB extensions to install, and add additional PyPI packages.
					</p>
				</div>
					</div>
				</div>
			)}

			{/* Progress bar */}

			<div
				className={`rounded-sm shadow-sm bg-theme-tertiary border border-theme-modal pr-2 pl-4 ${
					phase === "extension_select" ? "flex-1 flex flex-col min-h-0" : "overflow-y-hidden"
				}`}
			>
				{/* Python version selector */}
				{phase === "version_select" && !error && (
					<div className="w-full pt-3">
						<PythonVersionSelector
							onSelectVersion={handleVersionSelect}
						/>
					</div>
				)}
				{phase === "cancelled" &&
					!error &&
					isComplete && (
						<Button
							variant="outline"
							size="sm"
							onClick={handleCancelExtensionInstall}
							className="button-outline px-2 py-1"
						>
							Back to Extensions
						</Button>
					)}
				{phase === "extension_select" && !error && (
					<ExtensionSelector
						searchQuery={extensionSearchQuery}
						onSearchQueryChange={setExtensionSearchQuery}
						selectedExtensions={selectedExtensions}
						setSelectedExtensions={setSelectedExtensions}
						customPackages={customPackages}
						setCustomPackages={setCustomPackages}
					/>
				)}

				{/* Only show status section if not in selection phases and haven't encountered an error */}
				{!error &&
					phase !== "complete" &&
					phase !== "cancelled" &&
					phase !== "version_select" &&
					phase !== "extension_select" && (
						<div className="mb-4 mt-4 p-2">
							<div className="flex justify-between items-center">
								<span className="text-theme-primary">
									{message}
									{ellipsis}
								</span>
								{/* Cancel button - only show during active installation */}
								{(phase === "downloading" ||
									phase === "installing" ||
									phase === "configuring") &&

									!error &&
									!isComplete && (
										<Button
											variant="danger"
											size="sm"
											onClick={handleCancel}
											disabled={isCancelling}
											className="button-danger px-2 py-1"
										>
											{isCancelling ? "Cancelling..." : "Cancel"}
										</Button>
									)}
							</div>
						</div>
					)}

				{/* Cancelled state message */}
				{phase === "cancelled" && (
					<div className="pt-5 px-2 pb-5 bg-theme-tertiary text-theme-primary rounded-md">
						<p className="font-semibold">Installation cancelled</p>
						<p className="mt-2 body-sm-regular text-theme-secondary">
							The installation process has been cancelled and any partial files
							have been cleaned up.
						</p>
					</div>
				)}

				{/* Success message */}
                {isComplete && !error && (
                    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center">
                        <div className="flex-1 bg-theme-secondary border border-theme-modal rounded-lg shadow-lg min-w-[60vw] max-w-[50vw] w-full pt-3 mb-5 max-h-[95vh]">
                            <div className="flex justify-between items-center mb-2">
                                <h2 className="text-theme-primary body-md-bold pl-4">
                                    Installation completed successfully!
                                </h2>
                                <Button
                                    variant="ghost"
                                    onClick={handleContinue}
									size="sm"
                                    className="button-ghost"
                                    aria-label="Close"
                                >
                                    <CustomIcon id="close" className="h-6 w-6" />
                                </Button>
                            </div>
                            <div className="mb-6 px-4">
                                <p className="text-theme-secondary body-sm-regular mb-3">
                                    OpenBB has been installed to: {directory}
                                </p>
                                {selectedVersion && (
                                    <p className="text-theme-secondary body-sm-regular mb-1">
                                        <span className="font-bold">Python version:</span> <span>{selectedVersion}</span>
                                    </p>
                                )}
                                {selectedExtensions.length > 0 && (
                                    <div className="text-theme-secondary">
                                        <span className="body-sm-bold">Extensions:</span>
                                        <div className="mt-2 min-h-0 max-h-[40vh] overflow-y-auto">
                                            <div className="text-theme-primary body-xs-regular bg-theme-primary p-2 rounded-sm shadow-sm">
                                                {selectedExtensions.join(", ")}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            <div className="flex justify-end pt-5 items-center">
                                <Button
                                    className="button-primary shadow-md"
                                    onClick={handleContinue}
                                    size="sm"
                                    variant="primary"
                                    disabled={isContinuing}
                                >
									Done
                                </Button>
                            </div>
                        </div>
                    </div>
				</div>
                )}

				{/* Error message */}
				{error && phase !== "cancelled" && phase !== "cancelling" && (
					<div className="mt-4 mb-4 p-4 bg-red-900/30 text-red-300 rounded-md">
						<p className="body-md-bold">Installation failed</p>
						<p className="mt-2 body-sm-regular overflow-auto max-h-40">{error}</p>
						<p className="mt-3 body-xs-regular text-theme-secondary">
							For common installation issues (permissions, missing compilers, etc.), see the{" "}
							<a
								href="https://docs.openbb.co/odp/desktop/troubleshooting"
								target="_blank"
								rel="noopener noreferrer"
								className="text-blue-400 hover:text-blue-300 underline"
							>
								troubleshooting guide
							</a>.
						</p>
						<div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-600/30 rounded-md">
							<p className="body-xs-bold text-yellow-300">What happens if you continue?</p>
							<ul className="mt-2 body-xs-regular text-yellow-200/80 list-disc list-inside space-y-1">
								<li>The environment may be incomplete or non-functional</li>
								<li>Default backend services (OpenBB API, MCP) will not be configured</li>
								<li>You may need to manually set up the environment later</li>
							</ul>
						</div>
						<div className="mt-4 flex gap-2 justify-end">
							<Button
								variant="secondary"
								onClick={handleContinueAnyway}
								className="button-secondary px-2 py-1"
								size="sm"
							>
								Continue Anyway
							</Button>
							<Button
								variant="destructive"
								onClick={handleTryAgain}
								className="button-danger px-2 py-1"
								size="sm"
							>
								Try Again
							</Button>
						</div>
					</div>
				)}
			</div>
		{phase === "version_select" && !error && (
			<div className="flex justify-end gap-2 mt-7">
				<Button
					variant="outline"
					size="sm"
					className="button-outline px-2 py-1"
					onClick={handleCancel}
				>
					Cancel
				</Button>
				<Button
					variant="neutral"
					size="sm"
					className="button-neutral px-2 py-1 mr-1"
					onClick={handleVersionNext}
				>
					Next Step
				</Button>
			</div>
		)}
		{phase === "cancelled" && !isComplete && (
			<div className="mt-3 flex justify-end">
				<Button
					className="mt-4 button-primary whitespace-nowrap px-2 py-1"
					variant="primary"
					onClick={() => navigate({ to: "/setup" })}
					size="sm"
				>
					Return to Setup
				</Button>
			</div>
		)}
			{phase === "extension_select" && !error && (
				<div className="pt-5">
					{/* Install/Skip Buttons */}
					<div className="flex items-center justify-end gap-4">
						{/* Skip and Install buttons */}
						<Tooltip
							content="Skip and install later."
							className="tooltip-theme"
						>
							<Button
								onClick={handleSkipExtensions}
								variant="outline"
								size="sm"
								className="button-outline shadow-md px-2 py-1"
							>
								Skip
							</Button>
						</Tooltip>
						<Tooltip
							content="Install the selected extensions."
							className="tooltip-theme"
						>
							<Button
								onClick={handleInstallExtensions}
								variant="neutral"
								size="sm"
								className="button-neutral shadow-md px-2 py-1"
								disabled={
									selectedExtensions.length === 0 && customPackages.length === 0
								}
							>
								Install
							</Button>
						</Tooltip>
					</div>
				</div>
			)}
		</div>
	);
}

export const Route = createFileRoute("/installation-progress")({
	component: InstallationProgress,
});
