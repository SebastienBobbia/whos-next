//! Placement de la fenêtre sur l'écran courant (FE-07, FE-08, FE-14).
//!
//! La zone de travail vient de l'API Windows, comme dans l'application Python :
//! MonitorFromWindow + GetMonitorInfoW. Tauri ne donne que la taille totale de
//! l'écran, barre des tâches comprise.
//!
//! Le calage se fait en deux temps : on pose une taille, on mesure les bords
//! réellement visibles, puis on corrige. Sous Windows 10 et 11, le rectangle
//! d'une fenêtre déborde de plusieurs pixels invisibles sur les côtés et en
//! bas (poignées de redimensionnement) : sans cette correction, la fenêtre
//! semble décollée du bord droit.

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

/// Marges invisibles du cadre, en pixels physiques.
#[derive(Clone, Copy, Default)]
struct Invisible {
    left: i32,
    top: i32,
    right: i32,
    bottom: i32,
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
    if unsafe { GetMonitorInfoW(monitor, &mut info) } == 0 {
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

/// Écart entre le rectangle de la fenêtre et ses bords réellement visibles.
#[cfg(windows)]
fn invisible_margins(window: &Window) -> Invisible {
    use windows_sys::Win32::Foundation::{HWND, RECT};
    use windows_sys::Win32::Graphics::Dwm::{DwmGetWindowAttribute, DWMWA_EXTENDED_FRAME_BOUNDS};

    let (Ok(hwnd), Ok(position), Ok(size)) = (
        window.hwnd(),
        window.outer_position(),
        window.outer_size(),
    ) else {
        return Invisible::default();
    };

    let mut visible: RECT = unsafe { std::mem::zeroed() };
    let hr = unsafe {
        DwmGetWindowAttribute(
            hwnd.0 as HWND,
            DWMWA_EXTENDED_FRAME_BOUNDS as u32,
            &mut visible as *mut RECT as *mut std::ffi::c_void,
            std::mem::size_of::<RECT>() as u32,
        )
    };
    if hr != 0 {
        return Invisible::default();
    }

    Invisible {
        left: visible.left - position.x,
        top: visible.top - position.y,
        right: (position.x + size.width as i32) - visible.right,
        bottom: (position.y + size.height as i32) - visible.bottom,
    }
}

#[cfg(not(windows))]
fn invisible_margins(_window: &Window) -> Invisible {
    Invisible::default()
}

/// Zone de travail et facteur d'échelle de l'écran qui porte la fenêtre.
#[tauri::command]
pub fn monitor_work_area(window: Window) -> Result<WorkArea, String> {
    work_area(&window)
}

/// Largeur et hauteur visibles après calage, en pixels logiques.
#[derive(Serialize)]
pub struct FitResult {
    pub width: f64,
    pub height: f64,
}

/// Colle la fenêtre au bord droit de la zone de travail, sur toute sa hauteur (FE-07).
///
/// `desired_width` est une largeur logique calculée par l'interface à partir du
/// plus long nom affiché. Elle est bornée par `min_width` et par une fraction de
/// la largeur de l'écran. Ce sont les bords **visibles** qui touchent la zone de
/// travail, cadre compris (FE-08).
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
    let max_w = work_w * max_width_ratio;
    let width = desired_width.clamp(min_width.min(max_w), max_w);

    // Première pose : largeur voulue, hauteur approchée.
    let outer = window.outer_size().map_err(|e| e.to_string())?;
    let inner = window.inner_size().map_err(|e| e.to_string())?;
    let chrome_h = f64::from(outer.height.saturating_sub(inner.height)) / scale;
    window
        .set_size(LogicalSize::new(width, (f64::from(area.height) / scale) - chrome_h))
        .map_err(|e| e.to_string())?;

    // Mesure des bords visibles, puis correction de la hauteur et de la position.
    let margins = invisible_margins(&window);
    let outer = window.outer_size().map_err(|e| e.to_string())?;
    let inner = window.inner_size().map_err(|e| e.to_string())?;

    let visible_h = outer.height as i32 - margins.top - margins.bottom;
    let correction = area.height - visible_h;
    let inner_h = (inner.height as i32 + correction).max(100) as u32;
    if correction != 0 {
        window
            .set_size(PhysicalSize::new(inner.width, inner_h))
            .map_err(|e| e.to_string())?;
    }

    let outer = window.outer_size().map_err(|e| e.to_string())?;
    window
        .set_position(PhysicalPosition::new(
            area.x + area.width - outer.width as i32 + margins.right,
            area.y - margins.top,
        ))
        .map_err(|e| e.to_string())?;

    let visible_w = outer.width as i32 - margins.left - margins.right;
    Ok(FitResult {
        width: f64::from(visible_w) / scale,
        height: f64::from(area.height) / scale,
    })
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
