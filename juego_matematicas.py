import pygame
import random
import sys
import math
import json
import os

pygame.init()

ANCHO = 1000
ALTO = 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Math Climber - Deluxe Edition 2.0")
reloj = pygame.time.Clock()

NEGRO = (8, 8, 18)
BLANCO = (255, 255, 255)
CIELO_ARRIBA = (18, 18, 42)
CIELO_ABAJO = (58, 28, 88)
AZUL_CIELO = (135, 206, 250)
AZUL_NEON = (0, 191, 255)
VERDE_NEON = (57, 255, 20)
ROJO_NEON = (255, 40, 90)
AMARILLO = (255, 215, 0)
NARANJA_NEON = (255, 140, 0)
MORADO_NEON = (180, 70, 255)
GRIS_BOTON = (40, 40, 65)
GRIS_BOTON_HOVER = (72, 72, 112)
DORADO = (255, 215, 0)

fuente_titulo = pygame.font.Font(None, 100)
fuente_grande = pygame.font.Font(None, 72)
fuente_mediana = pygame.font.Font(None, 48)
fuente_pequena = pygame.font.Font(None, 30)
fuente_hud = pygame.font.Font(None, 32)

RUTA_HIGHSCORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_climber_highscore.json")


def cargar_high_score():
    try:
        with open(RUTA_HIGHSCORE, "r") as f:
            datos = json.load(f)
            return int(datos.get("high_score", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 0


def guardar_high_score(valor):
    try:
        with open(RUTA_HIGHSCORE, "w") as f:
            json.dump({"high_score": valor}, f)
    except OSError:
        pass

MENU = 0
SELECCION_DIFICULTAD = 1
JUGANDO = 2
PAUSA = 3
VICTORIA = 4
GAME_OVER = 5
estado_actual = MENU

DIFICULTADES = {
    "facil": {"rango": (1, 20), "operadores": ["+", "-"], "tiempo": 15, "nombre": "Fácil"},
    "normal": {"rango": (1, 99), "operadores": ["+", "-"], "tiempo": 12, "nombre": "Normal"},
    "dificil": {"rango": (1, 50), "operadores": ["+", "-", "*"], "tiempo": 9, "nombre": "Difícil"},
}

MAX_DIGITOS = 3
VIDAS_MAX = 3
USOS_TIEMPO_EXTRA_MAX = 3
META = 10

escalon_actual = 0
ecuacion_actual = ""
respuesta_correcta = 0
respuesta_escrita = ""
mensaje_resultado = ""
color_mensaje = BLANCO
tiempo_mensaje = 0

vidas = VIDAS_MAX
puntuacion = 0
racha = 0
racha_maxima = 0
multiplicador = 1
dificultad_actual = "normal"
tiempo_restante = DIFICULTADES[dificultad_actual]["tiempo"]
tiempo_max = tiempo_restante
usos_tiempo_extra = USOS_TIEMPO_EXTRA_MAX
high_score = cargar_high_score()
nuevo_record = False

personaje_x = 0.0
personaje_y = 0.0
shake_timer = 0
shake_magnitud = 0

particulas = []
textos_flotantes = []

dt_actual = 0.0
tiempo_global = 0.0

superficie_juego = pygame.Surface((ANCHO, ALTO))

ESTRELLAS = [
    {
        "x": random.randint(0, ANCHO),
        "y": random.randint(0, ALTO // 2),
        "tam": random.randint(1, 3),
        "vel": random.uniform(1.0, 3.0),
        "fase": random.uniform(0, 6.28),
    }
    for _ in range(60)
]

NUBES = [
    {
        "x": random.randint(0, ANCHO),
        "y": random.randint(30, 160),
        "vel": random.uniform(6, 16),
        "escala": random.uniform(0.6, 1.3),
    }
    for _ in range(5)
]

def interpolar_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def calcular_posicion_escalon(escalon):
    x = 100 + (escalon * 80) + 15
    y = 600 - (escalon * 50) - 45
    return float(x), float(y)


def generar_ecuacion(dificultad):
    config = DIFICULTADES[dificultad]
    operador = random.choice(config["operadores"])
    if operador == "*":
        num1 = random.randint(2, 12)
        num2 = random.randint(2, 12)
        resultado = num1 * num2
    else:
        lo, hi = config["rango"]
        num1 = random.randint(lo, hi)
        num2 = random.randint(lo, hi)
        if operador == "+":
            resultado = num1 + num2
        else:
            if num1 < num2:
                num1, num2 = num2, num1
            resultado = num1 - num2
    return f"{num1} {operador} {num2}", resultado


def crear_explosion(x, y, color, cantidad):
    for _ in range(cantidad):
        particulas.append(Particula(x, y, color))

class Boton:
    def __init__(self, texto, x, y, ancho, alto, color_normal, color_hover, accion):
        self.texto = texto
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.accion = accion

    def dibujar(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse_pos)
        color_actual = self.color_hover if hover else self.color_normal

        if hover:
            glow = pygame.Surface((self.rect.width + 24, self.rect.height + 24), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*self.color_hover, 90), glow.get_rect(), border_radius=22)
            pantalla.blit(glow, (self.rect.x - 12, self.rect.y - 12))

        pygame.draw.rect(pantalla, color_actual, self.rect, border_radius=15)
        pygame.draw.rect(pantalla, BLANCO, self.rect, 2, border_radius=15)

        texto_surf = fuente_mediana.render(self.texto, True, BLANCO)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        pantalla.blit(texto_surf, texto_rect)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.accion()


class Particula:
    def __init__(self, x, y, color):
        angulo = random.uniform(0, 2 * math.pi)
        velocidad = random.uniform(80, 220)
        self.x = x
        self.y = y
        self.vx = math.cos(angulo) * velocidad
        self.vy = math.sin(angulo) * velocidad - 120
        self.color = color
        self.vida = 1.0
        self.radio = random.randint(2, 5)

    def actualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 400 * dt
        self.vida -= dt * 1.1

    def dibujar(self, surf):
        if self.vida > 0:
            alpha = max(0, min(255, int(self.vida * 255)))
            tam = self.radio * 2
            s = pygame.Surface((tam, tam), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.radio, self.radio), self.radio)
            surf.blit(s, (self.x - self.radio, self.y - self.radio))


class TextoFlotante:
    def __init__(self, x, y, texto, color, tam=34):
        self.x = x
        self.y = y
        self.texto = texto
        self.color = color
        self.vida = 1.2
        self.fuente = pygame.font.Font(None, tam)

    def actualizar(self, dt):
        self.y -= 45 * dt
        self.vida -= dt * 0.9

    def dibujar(self, surf):
        if self.vida > 0:
            alpha = max(0, min(255, int(self.vida * 255)))
            render = self.fuente.render(self.texto, True, self.color)
            render.set_alpha(alpha)
            surf.blit(render, (self.x, self.y))

def ir_a_seleccion_dificultad():
    global estado_actual
    estado_actual = SELECCION_DIFICULTAD


def iniciar_juego(dificultad):
    global escalon_actual, ecuacion_actual, respuesta_correcta, respuesta_escrita
    global mensaje_resultado, estado_actual, vidas, puntuacion, racha, racha_maxima
    global multiplicador, dificultad_actual, tiempo_restante, tiempo_max, usos_tiempo_extra
    global personaje_x, personaje_y, nuevo_record, particulas, textos_flotantes, shake_timer

    dificultad_actual = dificultad
    config = DIFICULTADES[dificultad]
    tiempo_max = config["tiempo"]
    tiempo_restante = tiempo_max

    escalon_actual = 0
    respuesta_escrita = ""
    mensaje_resultado = ""
    vidas = VIDAS_MAX
    puntuacion = 0
    racha = 0
    racha_maxima = 0
    multiplicador = 1
    usos_tiempo_extra = USOS_TIEMPO_EXTRA_MAX
    nuevo_record = False
    particulas = []
    textos_flotantes = []
    shake_timer = 0

    personaje_x, personaje_y = calcular_posicion_escalon(0)
    ecuacion_actual, respuesta_correcta = generar_ecuacion(dificultad_actual)
    estado_actual = JUGANDO


def pausar_juego():
    global estado_actual
    if estado_actual == JUGANDO:
        estado_actual = PAUSA


def reanudar_juego():
    global estado_actual
    estado_actual = JUGANDO


def volver_menu():
    global estado_actual
    estado_actual = MENU


def salir_juego():
    pygame.quit()
    sys.exit()


def responder(es_correcta):
    global escalon_actual, puntuacion, racha, racha_maxima, multiplicador, vidas
    global mensaje_resultado, color_mensaje, tiempo_mensaje, estado_actual
    global ecuacion_actual, respuesta_correcta, respuesta_escrita, tiempo_restante
    global shake_timer, shake_magnitud, high_score, nuevo_record

    cx, cy = calcular_posicion_escalon(escalon_actual)

    if es_correcta:
        racha += 1
        racha_maxima = max(racha_maxima, racha)
        multiplicador = 1 + min(racha // 3, 4)
        puntos = 100 * multiplicador
        puntuacion += puntos
        escalon_actual += 1
        mensaje_resultado = "¡CORRECTO!"
        color_mensaje = VERDE_NEON
        crear_explosion(cx + 20, cy, VERDE_NEON, 18)
        textos_flotantes.append(TextoFlotante(cx, cy - 20, f"+{puntos}", DORADO))
        if racha >= 3:
            textos_flotantes.append(TextoFlotante(cx - 10, cy - 55, f"RACHA x{multiplicador}", NARANJA_NEON, tam=28))
    else:
        vidas -= 1
        racha = 0
        multiplicador = 1
        mensaje_resultado = f"Fallo. Era {respuesta_correcta}"
        color_mensaje = ROJO_NEON
        shake_timer = 15
        shake_magnitud = 8
        crear_explosion(cx + 20, cy, ROJO_NEON, 14)

    if escalon_actual >= META:
        if puntuacion > high_score:
            high_score = puntuacion
            nuevo_record = True
            guardar_high_score(high_score)
        estado_actual = VICTORIA
        return

    if vidas <= 0:
        if puntuacion > high_score:
            high_score = puntuacion
            nuevo_record = True
            guardar_high_score(high_score)
        estado_actual = GAME_OVER
        return

    ecuacion_actual, respuesta_correcta = generar_ecuacion(dificultad_actual)
    respuesta_escrita = ""
    tiempo_restante = tiempo_max
    tiempo_mensaje = pygame.time.get_ticks()

btn_jugar = Boton("JUGAR", ANCHO // 2 - 100, 400, 200, 60, AZUL_NEON, (0, 100, 200), ir_a_seleccion_dificultad)
btn_salir_menu = Boton("SALIR", ANCHO // 2 - 60, 480, 120, 50, ROJO_NEON, (150, 0, 0), salir_juego)

btn_facil = Boton("FÁCIL", ANCHO // 2 - 140, 220, 280, 60, VERDE_NEON, (0, 150, 0), lambda: iniciar_juego("facil"))
btn_normal = Boton("NORMAL", ANCHO // 2 - 140, 320, 280, 60, AZUL_NEON, (0, 100, 200), lambda: iniciar_juego("normal"))
btn_dificil = Boton("DIFÍCIL", ANCHO // 2 - 140, 420, 280, 60, ROJO_NEON, (150, 0, 40), lambda: iniciar_juego("dificil"))
btn_volver_dif = Boton("VOLVER", ANCHO // 2 - 90, 520, 180, 50, GRIS_BOTON, GRIS_BOTON_HOVER, volver_menu)

btn_continuar = Boton("CONTINUAR", ANCHO // 2 - 130, 320, 260, 60, VERDE_NEON, (0, 150, 0), reanudar_juego)
btn_menu_pausa = Boton("MENÚ PRINCIPAL", ANCHO // 2 - 150, 400, 300, 60, GRIS_BOTON, GRIS_BOTON_HOVER, volver_menu)

btn_reintentar_victoria = Boton("JUGAR DE NUEVO", ANCHO // 2 - 260, ALTO // 2 + 130, 240, 55, VERDE_NEON, (0, 150, 0),
                                 lambda: iniciar_juego(dificultad_actual))
btn_menu_victoria = Boton("MENÚ", ANCHO // 2 + 20, ALTO // 2 + 130, 240, 55, GRIS_BOTON, GRIS_BOTON_HOVER, volver_menu)

btn_reintentar_go = Boton("REINTENTAR", ANCHO // 2 - 260, ALTO // 2 + 130, 240, 55, VERDE_NEON, (0, 150, 0),
                           lambda: iniciar_juego(dificultad_actual))
btn_menu_go = Boton("MENÚ", ANCHO // 2 + 20, ALTO // 2 + 130, 240, 55, GRIS_BOTON, GRIS_BOTON_HOVER, volver_menu)

def dibujar_nube(surf, x, y, escala):
    s = pygame.Surface((200, 100), pygame.SRCALPHA)
    color = (255, 255, 255, 35)
    pygame.draw.ellipse(s, color, (0, 30, int(90 * escala), int(45 * escala)))
    pygame.draw.ellipse(s, color, (int(35 * escala), 5, int(75 * escala), int(50 * escala)))
    pygame.draw.ellipse(s, color, (int(65 * escala), 25, int(90 * escala), int(45 * escala)))
    surf.blit(s, (x, y))


def dibujar_fondo(surf, dt):
    for y in range(0, ALTO, 2):
        t = y / ALTO
        color = interpolar_color(CIELO_ARRIBA, CIELO_ABAJO, t)
        pygame.draw.line(surf, color, (0, y), (ANCHO, y), 2)

    for nube in NUBES:
        nube["x"] += nube["vel"] * dt
        if nube["x"] > ANCHO + 150:
            nube["x"] = -200
        dibujar_nube(surf, nube["x"], nube["y"], nube["escala"])

    for estrella in ESTRELLAS:
        alpha = int(120 + 100 * math.sin(tiempo_global * estrella["vel"] + estrella["fase"]))
        alpha = max(30, min(255, alpha))
        tam = estrella["tam"]
        s = pygame.Surface((tam * 4, tam * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha), (tam * 2, tam * 2), tam)
        surf.blit(s, (estrella["x"] - tam * 2, estrella["y"] - tam * 2))


def dibujar_escalones_deluxe(surf):
    for i in range(META + 1):
        x = 100 + (i * 80)
        y = 600 - (i * 50)

        glow = pygame.Surface((100, 60), pygame.SRCALPHA)
        color_glow = (255, 215, 0, 70) if i == META else (0, 150, 255, 60)
        pygame.draw.ellipse(glow, color_glow, (5, 5, 90, 50))
        surf.blit(glow, (x - 10, y - 10))

        color_bloque = (255, 190, 60) if i == META else (30, 144, 255)
        pygame.draw.rect(surf, color_bloque, (x, y, 70, 20), border_radius=8)
        pygame.draw.rect(surf, AZUL_CIELO, (x, y, 70, 20), 3, border_radius=8)

        brillo = pygame.Surface((60, 8), pygame.SRCALPHA)
        pygame.draw.rect(brillo, (255, 255, 255, 90), brillo.get_rect(), border_radius=4)
        surf.blit(brillo, (x + 5, y + 3))

        num_texto = fuente_pequena.render(str(i), True, NEGRO if i == META else BLANCO)
        surf.blit(num_texto, (x + 30, y + 2))


def dibujar_personaje_deluxe(surf, x, y):
    bob = math.sin(tiempo_global * 6) * 3
    y = y + bob

    sombra = pygame.Surface((44, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, 90), sombra.get_rect())
    surf.blit(sombra, (x - 2, y + 42))

    pygame.draw.rect(surf, (255, 200, 100), (x, y + 20, 40, 25), border_radius=8)
    pygame.draw.circle(surf, (255, 220, 140), (int(x + 20), int(y + 10)), 18)
    pygame.draw.circle(surf, NEGRO, (int(x + 12), int(y + 8)), 5)
    pygame.draw.circle(surf, NEGRO, (int(x + 28), int(y + 8)), 5)
    pygame.draw.circle(surf, BLANCO, (int(x + 10), int(y + 6)), 2)
    pygame.draw.circle(surf, BLANCO, (int(x + 26), int(y + 6)), 2)
    pygame.draw.circle(surf, (255, 150, 150), (int(x + 8), int(y + 15)), 4)
    pygame.draw.circle(surf, (255, 150, 150), (int(x + 32), int(y + 15)), 4)


def dibujar_corazon(surf, x, y, lleno):
    color = ROJO_NEON if lleno else (55, 55, 75)
    r = 8
    pygame.draw.circle(surf, color, (x - r // 2, y), r)
    pygame.draw.circle(surf, color, (x + r // 2, y), r)
    pygame.draw.polygon(surf, color, [(x - r - 1, y + 2), (x + r + 1, y + 2), (x, y + r + 9)])


def dibujar_hud(surf):
    panel = pygame.Surface((300, 140), pygame.SRCALPHA)
    pygame.draw.rect(panel, (15, 15, 30, 160), panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, AZUL_NEON, panel.get_rect(), 2, border_radius=16)
    surf.blit(panel, (20, 20))

    surf.blit(fuente_hud.render(f"Puntos: {puntuacion}", True, BLANCO), (35, 30))
    surf.blit(fuente_pequena.render(f"Récord: {high_score}", True, AMARILLO), (35, 56))
    surf.blit(fuente_pequena.render(f"Escalón: {escalon_actual}/{META}", True, AZUL_CIELO), (35, 82))

    if racha >= 2:
        color_racha = NARANJA_NEON if racha < 6 else ROJO_NEON
        surf.blit(fuente_pequena.render(f"Racha x{multiplicador}", True, color_racha), (35, 108))

    for i in range(VIDAS_MAX):
        dibujar_corazon(surf, ANCHO - 40 - i * 40, 45, i < vidas)

    ancho_barra = 300
    x_barra = ANCHO // 2 - ancho_barra // 2
    y_barra = 20
    proporcion = max(0, min(1, tiempo_restante / tiempo_max))
    color_barra = interpolar_color(ROJO_NEON, VERDE_NEON, proporcion)
    pygame.draw.rect(surf, (30, 30, 50), (x_barra, y_barra, ancho_barra, 18), border_radius=9)
    pygame.draw.rect(surf, color_barra, (x_barra, y_barra, int(ancho_barra * proporcion), 18), border_radius=9)
    pygame.draw.rect(surf, BLANCO, (x_barra, y_barra, ancho_barra, 18), 2, border_radius=9)

    color_pu = AZUL_CIELO if usos_tiempo_extra > 0 else (90, 90, 110)
    texto_pu = fuente_pequena.render(f"[E] +5s de tiempo extra (x{usos_tiempo_extra})", True, color_pu)
    surf.blit(texto_pu, (ANCHO // 2 - texto_pu.get_width() // 2, 45))


def dibujar_menu():
    dibujar_fondo(pantalla, dt_actual)

    pulso = (math.sin(tiempo_global * 2) + 1) / 2
    color_titulo = interpolar_color(AMARILLO, BLANCO, pulso * 0.3)

    titulo_sombra = fuente_titulo.render("MATH CLIMBER", True, NEGRO)
    pantalla.blit(titulo_sombra, (ANCHO // 2 - 185, 145))
    titulo = fuente_titulo.render("MATH CLIMBER", True, color_titulo)
    pantalla.blit(titulo, (ANCHO // 2 - 190, 140))

    subtitulo = fuente_mediana.render("¡Sube la escalera resolviendo ecuaciones!", True, AZUL_CIELO)
    pantalla.blit(subtitulo, (ANCHO // 2 - subtitulo.get_width() // 2, 225))

    texto_record = fuente_mediana.render(f"Récord: {high_score} puntos", True, DORADO)
    pantalla.blit(texto_record, (ANCHO // 2 - texto_record.get_width() // 2, 280))

    inst = fuente_pequena.render("Vidas, racha, temporizador y power-ups te esperan", True, (200, 200, 220))
    pantalla.blit(inst, (ANCHO // 2 - inst.get_width() // 2, 340))

    btn_jugar.dibujar(pantalla)
    btn_salir_menu.dibujar(pantalla)


def dibujar_seleccion_dificultad():
    dibujar_fondo(pantalla, dt_actual)

    titulo = fuente_grande.render("Elige tu dificultad", True, BLANCO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 120))

    btn_facil.dibujar(pantalla)
    btn_normal.dibujar(pantalla)
    btn_dificil.dibujar(pantalla)
    btn_volver_dif.dibujar(pantalla)

    descripciones = {
        "facil": "Números del 1 al 20 · Suma y resta · 15 s por pregunta",
        "normal": "Números del 1 al 99 · Suma y resta · 12 s por pregunta",
        "dificil": "Suma, resta y multiplicación · 9 s por pregunta",
    }
    posiciones_y = {"facil": 290, "normal": 390, "dificil": 490}
    for clave, texto in descripciones.items():
        render = fuente_pequena.render(texto, True, (200, 200, 220))
        pantalla.blit(render, (ANCHO // 2 - render.get_width() // 2, posiciones_y[clave]))


def dibujar_juego():
    superficie_juego.fill((0, 0, 0))
    dibujar_fondo(superficie_juego, dt_actual)
    dibujar_escalones_deluxe(superficie_juego)
    dibujar_personaje_deluxe(superficie_juego, personaje_x, personaje_y)

    x_meta = 100 + (META * 80) + 8
    y_meta = 600 - (META * 50) - 75
    pygame.draw.polygon(superficie_juego, DORADO, [(x_meta + 25, y_meta), (x_meta + 6, y_meta + 45), (x_meta + 44, y_meta + 45)])
    pygame.draw.polygon(superficie_juego, AMARILLO, [(x_meta + 25, y_meta + 7), (x_meta + 13, y_meta + 38), (x_meta + 37, y_meta + 38)])
    texto_meta = fuente_pequena.render("META", True, NEGRO)
    superficie_juego.blit(texto_meta, (x_meta + 3, y_meta + 48))

    panel_ec = pygame.Surface((380, 90), pygame.SRCALPHA)
    pygame.draw.rect(panel_ec, (15, 15, 30, 170), panel_ec.get_rect(), border_radius=20)
    pygame.draw.rect(panel_ec, MORADO_NEON, panel_ec.get_rect(), 2, border_radius=20)
    superficie_juego.blit(panel_ec, (ANCHO // 2 - 190, 100))
    texto_ec = fuente_grande.render(f"{ecuacion_actual} = ?", True, BLANCO)
    superficie_juego.blit(texto_ec, (ANCHO // 2 - texto_ec.get_width() // 2, 125))

    caja_rect = pygame.Rect(ANCHO // 2 - 70, 230, 140, 70)
    pygame.draw.rect(superficie_juego, (25, 25, 45), caja_rect, border_radius=18)
    pulso = int(155 + 100 * math.sin(tiempo_global * 4))
    pygame.draw.rect(superficie_juego, (0, pulso, 255), caja_rect, 4, border_radius=18)
    if respuesta_escrita:
        input_texto = fuente_grande.render(respuesta_escrita, True, BLANCO)
        superficie_juego.blit(input_texto, input_texto.get_rect(center=caja_rect.center))
    else:
        ph = fuente_pequena.render("¿?", True, (110, 110, 160))
        superficie_juego.blit(ph, ph.get_rect(center=caja_rect.center))

    inst = fuente_pequena.render("Escribe el número · ENTER confirma · ESC pausa", True, (180, 180, 200))
    superficie_juego.blit(inst, (ANCHO // 2 - inst.get_width() // 2, 320))

    if mensaje_resultado and (pygame.time.get_ticks() - tiempo_mensaje < 1500):
        msg = fuente_mediana.render(mensaje_resultado, True, color_mensaje)
        msg_rect = msg.get_rect(center=(ANCHO // 2, 400))
        fondo_msg = pygame.Surface((msg_rect.width + 40, msg_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(fondo_msg, (0, 0, 0, 160), fondo_msg.get_rect(), border_radius=12)
        superficie_juego.blit(fondo_msg, (msg_rect.x - 20, msg_rect.y - 10))
        superficie_juego.blit(msg, msg_rect)

    for p in particulas:
        p.dibujar(superficie_juego)
    for t in textos_flotantes:
        t.dibujar(superficie_juego)

    dibujar_hud(superficie_juego)

    if shake_timer > 0:
        offset = (random.randint(-shake_magnitud, shake_magnitud), random.randint(-shake_magnitud, shake_magnitud))
    else:
        offset = (0, 0)
    pantalla.fill(NEGRO)
    pantalla.blit(superficie_juego, offset)


def dibujar_pausa():
    pantalla.blit(superficie_juego, (0, 0))
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    pantalla.blit(overlay, (0, 0))

    titulo = fuente_grande.render("PAUSA", True, BLANCO)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 220))

    btn_continuar.dibujar(pantalla)
    btn_menu_pausa.dibujar(pantalla)


def dibujar_victoria():
    pantalla.fill(NEGRO)

    if random.random() < 0.5:
        crear_explosion(random.randint(0, ANCHO), -10,
                         random.choice([AZUL_NEON, VERDE_NEON, AMARILLO, MORADO_NEON]), 2)
    for p in particulas[:]:
        p.actualizar(dt_actual)
        p.dibujar(pantalla)
        if p.vida <= 0:
            particulas.remove(p)

    pygame.draw.rect(pantalla, DORADO, (ANCHO // 2 - 270, ALTO // 2 - 200, 540, 380), border_radius=30)
    pygame.draw.rect(pantalla, AMARILLO, (ANCHO // 2 - 260, ALTO // 2 - 190, 520, 360), border_radius=25)

    titulo_victoria = fuente_titulo.render("¡VICTORIA!", True, NEGRO)
    pantalla.blit(titulo_victoria, (ANCHO // 2 - titulo_victoria.get_width() // 2, ALTO // 2 - 170))

    subtitulo = fuente_mediana.render("¡Eres un genio de las matemáticas!", True, NEGRO)
    pantalla.blit(subtitulo, (ANCHO // 2 - subtitulo.get_width() // 2, ALTO // 2 - 90))

    texto_puntos = fuente_mediana.render(f"Puntuación: {puntuacion}", True, NEGRO)
    pantalla.blit(texto_puntos, (ANCHO // 2 - texto_puntos.get_width() // 2, ALTO // 2 - 35))

    mejor_multiplicador = 1 + min(racha_maxima // 3, 4)
    texto_racha = fuente_pequena.render(f"Mejor racha: x{mejor_multiplicador}", True, NEGRO)
    pantalla.blit(texto_racha, (ANCHO // 2 - texto_racha.get_width() // 2, ALTO // 2 + 10))

    if nuevo_record:
        texto_nr = fuente_pequena.render("¡NUEVO RÉCORD!", True, ROJO_NEON)
        pantalla.blit(texto_nr, (ANCHO // 2 - texto_nr.get_width() // 2, ALTO // 2 + 45))

    btn_reintentar_victoria.dibujar(pantalla)
    btn_menu_victoria.dibujar(pantalla)


def dibujar_game_over():
    dibujar_fondo(pantalla, dt_actual)
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((40, 0, 10, 150))
    pantalla.blit(overlay, (0, 0))

    pygame.draw.rect(pantalla, ROJO_NEON, (ANCHO // 2 - 270, ALTO // 2 - 200, 540, 380), border_radius=30)
    pygame.draw.rect(pantalla, (35, 10, 20), (ANCHO // 2 - 260, ALTO // 2 - 190, 520, 360), border_radius=25)

    titulo = fuente_titulo.render("GAME OVER", True, ROJO_NEON)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 2 - 170))

    texto_escalon = fuente_mediana.render(f"Llegaste al escalón {escalon_actual}/{META}", True, BLANCO)
    pantalla.blit(texto_escalon, (ANCHO // 2 - texto_escalon.get_width() // 2, ALTO // 2 - 80))

    texto_puntos = fuente_mediana.render(f"Puntuación: {puntuacion}", True, BLANCO)
    pantalla.blit(texto_puntos, (ANCHO // 2 - texto_puntos.get_width() // 2, ALTO // 2 - 25))

    if nuevo_record:
        texto_nr = fuente_pequena.render("¡NUEVO RÉCORD!", True, AMARILLO)
        pantalla.blit(texto_nr, (ANCHO // 2 - texto_nr.get_width() // 2, ALTO // 2 + 15))
    else:
        texto_rec = fuente_pequena.render(f"Récord actual: {high_score}", True, (210, 210, 210))
        pantalla.blit(texto_rec, (ANCHO // 2 - texto_rec.get_width() // 2, ALTO // 2 + 15))

    btn_reintentar_go.dibujar(pantalla)
    btn_menu_go.dibujar(pantalla)

jugando = True
while jugando:
    dt_actual = reloj.tick(60) / 1000.0
    tiempo_global += dt_actual

    # 1. GESTIÓN DE EVENTOS
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            salir_juego()

        if estado_actual == MENU:
            btn_jugar.manejar_evento(evento)
            btn_salir_menu.manejar_evento(evento)

        elif estado_actual == SELECCION_DIFICULTAD:
            btn_facil.manejar_evento(evento)
            btn_normal.manejar_evento(evento)
            btn_dificil.manejar_evento(evento)
            btn_volver_dif.manejar_evento(evento)

        elif estado_actual == JUGANDO:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pausar_juego()
                elif evento.key == pygame.K_BACKSPACE:
                    respuesta_escrita = respuesta_escrita[:-1]
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if len(respuesta_escrita) > 0:
                        try:
                            valor_jugador = int(respuesta_escrita)
                            responder(valor_jugador == respuesta_correcta)
                        except ValueError:
                            pass
                elif evento.key == pygame.K_e:
                    if usos_tiempo_extra > 0:
                        usos_tiempo_extra -= 1
                        tiempo_restante += 5
                        textos_flotantes.append(TextoFlotante(personaje_x, personaje_y - 60, "+5s", AZUL_CIELO))
                        crear_explosion(personaje_x + 20, personaje_y, AZUL_CIELO, 10)
                elif (pygame.K_0 <= evento.key <= pygame.K_9) or (pygame.K_KP0 <= evento.key <= pygame.K_KP9):
                    if len(respuesta_escrita) < MAX_DIGITOS:
                        if evento.key >= pygame.K_KP0:
                            digito = evento.key - pygame.K_KP0
                        else:
                            digito = evento.key - pygame.K_0
                        respuesta_escrita += str(digito)

        elif estado_actual == PAUSA:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                reanudar_juego()
            btn_continuar.manejar_evento(evento)
            btn_menu_pausa.manejar_evento(evento)

        elif estado_actual == VICTORIA:
            btn_reintentar_victoria.manejar_evento(evento)
            btn_menu_victoria.manejar_evento(evento)

        elif estado_actual == GAME_OVER:
            btn_reintentar_go.manejar_evento(evento)
            btn_menu_go.manejar_evento(evento)

    if estado_actual == JUGANDO:
        tiempo_restante -= dt_actual
        if tiempo_restante <= 0:
            tiempo_restante = 0
            responder(False)

        objetivo_x, objetivo_y = calcular_posicion_escalon(escalon_actual)
        personaje_x += (objetivo_x - personaje_x) * min(1, 8 * dt_actual)
        personaje_y += (objetivo_y - personaje_y) * min(1, 8 * dt_actual)

        for p in particulas[:]:
            p.actualizar(dt_actual)
            if p.vida <= 0:
                particulas.remove(p)

        for t in textos_flotantes[:]:
            t.actualizar(dt_actual)
            if t.vida <= 0:
                textos_flotantes.remove(t)

        if shake_timer > 0:
            shake_timer -= 1

    # 3. DIBUJADO SEGÚN ESTADO
    if estado_actual == MENU:
        dibujar_menu()
    elif estado_actual == SELECCION_DIFICULTAD:
        dibujar_seleccion_dificultad()
    elif estado_actual == JUGANDO:
        dibujar_juego()
    elif estado_actual == PAUSA:
        dibujar_pausa()
    elif estado_actual == VICTORIA:
        dibujar_victoria()
    elif estado_actual == GAME_OVER:
        dibujar_game_over()

    pygame.display.flip()

pygame.quit()
sys.exit()