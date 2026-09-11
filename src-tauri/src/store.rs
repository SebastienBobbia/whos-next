//! Persistance de l'Équipe : %APPDATA%\WhosNext\team.json et son dossier icons\.
//!
//! Les identifiants PE-xx et IC-xx renvoient à docs/spec/06-persistance.md
//! et docs/spec/02-icones.md.

use chrono::Local;
use include_dir::{include_dir, Dir};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

/// Équipe embarquée dans l'exe, copiée au premier lancement (PE-10, PE-11).
static DEFAULT_DATA: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/../default_data");

/// Seule version de team.json acceptée. Ne jamais l'incrémenter : voir ADR 0002.
const VERSION: u64 = 2;

fn is_false(b: &bool) -> bool {
    !*b
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Member {
    pub name: String,
    #[serde(default)]
    pub icon_type: String,
    #[serde(default)]
    pub icon_value: String,
    /// Absent : écrit seulement quand il vaut true (PE-02).
    #[serde(default, skip_serializing_if = "is_false")]
    pub absent: bool,
}

#[derive(Serialize, Deserialize)]
struct TeamFile {
    version: u64,
    members: Vec<Member>,
}

pub fn data_dir() -> PathBuf {
    let base = std::env::var_os("APPDATA")
        .or_else(|| std::env::var_os("USERPROFILE"))
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    base.join("WhosNext")
}

pub fn icons_dir() -> PathBuf {
    data_dir().join("icons")
}

fn team_file() -> PathBuf {
    data_dir().join("team.json")
}

/// Crée le dossier de données et son sous-dossier icons\ s'ils manquent (PE-01).
fn ensure_dirs() -> Result<(), String> {
    fs::create_dir_all(icons_dir()).map_err(|e| format!("dossier de données : {e}"))
}

/// Lit le fichier et retourne ses Membres, ou None si le fichier est illisible (PE-07).
fn parse_team(raw: &str) -> Option<Vec<Member>> {
    let value: serde_json::Value = serde_json::from_str(raw).ok()?;
    if value.get("version").and_then(|v| v.as_u64()) != Some(VERSION) {
        return None;
    }
    let members = value.get("members")?.as_array()?;
    Some(
        members
            .iter()
            .filter_map(|m| serde_json::from_value::<Member>(m.clone()).ok())
            .filter(|m| !m.name.is_empty())
            .collect(),
    )
}

fn file_is_readable(path: &Path) -> bool {
    match fs::read_to_string(path) {
        Ok(raw) => parse_team(&raw).is_some(),
        Err(_) => false,
    }
}

/// Copie l'Équipe embarquée quand team.json n'existe pas encore (PE-11).
fn seed_from_embedded() -> Result<(), String> {
    let Some(embedded_json) = DEFAULT_DATA.get_file("team.json") else {
        return Ok(());
    };
    fs::write(team_file(), embedded_json.contents())
        .map_err(|e| format!("copie de l'équipe embarquée : {e}"))?;

    if let Some(embedded_icons) = DEFAULT_DATA.get_dir("icons") {
        for file in embedded_icons.files() {
            let Some(name) = file.path().file_name() else {
                continue;
            };
            let _ = fs::write(icons_dir().join(name), file.contents());
        }
    }
    Ok(())
}

/// Charge l'Équipe. Un fichier illisible donne une Équipe vide, sans rien écrire (PE-07).
pub fn load_team() -> Result<Vec<Member>, String> {
    ensure_dirs()?;
    let path = team_file();
    if !path.exists() {
        seed_from_embedded()?;
    }
    if !path.exists() {
        return Ok(Vec::new());
    }
    match fs::read_to_string(&path) {
        Ok(raw) => Ok(parse_team(&raw).unwrap_or_default()),
        Err(_) => Ok(Vec::new()),
    }
}

/// Écrit l'Équipe. Un fichier illisible est mis de côté au lieu d'être écrasé (PE-07, PE-08).
pub fn save_team(members: Vec<Member>) -> Result<(), String> {
    ensure_dirs()?;
    let path = team_file();
    if path.exists() && !file_is_readable(&path) {
        let stamp = Local::now().format("%Y%m%d-%H%M%S");
        let aside = data_dir().join(format!("team.json.illisible-{stamp}"));
        fs::rename(&path, &aside).map_err(|e| format!("mise de côté du fichier illisible : {e}"))?;
    }
    let content = serde_json::to_string_pretty(&TeamFile {
        version: VERSION,
        members,
    })
    .map_err(|e| format!("sérialisation : {e}"))?;
    fs::write(&path, content).map_err(|e| format!("écriture de team.json : {e}"))
}

/// Copie une image dans icons\ et retourne son nom de fichier (IC-11).
/// La copie a toujours lieu avant toute suppression de l'ancienne Icône (IC-07).
pub fn import_icon(source: &str) -> Result<String, String> {
    ensure_dirs()?;
    let src = PathBuf::from(source);
    let bytes = fs::read(&src).map_err(|e| format!("lecture de l'image : {e}"))?;

    let stem = src
        .file_stem()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_else(|| "icone".to_string());
    let ext = src
        .extension()
        .map(|s| format!(".{}", s.to_string_lossy()))
        .unwrap_or_default();

    let mut name = format!("{stem}{ext}");
    let mut counter = 1;
    while icons_dir().join(&name).exists() {
        name = format!("{stem}_{counter}{ext}");
        counter += 1;
    }
    fs::write(icons_dir().join(&name), bytes).map_err(|e| format!("copie de l'image : {e}"))?;
    Ok(name)
}

/// Supprime un fichier image. Un échec est ignoré (IC-12).
pub fn remove_icon(filename: &str) {
    let _ = fs::remove_file(icons_dir().join(filename));
}

fn mime_for(filename: &str) -> &'static str {
    let lower = filename.to_ascii_lowercase();
    if lower.ends_with(".svg") {
        "image/svg+xml"
    } else if lower.ends_with(".jpg") || lower.ends_with(".jpeg") {
        "image/jpeg"
    } else if lower.ends_with(".gif") {
        "image/gif"
    } else if lower.ends_with(".bmp") {
        "image/bmp"
    } else if lower.ends_with(".webp") {
        "image/webp"
    } else {
        "image/png"
    }
}

