mod store;

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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            load_team,
            save_team,
            import_icon,
            remove_icon,
            read_icon
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
