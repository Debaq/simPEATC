//! simPEATC - Interfaz grafica del simulador ABR.
//!
//! Scaffold inicial: controles de intensidad y promediaciones, captura de la
//! curva via `abr-core` y dibujo de la senal en un canvas.

use abr_core::{AbrGenerator, Ear, StimParams, Waveform, DURATION_MS};
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

struct App {
    params: StimParams,
    wave: Waveform,
}

#[derive(Debug, Clone)]
enum Message {
    IntensityChanged(f64),
    AveragesChanged(u32),
    ToggleEar,
    Capture,
}

impl Default for App {
    fn default() -> Self {
        let params = StimParams::default();
        Self {
            params,
            wave: AbrGenerator::new(params).generate(),
        }
    }
}

impl App {
    fn update(&mut self, message: Message) {
        match message {
            Message::IntensityChanged(v) => self.params.intensity_db = v,
            Message::AveragesChanged(v) => self.params.averages = v,
            Message::ToggleEar => {
                self.params.ear = match self.params.ear {
                    Ear::Right => Ear::Left,
                    Ear::Left => Ear::Right,
                };
            }
            Message::Capture => {
                self.wave = AbrGenerator::new(self.params).generate();
            }
        }
    }

    fn view(&self) -> Element<'_, Message> {
        let gen = AbrGenerator::new(self.params);
        let picos: String = gen
            .peaks()
            .iter()
            .map(|p| format!("{}: {:.2} ms", p.label, p.latency_ms))
            .collect::<Vec<_>>()
            .join("   ");

        let controles = column![
            text(format!("Oido: {}", self.params.ear.label())).size(18),
            button("Cambiar oido").on_press(Message::ToggleEar),
            text(format!("Intensidad: {:.0} dB nHL", self.params.intensity_db)),
            slider(10.0..=90.0, self.params.intensity_db, Message::IntensityChanged).step(5.0),
            text(format!("Promediaciones: {}", self.params.averages)),
            slider(1..=4000, self.params.averages, Message::AveragesChanged).step(50u32),
            text(format!("SNR (FSP): {:.0}%", gen.snr() * 100.0)),
            button("Capturar").on_press(Message::Capture),
            text(picos).size(14),
        ]
        .spacing(10)
        .width(Length::Fixed(260.0));

        let grafico = Canvas::new(AbrPlot { wave: &self.wave })
            .width(Length::Fill)
            .height(Length::Fill);

        row![controles, grafico].spacing(20).padding(16).into()
    }
}

/// Programa de canvas que dibuja la curva ABR.
struct AbrPlot<'a> {
    wave: &'a Waveform,
}

impl<Message> canvas::Program<Message> for AbrPlot<'_> {
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

        // Escalado: x en [0, DURATION_MS], y centrado segun amplitud maxima.
        let max_amp = self
            .wave
            .amplitudes_uv
            .iter()
            .fold(0.1_f64, |m, &a| m.max(a.abs())) as f32;
        let y_scale = (h / 2.0 - 10.0) / max_amp;

        let mut path = canvas::path::Builder::new();
        for (i, (t, a)) in self.wave.points().enumerate() {
            let x = (t / DURATION_MS) as f32 * w;
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
