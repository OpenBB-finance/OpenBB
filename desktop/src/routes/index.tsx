import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { invoke } from "@tauri-apps/api/core";
import { useEffect, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { isTauriRuntime } from "../lib/runtime";

function Base() {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    let unlistenStatus: (() => void) | null = null;
    let unlistenDir: (() => void) | null = null;

    const redirectTo = async (targetRoute: string) => {
      if (cancelled) {
        return;
      }
      console.log("Redirecting to:", targetRoute);
      setLoading(false);
      await navigate({ to: targetRoute, replace: true });
    };

    if (!isTauriRuntime()) {
      void redirectTo("/workspace");
      return () => {
        cancelled = true;
      };
    }

    console.log("Base component mounted - listening for installation events");

    const setupListeners = async () => {
      unlistenStatus = await listen<boolean>("installation-status", (event) => {
        console.log("Received installation-status event:", event);

        const isInstalled = event.payload;
        if (isInstalled) {
          void redirectTo("/workspace");
        } else {
          void redirectTo("/setup");
        }
      });

      unlistenDir = await listen<string>("installation-directory", (event) => {
        console.log("Received installation-directory event:", event);
        localStorage.setItem("installationDirectory", event.payload);
      });

      timeoutId = setTimeout(() => {
        console.log("Event timeout - falling back to invoke");
        invoke<{ is_installed: boolean }>("get_installation_state")
          .then((state) => {
            console.log("Installation state from invoke:", state);
            if (state.is_installed) {
              void redirectTo("/workspace");
            } else {
              void redirectTo("/setup");
            }
          })
          .catch((err) => {
            console.error("Error getting installation state:", err);
            void redirectTo("/setup");
          });
      }, 2000);
    };

    void setupListeners();

    return () => {
      cancelled = true;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      unlistenStatus?.();
      unlistenDir?.();
    };
  }, [navigate]);

  return (
    <div className="flex items-center justify-center h-screen">
      {loading && (
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Starting OpenBB Platform</h1>
          <p className="text-gray-600">Checking installation status...</p>
        </div>
      )}
    </div>
  );
}

export const Route = createFileRoute("/")({
  component: Base,
});
