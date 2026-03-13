use std::ffi::c_void;
use std::sync::Once;

use objc2::rc::Retained;
use objc2::runtime::AnyObject;
use objc2::{ClassType, define_class, msg_send, sel};
use objc2_app_kit::NSApplication;
use objc2_foundation::{MainThreadMarker, NSNotificationCenter, NSNotificationName, NSObject};
use tauri::AppHandle;
use tokio::runtime::Runtime;

// Ensure this is initialized only once
static INIT: Once = Once::new();
// Store our observer to prevent it from being dropped
static mut OBSERVER: Option<Retained<AnyObject>> = None;
// Store the app handle pointer globally (set before observer is created)
static mut APP_HANDLE_PTR: *mut c_void = std::ptr::null_mut();

// Define the Objective-C class using objc2's define_class! macro
define_class!(
    #[unsafe(super(NSObject))]
    #[name = "OBBAppTerminationObserver"]
    struct AppTerminationObserver;

    impl AppTerminationObserver {
        #[unsafe(method(applicationWillTerminate:))]
        fn will_terminate(&self, _notification: *mut AnyObject) {
            log::debug!("applicationWillTerminate received, running cleanup...");
            let app_ptr = unsafe { APP_HANDLE_PTR };
            if !app_ptr.is_null() {
                let app_handle = unsafe { &*(app_ptr as *const AppHandle) };
                // Create a runtime and run the cleanup handler
                if let Ok(rt) = Runtime::new() {
                    rt.block_on(async {
                        crate::cleanup_all_processes(app_handle.clone()).await;
                    });
                }
            }
            // Don't call exit() as it may interfere with macOS shutdown
        }
    }
);

// NSApplicationWillTerminateNotification is an extern static in AppKit
unsafe extern "C" {
    static NSApplicationWillTerminateNotification: &'static NSNotificationName;
}

// Set up applicationWillTerminate listener
pub fn setup_termination_handler(app_handle: AppHandle) {
    INIT.call_once(|| {
        // Get the main thread marker - we should be on the main thread during app setup
        let Some(mtm) = MainThreadMarker::new() else {
            log::error!("setup_termination_handler must be called from the main thread");
            return;
        };

        // Store the app handle pointer globally before creating the observer
        let app_ptr = Box::into_raw(Box::new(app_handle)) as *mut c_void;
        unsafe {
            APP_HANDLE_PTR = app_ptr;
        }

        // Create our observer using NSObject's default allocator
        let observer: Retained<AppTerminationObserver> =
            unsafe { msg_send![AppTerminationObserver::class(), new] };

        // Get the notification center
        let notification_center = NSNotificationCenter::defaultCenter();

        // Get NSApplication shared instance
        let app = NSApplication::sharedApplication(mtm);

        // Get the selector for our handler method
        let selector = sel!(applicationWillTerminate:);

        // Register for the applicationWillTerminate notification
        unsafe {
            notification_center.addObserver_selector_name_object(
                &observer,
                selector,
                Some(NSApplicationWillTerminateNotification),
                Some(&app),
            );

            // Store the observer in our static to prevent it from being dropped
            let observer_any: Retained<AnyObject> = Retained::cast_unchecked(observer);
            OBSERVER = Some(observer_any);
        }

        log::debug!("applicationWillTerminate observer registered successfully");
    });
}
