import {
	Outlet,
	createRootRoute,
	useRouter,
} from "@tanstack/react-router";
{/*import { invoke } from "@tauri-apps/api/core";*/}
import { useEffect, useState } from "react";
{/*import { useEffect, useState } from "react";
import { ThemeToggleButton } from "../components/Icon";*/}
import ShowVersion from "../components/ShowVersion";
import { ODPLogo, OpenBBLogo } from "../components/Icon";
import { EnvironmentCreationProvider, useEnvironmentCreation } from "../contexts/EnvironmentCreationContext";

{/*interface UserCredentials {
	preferences?: {
		chart_style?: string;
	};
}*/}

export const Route = createRootRoute({
	component: RootWithProvider,
});

// Reusable NavLink component
interface NavLinkProps {
	to: string;
	search?: Record<string, undefined>;
	children: React.ReactNode;
}

function NavLink({ to, search, children, selectedTab, setSelectedTab }: NavLinkProps & { selectedTab: string, setSelectedTab: (tab: string) => void }) {
    const { isCreatingEnvironment } = useEnvironmentCreation();
    const router = useRouter();
    const currentPath = router.state.location.pathname;
    const isCurrentPage = currentPath === to;
    const isActive = selectedTab === to;

    if (isCreatingEnvironment && !isCurrentPage) {
        return (
            <div
                className="px-4 py-2 rounded-t-lg text-theme-muted cursor-not-allowed opacity-50"
                role="tab"
                aria-selected={isActive}
                tabIndex={-1}
            >
                {children}
            </div>
        );
    }

    const handleNavigation = async (e: React.MouseEvent) => {
        e.preventDefault();
        setSelectedTab(to); // update tab selection immediately
        router.navigate({ to, search });
    };

    const baseClassName = "mr-4 pb-1";
    const activeClassName = "body-sm-medium border-b-2 tab-border-active text-theme-accent";
    const inactiveClassName = "body-sm-regular text-theme-muted";

    return (
        <button
            onClick={handleNavigation}
            className={`${baseClassName} ${isActive ? activeClassName : inactiveClassName}`}
            role="tab"
            aria-selected={isActive}
            tabIndex={isActive ? 0 : -1}
            type="button"
        >
            {children}
        </button>
    );
}


