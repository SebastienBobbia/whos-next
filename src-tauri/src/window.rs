//! Placement de la fenêtre sur l'écran courant (FE-07, FE-08, FE-14).
//!
//! La zone de travail vient de l'API Windows, comme dans l'application Python :
//! MonitorFromWindow + GetMonitorInfoW. Tauri ne donne que la taille totale de
//! l'écran, barre des tâches comprise.

use serde::Serialize;
use tauri::{LogicalSize, PhysicalPosition, PhysicalSize, Window};

#[derive(Serialize, Clone, Copy)]
pub struct WorkArea {
    /// Pixels physiques
    pub x: i32,
    pub y: i32,
    pub width: i32,
    pub height: i32,
    /// 1.0 à 96 dpi, 1.5 à 144 dpi, etc.
    pub scale: f64,
}

#[cfg(windows)]
fn work_area(window: &Window) -> Result<WorkArea, String> {
    use windows_sys::Win32::Foundation::{HWND, POINT, RECT};
    use windows_sys::Win32::Graphics::Gdi::{
        GetMonitorInfoW, MonitorFromPoint, MonitorFromWindow, MONITORINFO,
        MONITOR_DEFAULTTONEAREST,
    };

    let scale = window.scale_factor().map_err(|e| e.to_string())?;
    let hwnd = window.hwnd().map_err(|e| e.to_string())?.0 as HWND;

    let monitor = unsafe {
        if hwnd.is_null() {
            MonitorFromPoint(POINT { x: 0, y: 0 }, MONITOR_DEFAULTTONEAREST)
        } else {
            MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        }
    };

    let mut info: MONITORINFO = unsafe { std::mem::zeroed() };
    info.cbSize = std::mem::size_of::<MONITORINFO>() as u32;
    let ok = unsafe { GetMonitorInfoW(monitor, &mut info) };
    if ok == 0 {
        return Err("GetMonitorInfoW a échoué".into());
    }

    let RECT {
        left,
        top,
        right,
        bottom,
    } = info.rcWork;
    Ok(WorkArea {
        x: left,
        y: top,
        width: right - left,
        height: bottom - top,
        scale,
    })
}

#[cfg(not(windows))]
fn work_area(window: &Window) -> Result<WorkArea, String> {
    let monitor = window
        .current_monitor()
        .map_err(|e| e.to_string())?
        .ok_or("aucun écran")?;
    let size = monitor.size();
    let position = monitor.position();
    Ok(WorkArea {
        x: position.x,
        y: position.y,
        width: size.width as i32,
        height: size.height as i32,
        scale: monitor.scale_factor(),
    })
}

/// Zone de travail et facteur d'échelle de l'écran qui porte la fenêtre.
#[tauri::command]
pub fn monitor_work_area(window: Window) -> Result<WorkArea, String> {
    work_area(&window)
}

/// Largeur et hauteur retenues après calage, en pixels logiques.
#[derive(Serialize)]
pub struct FitResult {
    pub width: f64,
    pub height: f64,
}

/// Colle la fenêtre au bord droit de la zone de travail, sur toute sa hauteur (FE-07).
///
/// `desired_width` est une largeur logique calculée par l'interface à partir du
/// plus long nom. Elle est bornée par `min_width` et par 18 % de la largeur de
/// l'écran. Le cadre de la fenêtre est déduit de la hauteur pour que la fenêtre
/// entière tienne dans la zone de travail (FE-08).
#[tauri::command]
pub fn fit_to_right_edge(
    window: Window,
    desired_width: f64,
    min_width: f64,
    max_width_ratio: f64,
) -> Result<FitResult, String> {
    let area = work_area(&window)?;
    let scale = area.scale;

    let work_w = f64::from(area.width) / scale;
    let work_h = f64::from(area.height) / scale;

    let max_w = work_w * max_width_ratio;
    let width = desired_width.clamp(min_width.min(max_w), max_w);

    // Décor de la fenêtre : différence entre taille extérieure et intérieure.
    let outer = window.outer_size().map_err(|e| e.to_string())?;
    let inner = window.inner_size().map_err(|e| e.to_string())?;
    let chrome_w = f64::from(outer.width.saturating_sub(inner.width)) / scale;
    let chrome_h = f64::from(outer.height.saturating_sub(inner.height)) / scale;

    let height = (work_h - chrome_h).max(100.0);

    window
        .set_size(LogicalSize::new(width, height))
        .map_err(|e| e.to_string())?;

    let outer_w_physical = ((width + chrome_w) * scale).round() as i32;
    window
        .set_position(PhysicalPosition::new(
            area.x + area.width - outer_w_physical,
            area.y,
        ))
        .map_err(|e| e.to_string())?;

    Ok(FitResult { width, height })
}

/// Restaure la taille des vues Équipe et Présence sans toucher à la position (FE-03).
#[tauri::command]
pub fn restore_window(window: Window, width: f64, height: f64) -> Result<(), String> {
    window
        .set_size(LogicalSize::new(width, height))
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn set_always_on_top(window: Window, on_top: bool) -> Result<(), String> {
    window.set_always_on_top(on_top).map_err(|e| e.to_string())
}

/// Ferme l'application après la Célébration (SE-10).
#[tauri::command]
pub fn quit_app(app: tauri::AppHandle) {
    app.exit(0);
}

/// Évite un avertissement quand PhysicalSize n'est pas utilisé sur une plateforme.
#[allow(dead_code)]
fn _unused(_: PhysicalSize<u32>) {}
