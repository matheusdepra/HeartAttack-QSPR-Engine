#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::Mutex;
use tauri::Manager;
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::ShellExt;

struct SidecarState {
    child: Mutex<Option<CommandChild>>,
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Resolve and create application data directories
            let app_data_dir = app.path().app_data_dir().expect("failed to get app data dir");
            let db_dir = app_data_dir.join("data");
            
            std::fs::create_dir_all(&db_dir).expect("failed to create data dir");
            std::fs::create_dir_all(db_dir.join("plots")).expect("failed to create plots dir");
            std::fs::create_dir_all(db_dir.join("qspr_results")).expect("failed to create qspr_results dir");

            let db_path = db_dir.join("drugs.db");
            let plots_dir = db_dir.join("plots");
            let results_dir = db_dir.join("qspr_results");

            // Resolve sidecar and set environment variables
            let shell = app.shell();
            let sidecar_command = shell.sidecar("api")
                .expect("failed to find api sidecar")
                .env("DATABASE_PATH", db_path.to_string_lossy().to_string())
                .env("PLOTS_DIR", plots_dir.to_string_lossy().to_string())
                .env("QSPR_RESULTS_DIR", results_dir.to_string_lossy().to_string())
                .env("BACKEND_HOST", "127.0.0.1")
                .env("BACKEND_PORT", "5555");

            // Spawn the python backend
            let (_, child) = sidecar_command.spawn().expect("failed to spawn api sidecar");

            // Manage child state to clean it up on exit
            app.manage(SidecarState {
                child: Mutex::new(Some(child)),
            });

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| {
            if let tauri::RunEvent::Exit = event {
                // Safely kill sidecar when app exits
                if let Some(state) = app_handle.try_state::<SidecarState>() {
                    let mut child_lock = state.child.lock().unwrap();
                    if let Some(child) = child_lock.take() {
                        let _ = child.kill();
                        println!("CardioQSPR Backend terminated successfully.");
                    }
                }
            }
        });
}
