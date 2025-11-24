import pygame
import cv2

import os

# === CONFIGURACIÓN INICIAL ===
# Nota: pygame.init() será llamado dentro de run_launcher()

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PATH = os.path.join(BASE_DIR, "main.py")
ICON_PATH = os.path.join(BASE_DIR, "icons", "puppet_icon.png")
VIDEO_PATH = os.path.join(BASE_DIR, "assets", "tutorial.mp4")
POSTER_PATH = os.path.join(BASE_DIR, "assets", "miniatura.jpg")

# Tamaños iniciales globales
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Estado del video
video_playing = False
video_paused = False
video_expanded = False
cap = None
dragging_bar = False

# Último frame
last_frame_surface = None


# ===============================
#   FUNCIONES DEL LAUNCHER
# ===============================

def load_icon(name, size=(40, 40)):
    path = os.path.join(BASE_DIR, "icons", name)
    icon = pygame.image.load(path)
    return pygame.transform.scale(icon, size)


def play_video():
    global cap, video_playing, video_paused, video_expanded, video_rect, button_rect, last_frame_surface
    if not os.path.exists(VIDEO_PATH):
        print(f"No se encontró el video: {VIDEO_PATH}")
        return

    cap = cv2.VideoCapture(VIDEO_PATH)
    video_playing = True
    video_paused = False
    video_expanded = True
    video_rect.update(40, 40, SCREEN_WIDTH - 80, 420)

    button_rect.y = video_rect.bottom + 40
    button_rect.centerx = SCREEN_WIDTH // 2

    last_frame_surface = video_poster.copy()


def stop_video():
    global cap, video_playing
    if cap:
        cap.release()
        cap = None
    video_playing = False


def draw_video_frame(surface, rect):
    global cap, last_frame_surface, video_paused, video_playing

    if not video_playing:
        surface.blit(video_poster, rect.topleft)
        return

    if video_paused:
        surface.blit(last_frame_surface, rect.topleft)
        return

    ret, frame = cap.read()
    if not ret:
        stop_video()
        return

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    frame = pygame.transform.scale(frame, (rect.width, rect.height))
    surface.blit(frame, rect.topleft)
    last_frame_surface = frame.copy()


def draw_progress_bar(surface, rect):
    global cap
    if not cap:
        return None, 0

    total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    current = cap.get(cv2.CAP_PROP_POS_FRAMES)
    progress = 0 if total == 0 else current / total

    bar_width = rect.width - 40
    bar_height = 6
    bar_x = rect.left + 20
    bar_y = rect.bottom + 10

    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), border_radius=3)
    progress_x = bar_x + int(progress * bar_width)
    pygame.draw.circle(surface, WHITE, (progress_x, bar_y + bar_height // 2), 8)

    return pygame.Rect(bar_x, bar_y, bar_width, bar_height), progress


def seek_video(pos_x, bar_rect):
    global cap
    if not cap:
        return
    total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    rel_x = max(0, min(pos_x - bar_rect.x, bar_rect.width))
    progress = rel_x / bar_rect.width
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(progress * total))


def launch_main():
    stop_video()
    return True



# ===================================
#   FUNCIÓN PRINCIPAL DEL LAUNCHER
# ===================================

def run_launcher():
    global video_playing, video_paused, video_expanded, cap, dragging_bar, last_frame_surface
    global video_rect, button_rect, video_poster
    global WHITE, DARK, GRAY, BLUE
    global play_icon, pause_icon
    global last_frame_surface

    pygame.init()

    WHITE = (30, 35, 40)
    DARK = (255, 255, 255)
    GRAY = (90, 90, 90)
    BLUE = (233, 233, 233)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Puppet Memphis - Inicio")
    pygame.display.set_icon(pygame.image.load(ICON_PATH))

    font = pygame.font.SysFont("Arial", 36, bold=True)

    video_rect = pygame.Rect(100, 180, 350, 225)
    video_rect.centerx = SCREEN_WIDTH // 2
    video_rect.top = 100

    video_poster_img = pygame.image.load(POSTER_PATH).convert()
    video_poster = pygame.transform.scale(video_poster_img, (video_rect.width, video_rect.height))
    last_frame_surface = video_poster.copy()

    button_rect = pygame.Rect(0, 0, 200, 80)
    button_rect.centerx = SCREEN_WIDTH // 2
    button_rect.top = video_rect.bottom + 20

    play_icon = load_icon("play.png")
    pause_icon = load_icon("pause.png")

    clock = pygame.time.Clock()
    running = True
    dragging_bar = False

    iniciar = False  # <- variable que devuelve si se presionó iniciar

    while running:
        screen.fill(DARK)

        pygame.draw.rect(screen, GRAY, video_rect, border_radius=8)
        pygame.draw.rect(screen, BLUE, video_rect, 2, border_radius=8)

        draw_video_frame(screen, video_rect)

        if video_playing:
            icon = pause_icon if not video_paused else play_icon
            pause_rect = pygame.Rect(video_rect.left + 10, video_rect.bottom - 50, 40, 40)
            screen.blit(icon, pause_rect.topleft)
        else:
            screen.blit(play_icon, (video_rect.centerx - 20, video_rect.centery - 20))

        progress_bar_rect = None
        if video_playing:
            progress_bar_rect, _ = draw_progress_bar(screen, video_rect)

        pygame.draw.rect(screen, BLUE, button_rect, border_radius=3)
        txt = font.render("Iniciar", True, WHITE)
        screen.blit(txt, (button_rect.centerx - txt.get_width() // 2,
                          button_rect.centery - txt.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if button_rect.collidepoint(mx, my):
                    iniciar = launch_main()
                    running = False  # Cierra el launcher

                if video_rect.collidepoint(mx, my):
                    if not video_playing:
                        play_video()
                    else:
                        video_paused = not video_paused

                if progress_bar_rect and progress_bar_rect.collidepoint(mx, my):
                    seek_video(mx, progress_bar_rect)
                    dragging_bar = True

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_bar = False

            elif event.type == pygame.MOUSEMOTION and dragging_bar:
                if progress_bar_rect:
                    seek_video(event.pos[0], progress_bar_rect)

        pygame.display.flip()
        clock.tick(30)

    stop_video()
    return iniciar  # Devuelve True si se presionó iniciar
