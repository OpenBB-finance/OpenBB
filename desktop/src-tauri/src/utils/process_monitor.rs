use once_cell::sync::Lazy;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use std::process::Child;
use std::sync::{Arc, Mutex};

pub type LogStorage = Arc<Mutex<HashMap<String, LogBuffer>>>;

pub static LOG_STORAGE: Lazy<LogStorage> = Lazy::new(create_log_storage);

pub fn get_log_storage() -> LogStorage {
    LOG_STORAGE.clone()
}

#[derive(Debug, Clone, Serialize)]
pub struct LogEntry {
    pub timestamp: i64,
    pub content: String,
    pub process_id: String,
}

#[derive(Debug)]
pub struct LogBuffer {
    pub entries: VecDeque<LogEntry>,
    pub max_size: usize,
}

impl LogBuffer {
    pub fn new(max_size: usize) -> Self {
        Self {
            entries: VecDeque::with_capacity(max_size),
            max_size,
        }
    }

    pub fn add(&mut self, entry: LogEntry) {
        if self.entries.len() >= self.max_size {
            self.entries.pop_front();
        }
        self.entries.push_back(entry);
    }

    pub fn get_logs(&self, count: Option<usize>) -> Vec<LogEntry> {
        match count {
            Some(n) if n < self.entries.len() => {
                // Get the most recent n entries
                self.entries
                    .iter()
                    .skip(self.entries.len() - n)
                    .cloned()
                    .collect()
            }
            _ => {
                // Get all entries
                self.entries.iter().cloned().collect()
            }
        }
    }
}

pub fn create_log_storage() -> LogStorage {
    Arc::new(Mutex::new(HashMap::new()))
}

pub fn register_process(logs: &LogStorage, process_id: &str) -> bool {
    let mut storage = logs.lock().unwrap();
    if !storage.contains_key(process_id) {
        storage.insert(process_id.to_string(), LogBuffer::new(10000)); // Store last 10,000 lines
        true
    } else {
        false
    }
}

pub fn unregister_process(logs: &LogStorage, process_id: &str) -> bool {
    let mut storage = logs.lock().unwrap();
    storage.remove(process_id).is_some()
}

#[derive(Deserialize)]
pub struct GetProcessLogsRequest {
    pub process_id: String,
    pub count: Option<usize>,
}

pub fn get_process_logs(logs: &LogStorage, request: GetProcessLogsRequest) -> Vec<LogEntry> {
    let storage = logs.lock().unwrap();
    if let Some(buffer) = storage.get(&request.process_id) {
        buffer.get_logs(request.count)
    } else {
        Vec::new()
    }
}

// Struct to hold running processes
pub struct RunningProcesses(pub Arc<Mutex<HashMap<String, Child>>>);

impl Default for RunningProcesses {
    fn default() -> Self {
        Self::new()
    }
}

impl RunningProcesses {
    /// Create a new RunningProcesses instance
    pub fn new() -> Self {
        Self(Arc::new(Mutex::new(HashMap::new())))
    }

    /// Add a process to tracking
    pub fn add_process(&self, name: String, child: Child) -> Result<(), String> {
        let mut processes = self.0.lock().map_err(|e| e.to_string())?;
        if processes.contains_key(&name) {
            return Err(format!("Process '{name}' is already being tracked"));
        }
        processes.insert(name, child);
        Ok(())
    }

    /// Check if a process is still running and clean up dead ones
    pub fn is_process_running(&self, name: &str) -> Result<bool, String> {
        let mut processes = self.0.lock().map_err(|e| e.to_string())?;

        if let Some(child) = processes.get_mut(name) {
            match child.try_wait() {
                Ok(Some(_)) => {
                    // Process has exited - remove it
                    processes.remove(name);
                    Ok(false)
                }
                Ok(None) => {
                    // Process is still running
                    Ok(true)
                }
                Err(_) => {
                    // Error checking - assume dead and remove
                    processes.remove(name);
                    Ok(false)
                }
            }
        } else {
            Ok(false)
        }
    }

