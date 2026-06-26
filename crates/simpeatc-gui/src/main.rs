//! simPEATC - Interfaz grafica del simulador ABR.
//!
//! Controles de intensidad, promediaciones y oido; captura el registro via el
//! motor `aep-core` (`EvokedPotentialEngine`) y dibuja la curva del canal en un
//! canvas, junto con la FSP alcanzada y las ondas detectadas.

use aep_core::{Ear, EvokedPotentialEngine, Level, Protocol, Recording, Subject, Waveform};
use iced::widget::canvas::{self, Frame, Geometry, Path, Stroke, Text};
use iced::widget::{button, column, row, slider, text, Canvas};
use iced::{mouse, Color, Element, Length, Point, Rectangle, Renderer, Size, Theme};

fn main() -> iced::Result {
    iced::application(App::default, App::update, App::view)
        .title("simPEATC - Simulador ABR")
        .theme(theme)
        .run()
}

fn theme(_state: &App) -> Theme {
    Theme::Dark
}

/// Construye el protocolo ABR a partir de los controles de la GUI.
fn build_protocol(ear: Ear, intensity_db: f64, sweeps: u32) -> Protocol {
    let mut p = Protocol::abr_click(ear);
    p.stimulus.level = Level::DbNhl(intensity_db);
    p.acquisition.sweeps = sweeps;
    p
}

/// Simula un registro con el sujeto por defecto (adulto sano).
fn simulate(ear: Ear, intensity_db: f64, sweeps: u32) -> Recording {
    let protocol = build_protocol(ear, intensity_db, sweeps);
    EvokedPotentialEngine::simulate(&protocol, &Subject::default())
}

struct App {
    ear: Ear,
    intensity_db: f64,
    sweeps: u32,
    rec: Recording,
}

#[derive(Debug, Clone)]
enum Message {
    IntensityChanged(f64),
    SweepsChanged(u32),
    ToggleEar,
    Capture,
}

impl Default for App {
    fn default() -> Self {
        let ear = Ear::Right;
        let intensity_db = 80.0;
        let sweeps = 2000;
        Self {
            ear,
            intensity_db,
            sweeps,
            rec: simulate(ear, intensity_db, sweeps),
        }
    }
}

impl App {
    fn update(&mut self, message: Message) {
        match message {
            Message::IntensityChanged(v) => self.intensity_db = v,
            Message::SweepsChanged(v) => self.sweeps = v,
            Message::ToggleEar => self.ear = self.ear.opposite(),
            Message::Capture => {
                self.rec = simulate(self.ear, self.intensity_db, self.sweeps);
            }
        }
    }

    fn view(&self) -> Element<'_, Message> {
        let picos: String = if self.rec.detected.is_empty() {
            "Sin ondas detectadas".to_string()
        } else {
            self.rec
                .detected
                .iter()
                .map(|w| format!("{}: {:.2} ms", w.label, w.latency_ms))
                .collect::<Vec<_>>()
                .join("   ")
        };

        let controles = column![
            text(format!("Oido: {}", self.ear.label())).size(18),
            button("Cambiar oido").on_press(Message::ToggleEar),
            text(format!("Intensidad: {:.0} dB nHL", self.intensity_db)),
            slider(10.0..=90.0, self.intensity_db, Message::IntensityChanged).step(5.0),
            text(format!("Promediaciones: {}", self.sweeps)),
            slider(1..=4000, self.sweeps, Message::SweepsChanged).step(50u32),
            text(format!("FSP: {:.1}", self.rec.fsp)),
            text(format!(
                "Sweeps: {} aceptados / {} rechazados",
                self.rec.accepted_sweeps, self.rec.rejected_sweeps
            ))
            .size(13),
            button("Capturar").on_press(Message::Capture),
            text(picos).size(14),
        ]
        .spacing(10)
        .width(Length::Fixed(280.0));

        let canal = self.rec.primary().cloned().unwrap_or_default();
        let grafico = Canvas::new(AbrPlot { wave: canal })
            .width(Length::Fill)
            .height(Length::Fill);

        row![controles, grafico].spacing(20).padding(16).into()
    }
}

/// Programa de canvas que dibuja la curva del canal.
struct AbrPlot {
    wave: Waveform,
}

impl<Message> canvas::Program<Message> for AbrPlot {
    type State = ();

    fn draw(
        &self,
        _state: &Self::State,
        renderer: &Renderer,
        _theme: &Theme,
        bounds: Rectangle,
        _cursor: mouse::Cursor,
    ) -> Vec<Geometry> {
        let mut frame = Frame::new(renderer, bounds.size());
        let w = bounds.width;
        let h = bounds.height;

        // Fondo y eje base (linea cero).
        frame.fill_rectangle(Point::ORIGIN, Size::new(w, h), Color::from_rgb(0.07, 0.07, 0.1));
        let zero_y = h / 2.0;
        frame.stroke(
            &Path::line(Point::new(0.0, zero_y), Point::new(w, zero_y)),
            Stroke::default().with_color(Color::from_rgb(0.3, 0.3, 0.35)),
        );

        if self.wave.is_empty() {
            return vec![frame.into_geometry()];
        }

        // Rango temporal real de la ventana (incluye el pre-estimulo negativo).
        let t0 = *self.wave.times_ms.first().unwrap();
        let t1 = *self.wave.times_ms.last().unwrap();
        let span = (t1 - t0).max(1e-6);

        let max_amp = self.wave.max_abs_uv().max(0.1) as f32;
        let y_scale = (h / 2.0 - 10.0) / max_amp;

        let mut path = canvas::path::Builder::new();
        for (i, (t, a)) in self.wave.points().enumerate() {
            let x = ((t - t0) / span) as f32 * w;
            let y = zero_y - (a as f32) * y_scale;
            if i == 0 {
                path.move_to(Point::new(x, y));
            } else {
                path.line_to(Point::new(x, y));
            }
        }
        frame.stroke(
            &path.build(),
            Stroke::default()
                .with_width(1.5)
                .with_color(Color::from_rgb(0.2, 0.9, 0.6)),
        );

        frame.fill_text(Text {
            content: "Amplitud (uV) vs Tiempo (ms)".into(),
            position: Point::new(8.0, 8.0),
            color: Color::from_rgb(0.7, 0.7, 0.7),
            size: 14.0.into(),
            ..Text::default()
        });

        vec![frame.into_geometry()]
    }
}
