import { createFileRoute } from "@tanstack/react-router";
import { invoke } from "@tauri-apps/api/core";
import { useEffect, useState } from "react";
import { listen } from "@tauri-apps/api/event";

function Base() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("Base component mounted - listening for installation events");
    
    // Create a promise that will be resolved when we get the installation status
    const redirectPromise = new Promise<string>((resolve) => {
      // Listen for the installation status event
      const unlistenStatus = listen<boolean>("installation-status", (event) => {
        console.log("Received installation-status event:", event);
        
        const isInstalled = event.payload;
        if (isInstalled) {
          resolve("/environments");
        } else {
          resolve("/setup");
        }
      });
      
      // Also listen for installation directory
      const unlistenDir = listen<string>("installation-directory", (event) => {
        console.log("Received installation-directory event:", event);
        // Store the directory in localStorage for later use
        localStorage.setItem("installationDirectory", event.payload);
      });
      
      // Fallback in case the event doesn't arrive
      setTimeout(() => {
        console.log("Event timeout - falling back to invoke");
        // If we don't get the event within 2 seconds, use the invoke method
        invoke<{ is_installed: boolean }>("get_installation_state")
          .then((state) => {
            console.log("Installation state from invoke:", state);
            if (state.is_installed) {
              resolve("/environments");
            } else {
              resolve("/setup");
            }
          })
          .catch((err) => {
            console.error("Error getting installation state:", err);
            resolve("/setup"); // Default to setup on error
          });
      }, 2000);
      
      // Clean up listeners
      return () => {
        unlistenStatus.then(fn => fn());
        unlistenDir.then(fn => fn());
      };
    });
    
    // Once we have the target route, redirect to it
    redirectPromise.then((targetRoute) => {
      console.log("Redirecting to:", targetRoute);
      setLoading(false);
      window.location.href = targetRoute;
    });
  }, []);
  

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