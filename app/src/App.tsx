import { getCurrentWindow } from "@tauri-apps/api/window";
import ClinicalPanel from "./components/ClinicalPanel";

const appWindow = getCurrentWindow();

/**
 * Shell de la estación clínica de simPEATC (ventana frameless: barra de título
 * propia con región arrastrable y controles de ventana).
 */
export default function App() {
  return (
    <div className="app">
      <header className="topbar" data-tauri-drag-region>
        <h1 data-tauri-drag-region>simPEATC</h1>
        <span className="hint" data-tauri-drag-region>
          Estación de Potenciales Evocados Auditivos
        </span>
        <div className="winbtns">
          <button className="winbtn" title="Minimizar" onClick={() => appWindow.minimize()}>
            –
          </button>
          <button className="winbtn" title="Maximizar" onClick={() => appWindow.toggleMaximize()}>
            □
          </button>
          <button className="winbtn close" title="Cerrar" onClick={() => appWindow.close()}>
            ✕
          </button>
        </div>
      </header>
      <ClinicalPanel />
    </div>
  );
}
