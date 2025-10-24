import { Button, Tooltip } from "@openbb/ui-pro";
import { createFileRoute } from "@tanstack/react-router";
import { invoke } from "@tauri-apps/api/core";
import { message } from "@tauri-apps/plugin-dialog";
import { useEffect, useMemo, useRef, useState } from "react";
import CustomIcon, { CopyIcon, DocumentationIcon, FileIcon } from "../components/Icon";

interface ApiKey {
	key: string;
	value: string;
	required: boolean;
}

type UserCredentialsResult = {
  credentials?: Record<string, string | null | undefined>;
};

export default function ApiKeysPage() {
	// State management
	const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [isAddKeyModalOpen, setIsAddKeyModalOpen] = useState(false);
	const [editingKeyIndex, setEditingKeyIndex] = useState<number | null>(null);
	const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
	const [searchQuery, setSearchQuery] = useState("");
	const [copiedKey, setCopiedKey] = useState<string | null>(null);
	const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
	const [selectedSettingsFile, setSelectedSettingsFile] = useState<
		'user_settings.json' | 'system_settings.json' | 'mcp_settings.json' | '.env' | '.condarc'
	>('user_settings.json');
	const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());
	const [isModalValueVisible, setIsModalValueVisible] = useState(false);
	const [modalCopied, setModalCopied] = useState(false);
	const [newKey, setNewKey] = useState({ key: "", value: "" });
	const [isImportConfirmModalOpen, setIsImportConfirmModalOpen] = useState(false);
	const [importedKeys, setImportedKeys] = useState<ApiKey[]>([]);
	const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());
	const [importVisibleKeys, setImportVisibleKeys] = useState<Set<string>>(new Set());
	const fileInputRef = useRef<HTMLInputElement>(null);
	const headerRef = useRef<HTMLDivElement>(null);
	const scrollContainerRef = useRef<HTMLDivElement>(null);
	const contentRef = useRef<HTMLDivElement>(null);

	// Parse imported files (.env or .json)
	const parseImportedFile = async (file: File) => {
		try {
			const text = await file.text();
			const extension = file.name.split(".").pop()?.toLowerCase();
			const newKeys: ApiKey[] = [];

			if (extension === "json") {
				// Parse JSON file
				try {
					const jsonData = JSON.parse(text);

					// Handle credential objects from OpenBB settings
					if (
						jsonData.credentials &&
						typeof jsonData.credentials === "object"
					) {
						Object.entries(jsonData.credentials).forEach(([key, value]) => {
							if (
								typeof key === "string" &&
								value !== null &&
								value !== undefined
							) {
								newKeys.push({
									key,
									value: String(value),
									required: false,
								});
							}
						});
					} else {
						// Handle flat JSON objects
						Object.entries(jsonData).forEach(([key, value]) => {
							if (
								typeof key === "string" &&
								value !== null &&
								value !== undefined
							) {
								newKeys.push({
									key,
									value: String(value),
									required: false,
								});
							}
						});
					}
				} catch (e) {
					throw new Error(`Invalid JSON file: ${e}`);
				}
			} else if (extension === "env") {
				// Parse .env file
				const lines = text.split("\n");

				for (const line of lines) {
					const trimmedLine = line.trim();
					if (trimmedLine && !trimmedLine.startsWith("#")) {
						// Look for KEY=VALUE or KEY="VALUE" patterns
						const match = trimmedLine.match(/^([^=]+)=(.*)$/);
						if (match) {
							let [, key, value] = match;
							key = key.trim();
							value = value.trim();

							// Remove surrounding quotes if present
							if (
								(value.startsWith('"') && value.endsWith('"')) ||
								(value.startsWith("'") && value.endsWith("'"))
							) {
								value = value.slice(1, -1);
							}

							newKeys.push({
								key,
								value,
								required: false,
							});
						}
					}
				}
			} else {
				throw new Error(
					"Unsupported file format. Please use .json or .env files.",
				);
			}

			if (newKeys.length > 0) {
				setImportedKeys(newKeys);
				setSelectedKeys(new Set(newKeys.map((k) => k.key))); // Pre-select all
				setIsImportConfirmModalOpen(true);
			} else {
				setError("No new keys found in the imported file.");
			}
		} catch (err) {
			console.error("Error parsing file:", err);
			setError(
				`Error parsing file: ${err instanceof Error ? err.message : String(err)}`,
			);
		}
	};

	// Copy value to clipboard
	const copyToClipboard = (value: string, keyName: string) => {
		navigator.clipboard
			.writeText(value)
			.then(() => {
				setCopiedKey(keyName);
				// Reset copied state after 2 seconds
				setTimeout(() => setCopiedKey(null), 2000);
			})
			.catch((err) => {
				console.error("Failed to copy text: ", err);
				setError("Failed to copy to clipboard");
			});
	};

	const copyModalValueToClipboard = () => {
		if (!newKey.value) return;
		navigator.clipboard
			.writeText(newKey.value)
			.then(() => {
				setModalCopied(true);
				setTimeout(() => setModalCopied(false), 2000);
			})
			.catch((err) => {
				console.error("Failed to copy text: ", err);
				setError("Failed to copy to clipboard");
			});
	};

	const loadData = async () => {
		try {
			setLoading(true);
			setError(null);

			// Get user settings to access credentials
			const userSettings = await invoke<UserCredentialsResult>("get_user_credentials");

			// Format existing keys
			const credentials = userSettings.credentials || {};
			const formattedKeys: ApiKey[] = Object.entries(credentials).map(
				([key, value]) => ({
					key,
					value: value === null ? "" : String(value),
					required: false,
				}),
			);

			setApiKeys(formattedKeys);
		} catch (err) {
			console.error("Failed to load API keys:", err);
			setError(`Failed to load API keys: ${err}`);
		} finally {
			setLoading(false);
		}
	};

	// Load API keys on component mount
	useEffect(() => {
		loadData();
	}, []);

	// Filter API keys based on search query
	const filteredApiKeys = useMemo(() => {
		if (!searchQuery.trim()) return apiKeys;

		const query = searchQuery.toLowerCase();
		return apiKeys.filter((key) => key.key.toLowerCase().includes(query));
	}, [apiKeys, searchQuery]);


	const handleSaveKey = async () => {
		if (!newKey.key.trim()) {
			setError("API Key Name is required.");
			return;
		}

		let updatedKeys: ApiKey[];
		if (modalMode === 'edit' && editingKeyIndex !== null) {
			// Edit existing key
			updatedKeys = [...apiKeys];
			updatedKeys[editingKeyIndex] = { ...newKey, required: false };
		} else {
			// Add new key - check for duplicates only when adding
			if (apiKeys.some((k) => k.key.toLowerCase() === newKey.key.toLowerCase())) {
				setError("An API key with this name already exists.");
				return;
			}
			updatedKeys = [{ ...newKey, required: false }, ...apiKeys];
		}

		// Close modal and reset
		setNewKey({ key: "", value: "" });
		setIsAddKeyModalOpen(false);
		setEditingKeyIndex(null);
		setModalMode('add');

		// Auto-save the changes
		await saveApiKeys(updatedKeys);
	};

	// Add function to handle editing
	const handleEditKey = (index: number) => {
		const keyToEdit = apiKeys[index];
		setNewKey({ key: keyToEdit.key, value: keyToEdit.value });
		setEditingKeyIndex(index);
		setModalMode('edit');
		setIsAddKeyModalOpen(true);
	};

	// Add function to handle deleting from modal
	const handleDeleteKeyFromModal = async () => {
		if (editingKeyIndex !== null) {
			const updatedKeys = [...apiKeys];
			updatedKeys.splice(editingKeyIndex, 1);

			// Close modal and reset
			setIsAddKeyModalOpen(false);
			setNewKey({ key: "", value: "" });
			setEditingKeyIndex(null);
			setModalMode('add');

			// Auto-save the changes
			await saveApiKeys(updatedKeys);
		}
	};


	const handleConfirmImport = async () => {
		const keysToImport = importedKeys.filter((k) => selectedKeys.has(k.key));

		if (keysToImport.length === 0) {
			setIsImportConfirmModalOpen(false);
			return;
		}

		const mergedKeys = [...apiKeys];

		for (const newKey of keysToImport) {
			const existingIndex = mergedKeys.findIndex((k) => k.key === newKey.key);
			if (existingIndex >= 0) {
				mergedKeys[existingIndex].value = newKey.value;
			} else {
				mergedKeys.push(newKey);
			}
		}

		await saveApiKeys(mergedKeys);

		setIsImportConfirmModalOpen(false);
		setImportedKeys([]);
		setSelectedKeys(new Set());
	};

	const handleToggleSelectAll = () => {
		if (selectedKeys.size === importedKeys.length) {
			setSelectedKeys(new Set());
		} else {
			setSelectedKeys(new Set(importedKeys.map((k) => k.key)));
		}
	};

	const handleToggleKeySelection = (key: string) => {
		const newSelection = new Set(selectedKeys);
		if (newSelection.has(key)) {
			newSelection.delete(key);
		} else {
			newSelection.add(key);
		}
		setSelectedKeys(newSelection);
	};

	const toggleImportKeyVisibility = (key: string) => {
		setImportVisibleKeys(prev => {
			const newSet = new Set(prev);
			if (newSet.has(key)) {
				newSet.delete(key);
			} else {
				newSet.add(key);
			}
			return newSet;
		});
	};

	// Save API keys to user_settings.json
	const saveApiKeys = async (keysToSave: ApiKey[]) => {
		try {
			setError(null);

			if (keysToSave.length > 0) {
				// Validate: All keys must have names
				const emptyKeys = keysToSave.filter((k) => k.key.trim() === "");
				if (emptyKeys.length > 0) {
					setError("All API keys must have names");
					return;
				}

				// Validate: No duplicate keys
				const keyNames = keysToSave.map((k) => k.key);
				const uniqueKeys = new Set(keyNames);
				if (uniqueKeys.size !== keyNames.length) {
					setError("Duplicate key names are not allowed");
					return;
				}
			}

			// Format the credentials object
			const credentials = keysToSave.reduce(
				(acc, curr) => {
					if (curr.key.trim()) {
						acc[curr.key] = curr.value;
					}
					return acc;
				},
				{} as Record<string, string>,
			);

			// Save the credentials to user_settings.json
			await invoke("update_user_credentials", { credentials });

			setApiKeys(keysToSave);
		} catch (err) {
			console.error("Failed to save API keys:", err);
			setError(`Failed to save API keys: ${err}`);
		}
	};

	const openUserSettings = async () => {
		try {
			// Open user_settings.json for API keys (default)
			await invoke("open_credentials_file", { fileName: "user_settings.json" });
		} catch (err) {
			console.error("Failed to open user settings file:", err);
			setError(`Failed to open user settings file: ${err}`);
		}
	};

	const openSystemSettings = async () => {
		try {
			// Open system_settings.json
			await invoke("open_credentials_file", {
				fileName: "system_settings.json",
			});
		} catch (err) {
			console.error("Failed to open system settings file:", err);
			setError(`Failed to open system settings file: ${err}`);
		}
	};

	const openEnvFile = async () => {
		try {
			// Open .env file
			await invoke("open_credentials_file", { fileName: ".env" });
		} catch (err) {
			console.error("Failed to open environment variables file:", err);
			setError(`Failed to open environment variables file: ${err}`);
		}
	};

	const openCondarcFile = async () => {
		try {
			// Open .condarc file
			await invoke("open_credentials_file", { fileName: ".condarc" });
		} catch (err) {
			console.error("Failed to open Conda configuration file:", err);
			setError(`Failed to open Conda configuration file: ${err}`);
		}
	};

	const openMcpSettings = async () => {
		try {
			// Open mcp_settings.json
			await invoke("open_credentials_file", { fileName: "mcp_settings.json" });
		} catch (err) {
			console.error("Failed to open MCP settings file:", err);
			setError(`Failed to open MCP settings file: ${err}`);
		}
	};

	const openDocumentation = async () => {
		try {
			// Open documentation URL in a new window
			await invoke("open_url_in_window", {
				url: "https://docs.openbb.co/desktop/api_keys",
				title: "Open Data Platform Documentation",
			});
		} catch (err) {
			console.error("Failed to open documentation:", err);
			setError(`Failed to open documentation: ${err}`);
		}
	};


	const handleFileInputChange = async (
		e: React.ChangeEvent<HTMLInputElement>,
	) => {
		if (e.target.files && e.target.files.length > 0) {
			const file = e.target.files[0];
			const extension = file.name.split(".").pop()?.toLowerCase();

			if (extension === "json" || extension === "env") {
				await parseImportedFile(file);
			} else {
				setError("Unsupported file format. Please use .json or .env files.");
			}

			// Clear the input so the same file can be selected again if needed
			e.target.value = "";
		}
	};

	const handleErrorAlert = async (messageText: string) => {
		try {
			await message(messageText, { title: "OpenBB", kind: "error" });
		} catch (error) {
			console.error("Failed to show error message:", error);
		}
	};

	// Show alert when error state changes
	useEffect(() => {
		if (error) {
			handleErrorAlert(error).then(() => {
				setError(null);
			});
		}
	}, [error]);

	// Add this useEffect to handle the Escape key
	useEffect(() => {
		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'Escape') {
				setIsAddKeyModalOpen(false);
				setNewKey({ key: "", value: "" }); // Also reset form
			}
		};

		if (isAddKeyModalOpen) {
			window.addEventListener('keydown', handleKeyDown);
		}

		return () => {
			window.removeEventListener('keydown', handleKeyDown);
		};
	}, [isAddKeyModalOpen]);

	// Toggle key visibility
	const toggleKeyVisibility = (key: string) => {
		setVisibleKeys(prev => {
			const newSet = new Set(prev);
			if (newSet.has(key)) {
				newSet.delete(key);
			} else {
				newSet.add(key);
			}
			return newSet;
		});
	};

	useEffect(() => {
		const scrollContainer = scrollContainerRef.current;
		const header = headerRef.current;
		const content = contentRef.current;

		if (!scrollContainer || !header || !content) {
			return;
		}

		const observer = new ResizeObserver(() => {
			const hasScrollbar = scrollContainer.scrollHeight > scrollContainer.clientHeight;
			if (hasScrollbar) {
				const scrollbarWidth = scrollContainer.offsetWidth - scrollContainer.clientWidth;
				header.style.paddingRight = `${scrollbarWidth}px`;
				content.style.paddingRight = `${scrollbarWidth}px`;
			} else {
				header.style.paddingRight = "0px";
				content.style.paddingRight = "0px";
			}
		});

		observer.observe(content);

		return () => {
			observer.disconnect();
		};
	}, [filteredApiKeys]);


	return (
		<div className="flex flex-col h-full">
			<div className="mt-2 flex flex-col flex-1">
				{/* API Keys Content Section */}
				<section>
					{loading ? (
						null
					) : error ? (
						null
					) : (
						<div>
							<div>
								<div className="flex items-center justify-between py-4 mb-2">
									{/* Search box */}
									<div className="w-[200px] shrink-0">
										<div className="relative">
											<input
												type="text"
												placeholder="Search API Keys..."
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

									{/* Action buttons including Save */}
									<div className="flex items-center gap-2">
										<Tooltip
											content="Add a new API key."
											className="tooltip tooltip-theme"
										>
											<Button
												onClick={() => {
													setModalMode('add');
													setNewKey({ key: "", value: "" });
													setEditingKeyIndex(null);
													setIsAddKeyModalOpen(true);
												}}
												variant="neutral"
												size="sm"
												className="button-neutral shadow-sm px-2 py-1"
											>
												Add New Key
											</Button>
										</Tooltip>
										<Tooltip
											content="Import API keys from a .env or JSON file. Saved only after clicking 'Save API Keys'."
											className="tooltip tooltip-theme"
										>
											<Button
												onClick={() => fileInputRef.current?.click()}
												variant="secondary"
												className="button-secondary shadow-sm px-2 py-1"
												size="sm"
											>
												<span className="body-xs-medium whitespace-nowrap">Import Keys</span>
											</Button>
										</Tooltip>
										<input
											type="file"
											ref={fileInputRef}
											onChange={handleFileInputChange}
											accept=".json,.env"
											className="hidden"
										/>
										<Tooltip
											content="View OpenBB Platform configuration and environment files."
											className="tooltip tooltip-theme"
										>
											<Button
												data-testid="settings-button"
												onClick={() => setIsSettingsModalOpen(true)}
												variant="outline"
												size="icon"
												className="button-secondary shadow-sm py-2 px-2"
											>
												<FileIcon className="h-4 w-4" />
											</Button>
										</Tooltip>

										<Tooltip
											content="Open the documentation for this screen."
											className="tooltip-theme"
										>
											<Button
												onClick={openDocumentation}
												variant="outline"
												className="button-secondary shadow-sm px-2 py-2"
												size="sm"
												data-testid="documentation-button"
											>
												<DocumentationIcon className="h-4 w-4" />
											</Button>
										</Tooltip>
									</div>
								</div>
							</div>
							<div className="flex flex-col justify-between">
								{/* Table Header */}
								{filteredApiKeys.length > 0 && (
									<div
										ref={headerRef}
										className="pl-2 flex items-center py-1 mb-3 rounded-sm body-xs-bold text-theme-muted bg-theme-quartary"
									>
										<div className="w-2/5 pr-2">Name</div>
										<div className="w-2/5 pr-2">Value</div>
										<div className="flex flex-1 items-center justify-end gap-2 pl-2 mr-2" />
									</div>
								)}
								<div
									className="overflow-y-auto max-h-[calc(100vh-16rem)]"
									ref={scrollContainerRef}
								>
									{/* API Keys List */}
									{filteredApiKeys.length > 0 ? (
										<div className="flex-1 space-y-3" ref={contentRef}>
											{filteredApiKeys.map((apiKey) => {
												const originalIndex = apiKeys.findIndex(
													(k) => k.key === apiKey.key,
												);
												return (
													<div
														key={`row-${originalIndex}`}
														className="flex items-start rounded-lg bg-theme-tertiary py-2 shadow-md pl-2 group"
													>
														{/* Key Name */}
														<div className="w-2/5 body-xs-medium truncate pr-2">{apiKey.key}</div>
														{/* Key Value (masked) */}
														<div className={`
															w-2/5 body-xs-medium whitespace-pre-wrap pr-2
															${!apiKey.value.trim() ? 'text-theme-muted' : ''}
														`}>
															{apiKey.value
																? visibleKeys.has(apiKey.key)
																	? apiKey.value
																	: "********************"
																: "Undefined"}
														</div>
														{/* Action Buttons */}
															<div className="flex flex-1 items-center justify-end gap-2 pl-2 mr-2 opacity-0 group group-hover:opacity-100">
																<Tooltip content="Edit API key" className="tooltip tooltip-theme">
																	<Button
																		onClick={() => handleEditKey(originalIndex)}
																		variant="ghost"
																		size="icon"
																		className="button-ghost"
																	>
																		<CustomIcon id="edit" className="h-4 w-4" />
																	</Button>
																</Tooltip>
																<Tooltip content={visibleKeys.has(apiKey.key) ? "Hide API key" : "Show API key"} className="tooltip tooltip-theme">
																	<Button
																		variant="ghost"
																		onClick={() => toggleKeyVisibility(apiKey.key)}
																		disabled={!apiKey.value.trim()}
																		className="button-ghost"
																		size="icon"
																	>
																		<CustomIcon
																			id={visibleKeys.has(apiKey.key) ? "eye-off" : "eye"}
																			className="h-4 w-4"
																		/>
																	</Button>
																</Tooltip>
																<Tooltip content={apiKey.value.trim() ? "Copy to clipboard" : "No value to copy"} className="tooltip tooltip-theme">
																	<Button
																		variant="ghost"
																		onClick={() => copyToClipboard(apiKey.value, apiKey.key)}
																		disabled={!apiKey.value.trim()}
																		className="button-ghost"
																		size="icon"
																	>
																		{copiedKey === apiKey.key ? (
																			<CustomIcon
																				id="success"
																				className="h-4 w-4 text-green-500"
																			/>
																		) : (
																			<CopyIcon className="h-4 w-4" />
																		)}
																	</Button>
																</Tooltip>
															</div>
													</div>
												);
											})}
										</div>
									) : (
										null
									)}
								</div>
							</div>
						</div>
					)}
				</section>

				{isAddKeyModalOpen && (
					<div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
						<div className="bg-theme-secondary border border-theme-modal rounded-lg shadow-md min-w-[22rem] max-w-[90vw] max-h-[95vh] px-3 pb-5 pt-3">
							<div className="flex flex-col">
								{/* Modal Header */}
								<div className="flex items-center justify-between mb-5">
									<h2 className="body-lg-bold font-bold text-theme-primary">
										{modalMode === 'edit' ? 'Edit API Key' : 'Add API Key'}
									</h2>
									<Tooltip
										content="Cancel and close"
										className="tooltip tooltip-theme"
									>
										<button
											type="button"
											onClick={() => {
												setIsAddKeyModalOpen(false);
												setNewKey({ key: "", value: "" }); // Reset form on cancel
											}}
											className="button button-ghost"
										>
											<CustomIcon id="close" className="h-6 w-6" />
										</button>
									</Tooltip>
								</div>

								{/* Form Content */}
								<div className="flex flex-col space-y-4">
									<div className="flex flex-col gap-1">
										<label htmlFor="modal-key-name" className="body-sm-medium text-theme-secondary">
											Name
										</label>
										<input
											id="modal-key-name"
											type="text"
											placeholder="api_key_name"
											value={newKey.key}
											spellCheck={false}
											onChange={(e) =>
												setNewKey({ ...newKey, key: e.target.value })
											}
											className="border border-theme-accent shadow-sm w-full h-10"
										/>
									</div>
									<div className="flex flex-col gap-1">
										<div className="flex justify-between items-center">
											<label htmlFor="modal-key-value" className="body-sm-medium text-theme-secondary">
												Value
											</label>
											<div className="flex items-center relative top-9 right-1">
												<Tooltip content={isModalValueVisible ? "Hide value" : "Show value"} className="tooltip tooltip-theme">
													<Button
														type="button"
														variant="ghost"
														size="icon"
														onClick={() => setIsModalValueVisible(!isModalValueVisible)}
														className="button-ghost flex items-center p-1"
													>
														<CustomIcon
															id={isModalValueVisible ? "eye-off" : "eye"}
															className="h-4 w-4"
														/>
													</Button>
												</Tooltip>
												<Tooltip content={newKey.value.trim() ? "Copy to clipboard" : "No value to copy"} className="tooltip tooltip-theme">
													<Button
														type="button"
														onClick={copyModalValueToClipboard}
														disabled={!newKey.value.trim()}
														size="icon"
														variant="ghost"
														className={`button-ghost flex items-center mr-1 ${!newKey.value.trim() ? 'opacity-50 cursor-not-allowed' : ''}`}
													>
														{modalCopied ? (
															<CustomIcon
																id="success"
																className="h-4 w-4 text-green-500"
															/>
														) : (
															<CopyIcon className="h-4 w-4" />
														)}
													</Button>
												</Tooltip>
											</div>
										</div>
										{isModalValueVisible ? (
											<textarea
												id="modal-key-value"
												placeholder="Enter your API key"
												value={newKey.value}
												spellCheck={false}
												onChange={(e) =>
													setNewKey({ ...newKey, value: e.target.value })
												}
												className="body-xs-regular leading-relaxed border border-theme-accent shadow-sm w-full rounded-md resize p-1 max-h-[calc(50vh-4rem)] max-w-[85vw] min-w-[21rem] !pr-12"
												style={{ caretShape: 'block', height: '2.5rem', minHeight: '2.5rem', lineHeight: '1.05rem' }}
											/>
										) : (
											<div className="border border-theme-accent shadow-sm w-full rounded-md">
											<input
												id="modal-key-value"
												type="password"
												placeholder="Enter your API key"
												value={newKey.value}
												spellCheck={false}
												onChange={(e) =>
													setNewKey({ ...newKey, value: e.target.value })
												}
												className="text-input *:body-xs-regular border-none p-1 h-10 min-w-[21rem] !pr-12"
											/>
											</div>
										)}
									</div>
								</div>

								{/* Action Buttons */}
								<div className="flex justify-between items-center mt-5">
									<div>
										{modalMode === 'edit' && (
											<Button
												onClick={handleDeleteKeyFromModal}
												variant="danger"
												size="sm"
												className="button-danger px-2 py-1"
											>
												Delete
											</Button>
										)}
									</div>
									<div className="flex gap-2">
										<Button
											onClick={() => {
												setIsAddKeyModalOpen(false);
												setNewKey({ key: "", value: "" });
											}}
											variant="outline"
											size="sm"
											className="button-outline px-2 py-1"
										>
											Cancel
										</Button>
										<Button
											onClick={handleSaveKey}
											variant="primary"
											size="sm"
											className="button-primary px-2 py-1"
											disabled={!newKey.key.trim()}
										>
											{modalMode === 'edit' ? 'Save' : 'Add'}
										</Button>
									</div>
								</div>
							</div>
						</div>
					</div>
				)}

				{/* Add API Key Button */}
				{filteredApiKeys.length === 0 && !loading && (
					<>
						{searchQuery ? (
							<div className="flex flex-col items-center justify-center mt-2">
								<div className="text-center">
									<CustomIcon
										id="search"
										className="h-12 w-12 text-theme-muted mb-2 mx-auto"
									/>
									<h3 className="body-md-bold text-theme-secondary mb-2">
										No API keys found
									</h3>
									<p className="body-sm-regular text-theme-muted mb-4">
										No API keys match your search for "{searchQuery}"
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
						) : (
							<div className="flex-1 w-full justify-center bg-theme-primary mb-4 rounded-sm flex flex-col items-center">
								<p className="text-theme-muted body-sm-regular">No API keys added</p>
							</div>
						)}
					</>
				)}
			</div>

			{/* Settings Modal */}
			{isSettingsModalOpen && (
				<div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
					<div className="bg-theme-secondary border border-theme-modal rounded-lg shadow-md w-full max-w-xs px-5 pb-5 pt-3">
						<div className="flex items-center justify-between mb-6">
							<h2 className="body-lg-bold font-bold text-theme-primary">
								Configuration Files
							</h2>
							<Tooltip
								content="Cancel and go back."
								className="tooltip tooltip-theme"
							>
								<button
									type="button"
									onClick={() => setIsSettingsModalOpen(false)}
									className="button button-ghost"
								>
									<CustomIcon id="close" className="h-6 w-6" />
								</button>
							</Tooltip>
						</div>

						{/* Radio Options */}
						<div className="space-y-2 mb-2">
							{[
								{ value: "user_settings.json", label: "user_settings.json" },
								{ value: "system_settings.json", label: "system_settings.json" },
								{ value: "mcp_settings.json", label: "mcp_settings.json" },
								{ value: ".env", label: ".env" },
								{ value: ".condarc", label: ".condarc" },
							].map((option) => (
								<label
									key={option.value}
									className="flex items-center gap-4 cursor-pointer body-xs-regular text-theme-primary"
								>
									<input
										type="radio"
										name="settingsFile"
										value={option.value}
										checked={selectedSettingsFile === option.value}
										onChange={(e) =>
											setSelectedSettingsFile(e.target.value as typeof selectedSettingsFile)
										}
										className="sr-only text-theme-accent"
									/>
									<span
										className={`relative flex items-center justify-center h-4 w-4 rounded-full border-2 ${
											selectedSettingsFile === option.value ? 'border-theme-radio' : 'border-theme'
										}`}
									>
										{selectedSettingsFile === option.value && (
											<span className="block h-2 w-2 rounded-full bg-theme-neutral" />
										)}
									</span>
									<span className="body-sm-medium text-theme-secondary">{option.label}</span>
								</label>
							))}
							</div>

						{/* Action Buttons */}
						<div className="flex justify-end">
							<Button
								onClick={() => {
									switch (selectedSettingsFile) {
										case 'user_settings.json':
											openUserSettings();
											setIsSettingsModalOpen(false);
											break;
										case 'system_settings.json':
											openSystemSettings();
											setIsSettingsModalOpen(false);
											break;
										case 'mcp_settings.json':
											openMcpSettings();
											setIsSettingsModalOpen(false);
											break;
										case '.env':
											openEnvFile();
											setIsSettingsModalOpen(false);
											break;
										case '.condarc':
											openCondarcFile();
											setIsSettingsModalOpen(false);
											break;
									}
								}}
								variant="primary"
								className="button-primary shadow-sm px-2 py-1"
								size="sm"
							>
								Open File
							</Button>
						</div>
					</div>
				</div>
			)}

			{/* Import Confirmation Modal */}
			{isImportConfirmModalOpen && (
				<div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
					<div className="bg-theme-secondary border border-theme-modal rounded-lg shadow-md w-full max-w-[90vw] px-5 pb-5 pt-3">
						<div className="flex items-center justify-between mb-4">
							<h2 className="body-lg-bold font-bold text-theme-primary">
								Confirm Import
							</h2>
							<Tooltip
								content="Cancel and close"
								className="tooltip tooltip-theme"
							>
								<button
									type="button"
									onClick={() => setIsImportConfirmModalOpen(false)}
									className="button button-ghost"
								>
									<CustomIcon id="close" className="h-6 w-6" />
								</button>
							</Tooltip>
						</div>

						<div className="flex max-h-64 overflow-y-auto mb-6 pr-1">
							<table className="w-full text-left flex-1 items-center">
								<thead className="sticky top-0 z-10 flex-1 items-center">
									<tr className="bg-theme-quartary flex-1 items-center">
										<th className="p-2 w-10 align-middle text-center">
											<input
												type="checkbox"
												checked={selectedKeys.size === importedKeys.length && importedKeys.length > 0}
												onChange={handleToggleSelectAll}
												className="checkbox checkbox-theme h-4 w-4"
											/>
										</th>
										<th className="p-2 body-sm-regular text-theme-secondary">Key</th>
										<th className="p-2 body-sm-regular text-theme-secondary">Value</th>
										<th className="p-2 w-10"></th>
									</tr>
								</thead>
								<tbody>
									{importedKeys.map((key, index) => (
										<tr key={key.key} className={`border-t ${index % 2 === 0 ? 'bg-theme-secondary' : 'bg-theme-tertiary'}`}>
											<td className="p-2 align-middle text-center">
												<input
													type="checkbox"
													checked={selectedKeys.has(key.key)}
													onChange={() => handleToggleKeySelection(key.key)}
													className="checkbox checkbox-theme h-4 w-4"
												/>
											</td>
											<td className="p-2 body-xs-medium text-theme-secondary truncate max-w-xs">{key.key}</td>
											<td className="p-2 body-xs-regular text-theme-muted truncate max-w-xs">
												{importVisibleKeys.has(key.key) ? key.value : "********************"}
											</td>
											<td className="p-2">
												<Tooltip content={importVisibleKeys.has(key.key) ? "Hide" : "Show"} className="tooltip tooltip-theme">
													<Button
														variant="ghost"
														size="icon"
														onClick={() => toggleImportKeyVisibility(key.key)}
														className="button-ghost"
													>
														<CustomIcon
															id={importVisibleKeys.has(key.key) ? "eye-off" : "eye"}
															className="h-4 w-4"
														/>
													</Button>
												</Tooltip>
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</div>

						<div className="flex justify-end gap-2">
							<Button
								onClick={() => setIsImportConfirmModalOpen(false)}
								variant="outline"
								size="sm"
								className="button-outline px-2 py-1"
							>
								Cancel
							</Button>
							<Button
								onClick={handleConfirmImport}
								variant="primary"
								size="sm"
								className="button-primary px-2 py-1"
							>
								Import Selected ({selectedKeys.size})
							</Button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
export const Route = createFileRoute("/api-keys")({
	component: ApiKeysPage,
});
