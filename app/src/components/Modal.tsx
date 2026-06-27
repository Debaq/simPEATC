// Modal genérico: overlay + tarjeta centrada. Solo cierra de forma explícita
// (✕ o botón Aceptar): NO se cierra al clicar el fondo ni al perder el foco.

import { type ReactNode } from "react";

interface ModalProps {
  title: string;
  onClose: () => void;
  children: ReactNode;
  /** Ancho máximo de la tarjeta (px). */
  width?: number;
}

export default function Modal({ title, onClose, children, width = 720 }: ModalProps) {
  return (
    <div className="modal-backdrop">
      <div className="modal-card" style={{ maxWidth: width }}>
        <div className="modal-head">
          <span className="section-title" style={{ margin: 0 }}>
            {title}
          </span>
          <button className="modal-x" onClick={onClose} aria-label="Cerrar">
            ✕
          </button>
        </div>
        <div className="modal-body">{children}</div>
        <div className="modal-foot">
          <button className="primary" onClick={onClose}>
            Aceptar
          </button>
        </div>
      </div>
    </div>
  );
}
