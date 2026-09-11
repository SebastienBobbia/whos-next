mod store;
mod window;

use store::Member;

#[tauri::command]
fn load_team() -> Result<Vec<Member>, String> {
    store::load_team()
}

#[tauri::command]
fn save_team(members: Vec<Member>) -> Result<(), String> {
    store::save_team(members)
}

#[tauri::command]
fn import_icon(source: String) -> Result<String, String> {
    store::import_icon(&source)
}

#[tauri::command]
fn remove_icon(filename: String) {
    store::remove_icon(&filename);
}

#[tauri::command]
fn read_icon(filename: String) -> Result<String, String> {
    store::read_icon(&filename)
}

/// Sans WebView2, la fenêtre ne peut pas s'afficher : on explique au lieu de
/// disparaître sans rien dire (DI-07).
#[cfg(windows)]
fn require_webview2() -> bool {
    if tauri::webview_version().is_ok() {
        return true;
    }

    use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONERROR, MB_OK};

    let title: Vec<u16> = "Who's Next?\0".encode_utf16().collect();
    let text: Vec<u16> = concat!(
        "Microsoft Edge WebView2 Runtime est nécessaire pour lancer cette application.\n\n",
        "Installez-le depuis https://developer.microsoft.com/microsoft-edge/webview2/ ",
        "puis relancez WhosNext.exe.\0"
    )
    .encode_utf16()
    .collect();

    unsafe {
        MessageBoxW(
            std::ptr::null_mut(),
            text.as_ptr(),
            title.as_ptr(),
            MB_OK | MB_ICONERROR,
        );
    }
    false
}

#[cfg(not(windows))]
fn require_webview2() -> bool {
    true
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    if !require_webview2() {
        return;
    }

    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            load_team,
            save_team,
            import_icon,
            remove_icon,
            read_icon,
            window::monitor_work_area,
            window::fit_to_right_edge,
            window::restore_window,
            window::set_always_on_top,
            window::quit_app
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