function Root() {
	useEffect(() => {
		const handleKeyDown = (event: KeyboardEvent) => {
			const target = event.target as HTMLElement;
			const targetTagName = target.tagName.toLowerCase();

			if (
				event.key === "Backspace" &&
				targetTagName !== "input" &&
				targetTagName !== "textarea" &&
				targetTagName !== "select" &&
				!target.isContentEditable
			) {
				event.preventDefault();
			}
		};

		window.addEventListener("keydown", handleKeyDown);

		return () => {
			window.removeEventListener("keydown", handleKeyDown);
		};
	}, []);

	const router = useRouter();
    const currentPath = router.state.location.pathname;
    const [selectedTab, setSelectedTab] = useState(currentPath);
	const isJupyterLogsView = currentPath === "/jupyter-logs";
	const isBackendLogsView = currentPath === "/backend-logs";
	const isLogsView = isJupyterLogsView || isBackendLogsView;
	const isInstallingSetup = currentPath === "/setup";
	const isInstallationProgress = currentPath === "/installation-progress";
	const shouldHideNav = isJupyterLogsView || isBackendLogsView || isInstallingSetup || isInstallationProgress;

    useEffect(() => {
        setSelectedTab(currentPath); // sync with route changes (e.g. browser nav)
    }, [currentPath]);

	// Set up theme state and persistence
	{/*const [isDarkMode, setIsDarkMode] = useState(() => {
		// Check localStorage or system preference on initial load
		if (typeof window !== "undefined") {
			const savedTheme = localStorage.getItem("theme");
			const prefersDark = window.matchMedia(
				"(prefers-color-scheme: dark)",
			).matches;
			return savedTheme === "dark" || (savedTheme === null && prefersDark);
		}
		return false;
	});*/}

	// Load theme from backend on initial load
	{/*useEffect(() => {
		async function loadThemeFromSettings() {
			try {
				// Try to get theme from user_settings.json
				const result = await invoke<UserCredentials>("get_user_credentials");
				if (result?.preferences?.chart_style) {
					const configTheme = result.preferences.chart_style;
					const isDark = configTheme === "dark";

					// Update UI state only if different from current localStorage
					const savedTheme = localStorage.getItem("theme");
					if (
						(isDark && savedTheme !== "dark") ||
						(!isDark && savedTheme !== "light")
					) {
						setIsDarkMode(isDark);
					}
				}
			} catch (error) {
				console.error("Failed to load theme from settings:", error);
				// Fall back to browser/localStorage preference (already handled in useState)
			}
		}

		loadThemeFromSettings();
	}, []);*/}

	// Apply theme class to document and save to localStorage
	{/*useEffect(() => {
		if (isDarkMode) {
			document.documentElement.classList.add("dark");
			localStorage.setItem("theme", "dark");
		} else {
			document.documentElement.classList.remove("dark");
			localStorage.setItem("theme", "light");
		}
	}, [isDarkMode]);*/}

	// Listen for theme changes in other windows
	{/*useEffect(() => {
		const handleStorageChange = (event: StorageEvent) => {
			if (event.key === "theme") {
				const newTheme = event.newValue;
				if (newTheme === "dark" && !isDarkMode) {
					setIsDarkMode(true);
				} else if (newTheme === "light" && isDarkMode) {
					setIsDarkMode(false);
				}
			}
		};

		window.addEventListener("storage", handleStorageChange);
		return () => {
			window.removeEventListener("storage", handleStorageChange);
		};
	}, [isDarkMode]);*/}

	// Toggle theme function - updates both UI and backend
	{/*const toggleTheme = async () => {
		const newTheme = !isDarkMode ? "dark" : "light";

	 	// Update UI state immediately
		setIsDarkMode(!isDarkMode);

	 	// Update backend configuration
	 	try {
	 		await invoke("toggle_theme", {
	 			theme: newTheme,
	 		});
	 		console.log(`Theme updated to ${newTheme} in configuration`);
	 	} catch (error) {
	 		console.error("Failed to update theme in configuration:", error);
	 		// Continue anyway since UI is already updated
	 	}
	};*/}

	{/*useEffect(() => {
		// Scroll to top on route change
		localStorage.setItem("theme", "dark");
	}, [currentPath]);*/}

    return (
        <div className="h-screen bg-theme-primary overflow-hidden transition-colors flex flex-col">
			<header className={`bg-theme-primary px-5 mt-2 ${isLogsView ? "logs-page-header" : ""}`}>
				{/*<div className="flex gap-2 relative top-2 left-[85vw] -mb-7 pt-2 px-2">
					<ThemeToggleButton isDarkMode={isDarkMode} toggleTheme={toggleTheme} />
				</div>*/}
				<div className="flex items-center justify-between w-full pb-3">
					{/* Left: ODN Logo */}
					<ODPLogo />

					{/* Right: OpenBBLogo with version below */}
					<div className="flex flex-row items-center justify-end">
						<div className="flex flex-col">
							<OpenBBLogo className="h-9 w-9" />
							<div>
								<ShowVersion />
							</div>
						</div>
					</div>
				</div>
			</header>
			<div className="px-5 border-b-2 border-theme-outline">
				{!shouldHideNav && (
					<nav
						className="flex flex-row gap-2 -mb-0.5"
						role="tablist"
						aria-orientation="horizontal"
					>
						<NavLink to="/backends" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Backends</NavLink>
						<NavLink to="/environments" search={{ directory: undefined, userDataDir: undefined }} selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Environments</NavLink>
						<NavLink to="/api-keys" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>API Keys</NavLink>
					</nav>
				)}
			</div>
            <div className="bg-theme-secondary flex flex-1 min-h-0">
                <main className={`flex-1 flex flex-col ${isLogsView ? "pl-5" : "px-5"}`}>
                    <Outlet />
                </main>
            </div>

            <footer className="w-full bg-theme-secondary">
                <div className="container mx-auto text-center">
                    <p className="body-sm-regular text-theme-muted mb-1 mt-1">Copyright © 2025 OpenBB Inc.</p>
                </div>
            </footer>
        </div>
    );
}

export function RootWithProvider() {
	return (
		<EnvironmentCreationProvider>
			<Root />
		</EnvironmentCreationProvider>
	);
}
