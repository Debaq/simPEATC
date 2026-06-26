// Evita una segunda ventana de consola en Windows en modo release.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    simpeatc_lib::run();
}
