# 🧗 Math Climber – Deluxe Edition 2.0

Un mini videojuego hecho con **Python + Pygame**: sube una escalera de 10 escalones resolviendo ecuaciones de suma, resta y multiplicación antes de que se te acabe el tiempo o las vidas.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?logo=pygame&logoColor=white)
![Licencia](https://img.shields.io/badge/Licencia-MIT-yellow)

<!-- Agrega aquí una captura o GIF del juego, por ejemplo: -->
<!-- ![Captura del juego](docs/preview.png) -->

## 🎮 Descripción

Cada acierto te hace subir un escalón; cada fallo te cuesta una vida. Encadena respuestas correctas para conseguir una **racha** que multiplica tus puntos, vigila la **barra de tiempo** antes de que se agote, y usa tu **power-up** de tiempo extra en el momento justo para llegar a la meta.

## ✨ Características

- ❤️ **Sistema de vidas**: 3 corazones. Si llegan a 0, es Game Over.
- 🏆 **Puntuación con racha**: encadena aciertos y el multiplicador de puntos sube hasta x5.
- 🎚️ **3 niveles de dificultad**: Fácil, Normal y Difícil (cambian el rango de números, las operaciones y el tiempo disponible).
- ⏱️ **Temporizador por pregunta** con barra de color dinámico (verde → rojo).
- ⚡ **Power-up de tiempo extra**: pulsa `E` para sumar +5 segundos (3 usos por partida).
- 💾 **Récord persistente**: tu mejor puntuación se guarda en un archivo local y se conserva entre partidas.
- ⏸️ **Pausa** en cualquier momento con `ESC`.
- 🎨 **Estilo visual moderno**: fondo con degradado y parallax, estrellas parpadeantes, efectos de brillo (glow), partículas al acertar/fallar y *screen shake* al equivocarte.
- 🚶 **Animación suave** del personaje al subir escalones (en vez de saltos instantáneos).
- ⌨️ Soporte para teclado numérico (numpad) además de la fila de números.

## 🖥️ Requisitos

- Python 3.9 o superior
- [Pygame](https://www.pygame.org/) 2.x

## 📦 Instalación

```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/tu-repositorio.git

# (Opcional) crea un entorno virtual
python3 -m venv venv
En Windows: venv\Scripts\activate

# Instala las dependencias
pip install pygame
```

## ▶️ Cómo jugar

```bash
python3 math_climber_deluxe.py
```

1. En el menú principal, pulsa **JUGAR**.
2. Elige tu dificultad: **Fácil**, **Normal** o **Difícil**.
3. Resuelve la ecuación que aparece en pantalla y escribe el resultado.
4. Pulsa **ENTER** para confirmar tu respuesta.
5. Llega al escalón 10 antes de quedarte sin vidas o sin tiempo.

## 🎹 Controles

| Tecla | Acción |
|---|---|
| `0-9` / Numpad | Escribir el número de tu respuesta |
| `Enter` | Confirmar respuesta |
| `Backspace` | Borrar el último dígito escrito |
| `E` | Usar power-up de +5 segundos |
| `Esc` | Pausar / reanudar |
| Clic del mouse | Navegar los menús y botones |

## 🎚️ Dificultades

| Dificultad | Números | Operaciones | Tiempo por pregunta |
|---|---|---|---|
| Fácil | 1 – 20 | Suma y resta | 15 s |
| Normal | 1 – 99 | Suma y resta | 12 s |
| Difícil | 1 – 50 (2-12 en multiplicación) | Suma, resta y multiplicación | 9 s |

## 🧮 Sistema de puntuación

- Cada respuesta correcta suma **100 puntos base**.
- Por cada 3 aciertos seguidos, el **multiplicador** sube (hasta x5 con una racha de 9+).
- Fallar una pregunta o dejar que el tiempo se agote reinicia la racha y resta una vida.
- Tu mejor puntuación se guarda automáticamente al terminar la partida (por victoria o Game Over) si superaste el récord anterior.

## 🚧 Ideas para el futuro

- [ ] Efectos de sonido y música
- [ ] Más niveles de dificultad / modo "contrarreloj infinito"
- [ ] Tabla de mejores puntuaciones (top 5-10)
- [ ] Distintos personajes o skins desbloqueables
- [ ] Versión web con Pygbag

## 🤝 Contribuciones

Las sugerencias, *issues* y *pull requests* son bienvenidos. Si tienes una idea para una nueva mecánica, ¡ábrela como issue!

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Puedes usar, modificar y distribuir el código libremente, dando crédito al autor original.