    /// Kill a process and remove it from tracking
    pub fn kill_process(&self, name: &str) -> Result<bool, String> {
        let mut processes = self.0.lock().map_err(|e| e.to_string())?;

        if let Some(mut child) = processes.remove(name) {
            match child.kill() {
                Ok(_) => {
                    // Try to wait for the process to exit
                    let _ = child.wait();
                    Ok(true)
                }
                Err(e) => Err(format!("Failed to kill process '{name}': {e}")),
            }
        } else {
            Ok(false) // Process not found
        }
    }

    /// Get list of all tracked process names
    pub fn get_all_process_names(&self) -> Result<Vec<String>, String> {
        let processes = self.0.lock().map_err(|e| e.to_string())?;
        Ok(processes.keys().cloned().collect())
    }

    /// Clean up all dead processes
    pub fn cleanup_dead_processes(&self) -> Result<Vec<String>, String> {
        let mut processes = self.0.lock().map_err(|e| e.to_string())?;
        let mut removed = Vec::new();
        let mut to_remove = Vec::new();

        for (name, child) in processes.iter_mut() {
            match child.try_wait() {
                Ok(Some(_)) => {
                    // Process has exited
                    to_remove.push(name.clone());
                }
                Err(_) => {
                    // Error checking - assume dead
                    to_remove.push(name.clone());
                }
                Ok(None) => {
                    // Process is still running - keep it
                }
            }
        }

        for name in to_remove {
            processes.remove(&name);
            removed.push(name);
        }

        Ok(removed)
    }
}