/// Retourne l'image sous forme de data URL, prête pour un <img> (PF-11 : une seule lecture).
pub fn read_icon(filename: &str) -> Result<String, String> {
    let path = icons_dir().join(filename);
    let bytes = fs::read(&path).map_err(|e| format!("lecture de l'icône : {e}"))?;
    let encoded = base64_encode(&bytes);
    Ok(format!("data:{};base64,{}", mime_for(filename), encoded))
}

fn base64_encode(bytes: &[u8]) -> String {
    const TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut out = String::with_capacity(bytes.len().div_ceil(3) * 4);
    for chunk in bytes.chunks(3) {
        let b0 = chunk[0] as u32;
        let b1 = *chunk.get(1).unwrap_or(&0) as u32;
        let b2 = *chunk.get(2).unwrap_or(&0) as u32;
        let n = (b0 << 16) | (b1 << 8) | b2;
        out.push(TABLE[(n >> 18) as usize & 63] as char);
        out.push(TABLE[(n >> 12) as usize & 63] as char);
        out.push(if chunk.len() > 1 {
            TABLE[(n >> 6) as usize & 63] as char
        } else {
            '='
        });
        out.push(if chunk.len() > 2 {
            TABLE[n as usize & 63] as char
        } else {
            '='
        });
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_refuse_une_version_differente_de_2() {
        assert!(parse_team(r#"{"version": 3, "members": []}"#).is_none());
        assert!(parse_team(r#"{"members": ["Alice"]}"#).is_none());
        assert!(parse_team("pas du json").is_none());
    }

    #[test]
    fn parse_ignore_les_membres_sans_nom() {
        let raw = r#"{"version": 2, "members": [
            {"name": "Alice", "icon_type": "emoji", "icon_value": "🐱"},
            {"name": ""},
            {"icon_type": "image"}
        ]}"#;
        let members = parse_team(raw).expect("fichier lisible");
        assert_eq!(members.len(), 1);
        assert_eq!(members[0].name, "Alice");
    }

    #[test]
    fn absent_est_facultatif_et_omis_quand_il_est_faux() {
        let raw = r#"{"version": 2, "members": [
            {"name": "Alice", "icon_type": "", "icon_value": ""},
            {"name": "Bob", "icon_type": "", "icon_value": "", "absent": true}
        ]}"#;
        let members = parse_team(raw).expect("fichier lisible");
        assert!(!members[0].absent);
        assert!(members[1].absent);

        let written = serde_json::to_string(&TeamFile {
            version: VERSION,
            members,
        })
        .unwrap();
        assert!(!written.contains(r#""name":"Alice","icon_type":"","icon_value":"","absent""#));
        assert!(written.contains(r#""absent":true"#));
    }

    #[test]
    fn base64_encode_gere_le_remplissage() {
        assert_eq!(base64_encode(b"a"), "YQ==");
        assert_eq!(base64_encode(b"ab"), "YWI=");
        assert_eq!(base64_encode(b"abc"), "YWJj");
        assert_eq!(base64_encode(&[0u8, 255, 128]), "AP+A");
    }
}
