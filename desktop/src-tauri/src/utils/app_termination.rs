use objc;
use std::sync::Once;
use tauri::AppHandle;
use tokio::runtime::Runtime;

// Ensure this is initialized only once
static INIT: Once = Once::new();
// Store our observer to prevent it from being dropped

static mut OBSERVER: Option<*mut std::ffi::c_void> = None;

// Set up applicationWillTerminate listener
pub fn setup_termination_handler(app_handle: AppHandle) {
    INIT.call_once(|| {
        unsafe {
            // Import objc macros
            use objc::runtime::{Class, Object, Sel};
            use objc::{msg_send, sel, sel_impl};
            use std::ffi::c_void;

            // Create a static reference to the app handle for use in the callback
            let app_ptr = Box::into_raw(Box::new(app_handle)) as *mut c_void;

            // Define our Objective-C class
            let superclass = Class::get("NSObject").unwrap();
            let mut decl =
                objc::declare::ClassDecl::new("OBBAppTerminationObserver", superclass).unwrap();

            // Add instance variable to store AppHandle
            decl.add_ivar::<*mut c_void>("appHandlePtr");

            // Implement the handler for applicationWillTerminate
            extern "C" fn will_terminate(this: &Object, _cmd: Sel, _notification: *mut Object) {
                log::debug!("applicationWillTerminate received, running cleanup...");

                unsafe {
                    // Retrieve the app handle pointer
                    let app_ptr: *mut c_void = *this.get_ivar("appHandlePtr");
                    let app_handle = &*(app_ptr as *const AppHandle);

                    // Create a runtime and run the cleanup handler
                    if let Ok(rt) = Runtime::new() {
                        rt.block_on(async {
                            crate::cleanup_all_processes(app_handle.clone()).await;
                        });
                    }
                }

                // Don't call exit() as it may interfere with macOS shutdown
            }

            // Add the method to our class
            #[allow(unexpected_cfgs)]
            let sel_app_will_terminate = sel!(applicationWillTerminate:);
            decl.add_method(
                sel_app_will_terminate,
                will_terminate as extern "C" fn(&Object, Sel, *mut Object),
            );

            // Register the class
            let termination_observer_class = decl.register();

            // Create an instance
            #[allow(unexpected_cfgs)]
            let observer: *mut Object = msg_send![termination_observer_class, new];

            // Store the app handle pointer in the instance variable
            (*observer).set_ivar("appHandlePtr", app_ptr);

            // Store the observer in our static to prevent it from being dropped
            OBSERVER = Some(observer as *mut c_void);

            // Get the notification center
            let notification_center_class = Class::get("NSNotificationCenter").unwrap();
            #[allow(unexpected_cfgs)]
            let notification_center: *mut Object =
                msg_send![notification_center_class, defaultCenter];

            // Get NSApplication shared instance
            #[allow(unexpected_cfgs)]
            let app_class = Class::get("NSApplication").unwrap();
            #[allow(unexpected_cfgs)]
            let app: *mut Object = msg_send![app_class, sharedApplication];

            // Create NSString for notification name
            #[allow(unexpected_cfgs)]
            let notification_name: *mut Object = {
                let nsstring_class = Class::get("NSString").unwrap();
                let cstr =
                    std::ffi::CString::new("NSApplicationWillTerminateNotification").unwrap();
                msg_send![nsstring_class, stringWithUTF8String: cstr.as_ptr()]
            };
            // Register for the applicationWillTerminate notification
            #[allow(unexpected_cfgs)]
            let _: () = msg_send![
                notification_center,
                addObserver:observer
                selector:sel_app_will_terminate
                name:notification_name
                object:app
            ];
            log::debug!("applicationWillTerminate observer registered successfully");
        }
    });
}