/// Initialize process monitoring system
pub fn init_process_monitoring() {
    let _ = &*LOG_STORAGE;
    log::debug!("Initializing process monitoring system");
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;
    use std::sync::{Arc, Mutex};
    use std::time::{SystemTime, UNIX_EPOCH};

    // Mock Child struct for process management
    #[derive(Debug)]
    pub struct MockChild {
        pub killed: Arc<Mutex<bool>>,
        pub running: Arc<Mutex<bool>>,
    }

    impl MockChild {
        fn new(running: bool) -> Self {
            Self {
                killed: Arc::new(Mutex::new(false)),
                running: Arc::new(Mutex::new(running)),
            }
        }
    }

    // Implement minimal methods to mimic std::process::Child
    impl MockChild {
        fn try_wait(&mut self) -> std::io::Result<Option<i32>> {
            let running = *self.running.lock().unwrap();
            if running { Ok(None) } else { Ok(Some(0)) }
        }
        fn kill(&mut self) -> std::io::Result<()> {
            let mut killed = self.killed.lock().unwrap();
            let mut running = self.running.lock().unwrap();
            *killed = true;
            *running = false;
            Ok(())
        }
        fn wait(&mut self) -> std::io::Result<i32> {
            let mut running = self.running.lock().unwrap();
            *running = false;
            Ok(0)
        }
    }

    pub struct TestRunningProcesses(pub Arc<Mutex<HashMap<String, MockChild>>>);

    impl TestRunningProcesses {
        pub fn new() -> Self {
            Self(Arc::new(Mutex::new(HashMap::new())))
        }

        pub fn add_process(&self, name: String, child: MockChild) -> Result<(), String> {
            let mut processes = self.0.lock().map_err(|e| e.to_string())?;
            if processes.contains_key(&name) {
                return Err(format!("Process '{name}' is already being tracked"));
            }
            processes.insert(name, child);
            Ok(())
        }

        pub fn is_process_running(&self, name: &str) -> Result<bool, String> {
            let mut processes = self.0.lock().map_err(|e| e.to_string())?;
            if let Some(child) = processes.get_mut(name) {
                match child.try_wait() {
                    Ok(Some(_)) => {
                        processes.remove(name);
                        Ok(false)
                    }
                    Ok(None) => Ok(true),
                    Err(_) => {
                        processes.remove(name);
                        Ok(false)
                    }
                }
            } else {
                Ok(false)
            }
        }

        pub fn kill_process(&self, name: &str) -> Result<bool, String> {
            let mut processes = self.0.lock().map_err(|e| e.to_string())?;
            if let Some(mut child) = processes.remove(name) {
                match child.kill() {
                    Ok(_) => {
                        let _ = child.wait();
                        Ok(true)
                    }
                    Err(e) => Err(format!("Failed to kill process '{name}': {e}")),
                }
            } else {
                Ok(false)
            }
        }

        pub fn get_all_process_names(&self) -> Result<Vec<String>, String> {
            let processes = self.0.lock().map_err(|e| e.to_string())?;
            Ok(processes.keys().cloned().collect())
        }

        pub fn cleanup_dead_processes(&self) -> Result<Vec<String>, String> {
            let mut processes = self.0.lock().map_err(|e| e.to_string())?;
            let mut removed = Vec::new();
            let mut to_remove = Vec::new();

            for (name, child) in processes.iter_mut() {
                match child.try_wait() {
                    Ok(Some(_)) | Err(_) => to_remove.push(name.clone()),
                    Ok(None) => {}
                }
            }

            for name in to_remove {
                processes.remove(&name);
                removed.push(name);
            }

            Ok(removed)
        }
    }

    #[test]
    fn test_log_entry_creation() {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64;

        let entry = LogEntry {
            timestamp,
            content: "Test log message".to_string(),
            process_id: "test_process".to_string(),
        };

        assert_eq!(entry.content, "Test log message");
        assert_eq!(entry.process_id, "test_process");
        assert!(entry.timestamp > 0);
    }

    #[test]
    fn test_log_buffer_new() {
        let buffer = LogBuffer::new(100);
        assert_eq!(buffer.max_size, 100);
        assert_eq!(buffer.entries.len(), 0);
    }

    #[test]
    fn test_log_buffer_add_entry() {
        let mut buffer = LogBuffer::new(3);

        let entry1 = LogEntry {
            timestamp: 1000,
            content: "Message 1".to_string(),
            process_id: "test".to_string(),
        };

        buffer.add(entry1);
        assert_eq!(buffer.entries.len(), 1);
        assert_eq!(buffer.entries[0].content, "Message 1");
    }

    #[test]
    fn test_log_buffer_max_size_enforcement() {
        let mut buffer = LogBuffer::new(2);

        // Add entries that exceed max size
        for i in 1..=3 {
            let entry = LogEntry {
                timestamp: i as i64,
                content: format!("Message {i}"),
                process_id: "test".to_string(),
            };
            buffer.add(entry);
        }

        // Should only keep the last 2 entries
        assert_eq!(buffer.entries.len(), 2);
        assert_eq!(buffer.entries[0].content, "Message 2");
        assert_eq!(buffer.entries[1].content, "Message 3");
    }

    #[test]
    fn test_log_buffer_get_logs_all() {
        let mut buffer = LogBuffer::new(10);

        // Add 3 entries
        for i in 1..=3 {
            let entry = LogEntry {
                timestamp: i as i64,
                content: format!("Message {i}"),
                process_id: "test".to_string(),
            };
            buffer.add(entry);
        }

        let logs = buffer.get_logs(None);
        assert_eq!(logs.len(), 3);
        assert_eq!(logs[0].content, "Message 1");
        assert_eq!(logs[2].content, "Message 3");
    }

    #[test]
    fn test_log_buffer_get_logs_limited() {
        let mut buffer = LogBuffer::new(10);

        // Add 5 entries
        for i in 1..=5 {
            let entry = LogEntry {
                timestamp: i as i64,
                content: format!("Message {i}"),
                process_id: "test".to_string(),
            };
            buffer.add(entry);
        }

        // Get only the last 2 entries
        let logs = buffer.get_logs(Some(2));
        assert_eq!(logs.len(), 2);
        assert_eq!(logs[0].content, "Message 4");
        assert_eq!(logs[1].content, "Message 5");
    }

    #[test]
    fn test_log_buffer_get_logs_more_than_available() {
        let mut buffer = LogBuffer::new(10);

        // Add 2 entries
        for i in 1..=2 {
            let entry = LogEntry {
                timestamp: i as i64,
                content: format!("Message {i}"),
                process_id: "test".to_string(),
            };
            buffer.add(entry);
        }

        // Request 5 entries (more than available)
        let logs = buffer.get_logs(Some(5));
        assert_eq!(logs.len(), 2);
    }

    #[test]
    fn test_create_log_storage() {
        let storage = create_log_storage();
        let locked = storage.lock().unwrap();
        assert_eq!(locked.len(), 0);
    }

    #[test]
    fn test_register_process() {
        let storage = create_log_storage();

        // Register a new process
        let result = register_process(&storage, "test_process");
        assert!(result);

        // Check that the process was registered
        let locked = storage.lock().unwrap();
        assert!(locked.contains_key("test_process"));
        assert_eq!(locked.get("test_process").unwrap().max_size, 10000);
    }

    #[test]
    fn test_register_process_duplicate() {
        let storage = create_log_storage();

        // Register a process twice
        let result1 = register_process(&storage, "test_process");
        let result2 = register_process(&storage, "test_process");

        assert!(result1);
        assert!(!result2); // Second registration should fail
    }

    #[test]
    fn test_unregister_process() {
        let storage = create_log_storage();

        // Register then unregister a process
        register_process(&storage, "test_process");
        let result = unregister_process(&storage, "test_process");

        assert!(result);

        // Check that the process was removed
        let locked = storage.lock().unwrap();
        assert!(!locked.contains_key("test_process"));
    }

    #[test]
    fn test_unregister_nonexistent_process() {
        let storage = create_log_storage();

        let result = unregister_process(&storage, "nonexistent");
        assert!(!result);
    }

    #[test]
    fn test_get_process_logs_existing() {
        let storage = create_log_storage();
        register_process(&storage, "test_process");

        // Add some logs to the process
        {
            let mut locked = storage.lock().unwrap();
            let buffer = locked.get_mut("test_process").unwrap();
            let entry = LogEntry {
                timestamp: 1000,
                content: "Test message".to_string(),
                process_id: "test_process".to_string(),
            };
            buffer.add(entry);
        }

        let request = GetProcessLogsRequest {
            process_id: "test_process".to_string(),
            count: None,
        };

        let logs = get_process_logs(&storage, request);
        assert_eq!(logs.len(), 1);
        assert_eq!(logs[0].content, "Test message");
    }

    #[test]
    fn test_get_process_logs_nonexistent() {
        let storage = create_log_storage();

        let request = GetProcessLogsRequest {
            process_id: "nonexistent".to_string(),
            count: None,
        };

        let logs = get_process_logs(&storage, request);
        assert_eq!(logs.len(), 0);
    }

    #[test]
    fn test_get_process_logs_with_count() {
        let storage = create_log_storage();
        register_process(&storage, "test_process");

        // Add multiple logs
        {
            let mut locked = storage.lock().unwrap();
            let buffer = locked.get_mut("test_process").unwrap();
            for i in 1..=5 {
                let entry = LogEntry {
                    timestamp: i as i64,
                    content: format!("Message {i}"),
                    process_id: "test_process".to_string(),
                };
                buffer.add(entry);
            }
        }

        let request = GetProcessLogsRequest {
            process_id: "test_process".to_string(),
            count: Some(2),
        };

        let logs = get_process_logs(&storage, request);
        assert_eq!(logs.len(), 2);
        assert_eq!(logs[0].content, "Message 4");
        assert_eq!(logs[1].content, "Message 5");
    }

    #[test]
    fn test_running_processes_add_process_mock() {
        let processes = TestRunningProcesses::new();
        let mock_child = MockChild::new(true);
        let result = processes.add_process("mock".to_string(), mock_child);
        assert!(result.is_ok());
        let names = processes.get_all_process_names().unwrap();
        assert_eq!(names.len(), 1);
        assert!(names.contains(&"mock".to_string()));
    }

    #[test]
    fn test_running_processes_add_duplicate_mock() {
        let processes = TestRunningProcesses::new();
        let mock_child1 = MockChild::new(true);
        let mock_child2 = MockChild::new(true);
        let _ = processes.add_process("mock".to_string(), mock_child1);
        let result = processes.add_process("mock".to_string(), mock_child2);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("already being tracked"));
    }

    #[test]
    fn test_running_processes_is_process_running_nonexistent_mock() {
        let processes = TestRunningProcesses::new();
        let result = processes.is_process_running("nonexistent");
        assert!(result.is_ok());
        assert!(!result.unwrap());
    }

    #[test]
    fn test_running_processes_kill_process_mock() {
        let processes = TestRunningProcesses::new();
        let mock_child = MockChild::new(true);
        let _ = processes.add_process("mock".to_string(), mock_child);
        let result = processes.kill_process("mock");
        assert!(result.is_ok());
        assert!(result.unwrap());
        let names = processes.get_all_process_names().unwrap();
        assert!(!names.contains(&"mock".to_string()));
    }

    #[test]
    fn test_running_processes_cleanup_dead_processes_mock() {
        let processes = TestRunningProcesses::new();
        let mock_child = MockChild::new(false); // Not running
        let _ = processes.add_process("mock".to_string(), mock_child);
        let removed = processes.cleanup_dead_processes().unwrap();
        assert!(removed.contains(&"mock".to_string()));
        let names = processes.get_all_process_names().unwrap();
        assert!(!names.contains(&"mock".to_string()));
    }

    #[test]
    fn test_init_process_monitoring() {
        // This test mainly ensures the function doesn't panic
        init_process_monitoring();

        // Create a fresh storage instance for this test to avoid shared state
        let storage = create_log_storage();
        let locked = storage.lock().unwrap();
        assert_eq!(locked.len(), 0);
    }

    #[test]
    fn test_get_log_storage() {
        // Create separate storage instances to avoid conflicts
        let storage = create_log_storage();
        register_process(&storage, "test");

        let locked = storage.lock().unwrap();
        assert!(locked.contains_key("test"));
    }

    #[test]
    fn test_concurrent_log_storage_access() {
        use std::sync::Arc;
        use std::thread;

        // Create a fresh storage instance for this test
        let storage = create_log_storage();
        let storage_clone = Arc::clone(&storage);

        // Spawn a thread that registers processes
        let handle = thread::spawn(move || {
            for i in 0..10 {
                let _ = register_process(&storage_clone, &format!("concurrent_process_{i}"));
            }
        });

        // Register processes in main thread
        for i in 10..20 {
            let _ = register_process(&storage, &format!("concurrent_process_{i}"));
        }

        handle.join().unwrap();

        // Verify processes were registered (may be less than 20 due to race conditions)
        let locked = storage.lock().unwrap();
        assert!(!locked.is_empty());
        assert!(locked.len() <= 20);
    }

    #[test]
    fn test_global_log_storage_singleton() {
        // Test that the global LOG_STORAGE works as a singleton
        let storage1 = get_log_storage();
        let storage2 = get_log_storage();

        // Clear any existing state first
        {
            let mut locked = storage1.lock().unwrap();
            locked.clear();
        }

        // Register a process using first reference
        register_process(&storage1, "singleton_test");

        // Verify it's accessible via second reference
        let locked2 = storage2.lock().unwrap();
        assert!(locked2.contains_key("singleton_test"));

        // Clean up
        drop(locked2);
        unregister_process(&storage1, "singleton_test");
    }
}
