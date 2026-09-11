// Empêche l'ouverture d'une console Windows en release. NE PAS SUPPRIMER.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    whos_next_lib::run()
}
