import {
	Outlet,
	createRootRoute,
	useRouter,
} from "@tanstack/react-router";
import { useCallback, useEffect, useState } from "react";
import ShowVersion from "../components/ShowVersion";
import { ODPLogo, OpenBBLogo } from "../components/Icon";
import { SystemReadinessBanner } from "../components/SystemReadinessBanner";
import { EnvironmentCreationProvider, useEnvironmentCreation } from "../contexts/EnvironmentCreationContext";
import { QuantSessionProvider } from "../contexts/QuantSessionContext";

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


function NavSeparator() {
    return <span className="mx-1 text-theme-muted opacity-30 select-none" aria-hidden>|</span>;
}

function ThemeToggle({ isDark, onToggle }: { isDark: boolean; onToggle: () => void }) {
    return (
        <button
            type="button"
            onClick={onToggle}
            className="rounded-sm px-2 py-1 body-xxs-medium text-theme-muted hover:text-theme-primary transition-colors"
            aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
        >
            {isDark ? "Light" : "Dark"}
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
        const groupedPath =
            currentPath === "/backends" || currentPath === "/environments" || currentPath === "/api-keys"
                ? "/settings"
                : currentPath === "/dashboard" || currentPath === "/workspace"
                    ? "/workspace"
                    : currentPath === "/trading" || currentPath === "/execution"
                        ? "/execution"
                        : currentPath;
        setSelectedTab(groupedPath);
    }, [currentPath]);

	const [isDarkMode, setIsDarkMode] = useState(() => {
		if (typeof window !== "undefined") {
			const savedTheme = localStorage.getItem("theme");
			const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
			return savedTheme === "dark" || (savedTheme === null && prefersDark);
		}
		return true;
	});

	useEffect(() => {
		const root = document.documentElement;
		if (isDarkMode) {
			root.classList.add("dark");
			root.setAttribute("data-theme", "dark");
			localStorage.setItem("theme", "dark");
		} else {
			root.classList.remove("dark");
			root.setAttribute("data-theme", "light");
			localStorage.setItem("theme", "light");
		}
	}, [isDarkMode]);

	useEffect(() => {
		const handleStorageChange = (event: StorageEvent) => {
			if (event.key === "theme") {
				setIsDarkMode(event.newValue === "dark");
			}
		};
		window.addEventListener("storage", handleStorageChange);
		return () => window.removeEventListener("storage", handleStorageChange);
	}, []);

	const toggleTheme = useCallback(() => {
		setIsDarkMode((prev) => !prev);
	}, []);

    return (
        <div className="h-screen bg-theme-primary overflow-hidden transition-colors flex flex-col">
			<header className={`bg-theme-primary px-5 mt-2 ${isLogsView ? "logs-page-header" : ""}`}>
				<div className="flex items-center justify-between w-full pb-3">
					<ODPLogo />
					<div className="flex flex-row items-center gap-3">
						<ThemeToggle isDark={isDarkMode} onToggle={toggleTheme} />
						<div className="flex flex-col">
							<OpenBBLogo className="h-9 w-9" />
							<div>
								<ShowVersion />
							</div>
						</div>
					</div>
				</div>
			</header>
            <SystemReadinessBanner hidden={shouldHideNav} />
			<div className="px-5 border-b-2 border-theme-outline">
				{!shouldHideNav && (
					<nav
						className="flex flex-row items-center -mb-0.5"
						role="tablist"
						aria-orientation="horizontal"
					>
						<NavLink to="/settings" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Settings</NavLink>
						<NavSeparator />
						<NavLink to="/workspace" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Workspace</NavLink>
						<NavLink to="/finance" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Finance Lab</NavLink>
						<NavLink to="/watchlist" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Watchlist</NavLink>
						<NavLink to="/macro" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Macro Lab</NavLink>
						<NavLink to="/quant" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Strategy Lab</NavLink>
						<NavLink to="/execution" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Portfolio & Execution</NavLink>
						<NavLink to="/ai" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>AI</NavLink>
						<NavLink to="/ops" selectedTab={selectedTab} setSelectedTab={setSelectedTab}>Ops</NavLink>
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
			<QuantSessionProvider>
				<Root />
			</QuantSessionProvider>
		</EnvironmentCreationProvider>
	);
}
