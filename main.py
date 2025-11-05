import pygame
import math
import sys
import cv2
import mediapipe as mp
import numpy as np

import os

import tkinter as tk
from tkinter import filedialog

from model_mophet import *

os.chdir(os.path.dirname(__file__))

pygame.init()

# pantalla
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rotación múltiple con pivotes internos + postura")

# colores
BG = (200, 200, 200)
WHITE = (255, 255, 255)

BLACK = (0, 0, 0)
GRAY = (180, 180, 180)

parte_activa = None


# Cuadro para arrastrar imagen
DROP_AREA = pygame.Rect(int(SCREEN_WIDTH*0.6)+20, 20, int(SCREEN_WIDTH*0.4)-40, SCREEN_HEIGHT//2 - 40)


# --------------------------
# cargar imágenes
# --------------------------
skin_folder = "skin01"

#turret_original = pygame.image.load("C:/Users/no name/Downloads/models/brazoDerecho1.png").convert_alpha()
turret_original = pygame.image.load(f"./models/{skin_folder}/brazoDerecho1.png").convert_alpha()
turret_original1 = pygame.image.load(f"./models/{skin_folder}/brazoDerecho2.png").convert_alpha()
turret_original2 = pygame.image.load(f"./models/{skin_folder}/brazoIzquierdo1.png").convert_alpha()
turret_original3 = pygame.image.load(f"./models/{skin_folder}/brazoIzquierdo2.png").convert_alpha()
turret_original4 = pygame.image.load(f"./models/{skin_folder}/piernaDerecha1.png").convert_alpha()
turret_original5 = pygame.image.load(f"./models/{skin_folder}/piernaDerecha2.png").convert_alpha()
turret_original6 = pygame.image.load(f"./models/{skin_folder}/piernaIzquierda1.png").convert_alpha()
turret_original7 = pygame.image.load(f"./models/{skin_folder}/piernaIzquierda2.png").convert_alpha()
torso_img = pygame.image.load(f"./models/{skin_folder}/faces/torzo00.png").convert_alpha()




# diccionario con todas las partes
partes = {
    "torso": {"imagen": torso_img, "pos": [250, 250], "offset": (0, 0),
              "rect": None, "modo": None, "angle": 90},

    "brazod1": {"imagen": turret_original, "pos": [195, 315], "offset": (-8, 25),
                "rect": None, "modo": None, "angle": 90, "punto_rel": (-18, 55)},
    "brazod2": {"imagen": turret_original1,"pos": [188, 385],"offset": (4, 48),
                "rect": None, "modo": None, "angle": 90,"punto_verde": (0, 70)},
    "brazoi1": {"imagen": turret_original2, "pos": [295, 315], "offset": (8, 25),
                "rect": None, "modo": None, "angle": 90, "punto_rel": (18, 55)},
    "brazoi2": {"imagen": turret_original3, "pos": [303, 385], "offset": (-5, 48),
                "rect": None, "modo": None, "angle": 90,"punto_verde": (0, 70)},

    "piernad1": {"imagen": turret_original4, "pos": [275, 445], "offset": (0, 25),
                 "rect": None, "modo": None, "angle": 90, "punto_rel": (0, 48)},
    "piernad2": {"imagen": turret_original5, "pos": [273, 493], "offset": (-5, 40),
                "rect": None, "modo": None, "angle": 90,"punto_verde": (0, 70)},

    "piernai1": {"imagen": turret_original6, "pos": [230, 445], "offset": (0, 25),
                 "rect": None, "modo": None, "angle": 90, "punto_rel": (0, 48)},
    "piernai2": {"imagen": turret_original7, "pos": [225, 493], "offset": (-5, 40),
                "rect": None, "modo": None, "angle": 90,"punto_verde": (0, 70)},
}


# --------------------------
# Guardar posiciones iniciales de todas las partes
# --------------------------
posiciones_iniciales = {}
for key, parte in partes.items():
    posiciones_iniciales[key] = {"pos": parte["pos"][:]}
    if "angle" in parte:
        posiciones_iniciales[key]["angle"] = parte["angle"]  # añadir angle sin sobrescribir
    if "punto_verde" in parte:
        posiciones_iniciales[key]["punto_verde"] = parte["punto_verde"]
    if "punto_rel" in parte:
        posiciones_iniciales[key]["punto_rel"] = parte["punto_rel"]




# --------------------------
# BOTONES (SIN CAMBIOS)
# --------------------------
# --------------------------
# BOTONES AJUSTADOS (Guardar + Texto + Tickbox)
# --------------------------
font = pygame.font.SysFont(None, 28)

def create_buttons(area_rect):
    buttons = []
    # Botón guardar: ocupa el ancho de dos botones
    btn_w = area_rect.width - 20
    btn_h = (area_rect.height // 3) - 20
    x = area_rect.x + 10
    y = area_rect.y + 10
    guardar_rect = pygame.Rect(x, y, btn_w, btn_h)
    buttons.append({"label": "Guardar", "rect": guardar_rect, "action": "guardar"})
    return buttons




# variables del tickbox
checkbox_options = ["Transparente", "Añadir fondo"]
checkbox_selected = 0  # 0 = transparente, 1 = añadir fondo

def draw_buttons(destino, buttons, mouse_pos):
    global checkbox_selected

    # --- Dibuja botón Guardar ---
    for btn in buttons:
        btn["rect"].y = 450
        color = (100, 170, 255) if btn["rect"].collidepoint(mouse_pos) else (180, 180, 180)
        pygame.draw.rect(destino, color, btn["rect"], border_radius=10)
        pygame.draw.rect(destino, BLACK, btn["rect"], 2, border_radius=10)
        text = font.render(btn["label"], True, BLACK)
        destino.blit(text, (btn["rect"].centerx - text.get_width()//2,
                            btn["rect"].centery - text.get_height()//2))

    # --- Texto "Fondos" debajo del botón ---
    fondos_y = buttons[0]["rect"].bottom -200
    fondos_text = font.render("Fondos", True, BLACK)
    destino.blit(fondos_text, (buttons[0]["rect"].x + 10, fondos_y))

    # --- Checkbox debajo del texto ---
    start_y = fondos_y + 35
    box_size = 20
    spacing = 40

    for i, option in enumerate(checkbox_options):
        box_rect = pygame.Rect(buttons[0]["rect"].x + 10, start_y + i * spacing, box_size, box_size)
        pygame.draw.rect(destino, BLACK, box_rect, 2, border_radius=4)
        if i == checkbox_selected:
            pygame.draw.line(destino, BLACK, (box_rect.x + 4, box_rect.centery),
                             (box_rect.x + box_rect.width - 4, box_rect.centery), 3)
        option_text = font.render(option, True, BLACK)
        destino.blit(option_text, (box_rect.right + 10, box_rect.y))


    # --- Detectar clic sobre el checkbox ---
    mouse_pressed = pygame.mouse.get_pressed()[0]
    if mouse_pressed:
        for i, option in enumerate(checkbox_options):
            box_rect = pygame.Rect(buttons[0]["rect"].x + 10, start_y + i * spacing, box_size, box_size)
            if box_rect.collidepoint(mouse_pos):
                checkbox_selected = i

                # Si elige "Añadir fondo", abrir ventana de selección
                if checkbox_selected == 1:
                    root = tk.Tk()
                    root.withdraw()  # Oculta la ventana principal de Tkinter
                    file_path = filedialog.askopenfilename(
                        title="Seleccionar imagen de fondo",
                        filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg")]
                    )
                    if file_path:
                        global imagen_fondo
                        imagen_fondo = pygame.image.load(file_path).convert()
                        # Escalar al tamaño del área blanca usando left_rect
                        imagen_fondo = pygame.transform.scale(imagen_fondo, (left_rect.width, left_rect.height))
                
                # Si elige "Transparente", borrar la imagen de fondo
                if checkbox_selected == 0:
                    imagen_fondo = None


# --------------------------
# DIBUJAR ESQUELETO MEDIA PIPE SOBRE IMAGEN
# --------------------------
pose_lines = [
    ("LEFT_SHOULDER", "RIGHT_SHOULDER"),
    ("LEFT_SHOULDER", "LEFT_ELBOW"), ("LEFT_ELBOW", "LEFT_WRIST"),
    ("RIGHT_SHOULDER", "RIGHT_ELBOW"), ("RIGHT_ELBOW", "RIGHT_WRIST"),
    ("LEFT_HIP", "RIGHT_HIP"),
    ("LEFT_SHOULDER", "LEFT_HIP"), ("RIGHT_SHOULDER", "RIGHT_HIP"),
    ("LEFT_HIP", "LEFT_KNEE"), ("LEFT_KNEE", "LEFT_ANKLE"),
    ("RIGHT_HIP", "RIGHT_KNEE"), ("RIGHT_KNEE", "RIGHT_ANKLE")
]

last_keypoints = None  # guardaremos la pose detectada para redibujar

def draw_pose_on_image(surface, keypoints, area):
    if not keypoints:
        return
    # Transformar coordenadas de keypoints (0-1) a área de imagen (DROP_AREA)
    def transform(pt):
        x = int(area.x + pt[0] * area.width)
        y = int(area.y + pt[1] * area.height)
        return (x, y)

    # Dibujar líneas
    for a, b in pose_lines:
        if a in keypoints and b in keypoints:
            p1, p2 = transform(keypoints[a]), transform(keypoints[b])
            pygame.draw.line(surface, (0, 255, 0), p1, p2, 2)

    # Dibujar puntos
    for name, pt in keypoints.items():
        x, y = transform(pt)
        pygame.draw.circle(surface, (255, 0, 0), (x, y), 4)





# --------------------------
# Bucle principal
# --------------------------
right_rect = pygame.Rect(int(SCREEN_WIDTH*0.6), 0, int(SCREEN_WIDTH*0.4), SCREEN_HEIGHT)
buttons_area = pygame.Rect(right_rect.x + 20, SCREEN_HEIGHT//2 + 10, right_rect.width - 40, SCREEN_HEIGHT//2 - 30)
buttons = create_buttons(buttons_area)

# --- Configuración del menú de skins (se carga una sola vez) ---

dir_default = r".\models\skin01\faces"

skins_dir = r".\models"
skins = []
skin_menu_visible = False
skin_thumbnail_size = (80, 80)




if os.path.isdir(skins_dir):
    for folder in sorted(os.listdir(skins_dir)):
        folder_path = os.path.join(skins_dir, folder)
        if os.path.isdir(folder_path) and folder.lower().startswith("skin"):
            skin_path = os.path.join(folder_path, "skin.png")
            if os.path.exists(skin_path):
                try:
                    img = pygame.image.load(skin_path).convert_alpha()
                    img = pygame.transform.scale(img, skin_thumbnail_size)
                    skins.append({"image": img, "path": skin_path})
                except Exception as e:
                    print("Error cargando", skin_path, e)


faces_dir = dir_default
faces = []
face_menu_visible = False
face_thumbnail_size = (80, 80)

# Cargar miniaturas de las faces dentro de la carpeta seleccionada
def carga_expresiones(faces_dir,faces,face_thumbnail_size):
    if os.path.isdir(faces_dir):
        for image_file in sorted(os.listdir(faces_dir)):
            image_path = os.path.join(faces_dir, image_file)
            if os.path.isfile(image_path) and image_file.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    img = pygame.image.load(image_path).convert_alpha()
                    w, h = img.get_size()
                    top_half = img.subsurface((0, 0, w, h // 2))
                    img = pygame.transform.scale(top_half, face_thumbnail_size)
                    faces.append({"image": img, "path": image_path})
                except Exception as e:
                    print("Error cargando face:", image_path, e)

carga_expresiones(faces_dir,faces,face_thumbnail_size)

face_thumbnails_rects = []
skin_thumbnails_rects = []  # rectángulos de cada miniatura
run = True
while run:
    screen.fill(BG)
    mouse_pos = pygame.mouse.get_pos()

    # ------------------------------
    # Fondo y área izquierda
    # ------------------------------
    left_rect = pygame.Rect(0, 0, int(SCREEN_WIDTH*0.6), SCREEN_HEIGHT)
    pygame.draw.rect(screen, WHITE, left_rect)

    # Dibujar imagen de fondo si existe
    if 'imagen_fondo' in globals() and imagen_fondo:
        # Escalar imagen al tamaño del área izquierda
        imagen_redimensionada = pygame.transform.scale(imagen_fondo, (left_rect.width, left_rect.height))
        screen.blit(imagen_redimensionada, left_rect.topleft)

    # ------------------------------
    # Botones cuadrados verticales
    # ------------------------------
    square_size = 50
    padding = 10
    top_right_x = left_rect.right - square_size - padding
    top_y = padding
    botones_cuadrados = [
        pygame.Rect(top_right_x, top_y + i*(square_size + padding), square_size, square_size)
        for i in range(3)
    ]

    for i, rect in enumerate(botones_cuadrados):
        pygame.draw.rect(screen, (150, 150, 255), rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        texto = font.render(f"B{i+1}", True, BLACK)
        screen.blit(texto, (rect.centerx - texto.get_width()//2, rect.centery - texto.get_height()//2))

    # ------------------------------
    # Otros elementos (cuerpo, derecha, drop area, botones)
    # ------------------------------
    dibujar_cuerpo(partes, parte_activa, screen, mouse_pos)

    pygame.draw.rect(screen, (230, 230, 230), right_rect)
    top_square = pygame.Rect(right_rect.x + 20, 20, right_rect.width - 40, right_rect.height//2 - 40)
    pygame.draw.rect(screen, WHITE, top_square)
    pygame.draw.rect(screen, BLACK, top_square, 2)

    pygame.draw.rect(screen, (180,180,180), DROP_AREA, border_radius=8)
    pygame.draw.rect(screen, (100,100,100), DROP_AREA, 3, border_radius=8)
    txt = font.render("Arrastra aquí una imagen", True, (50,50,50))
    screen.blit(txt, (DROP_AREA.x + 20, DROP_AREA.y + DROP_AREA.height//2 - 10))
    if image_preview:
        img_rect = image_preview.get_rect(center=DROP_AREA.center)
        screen.blit(image_preview, img_rect.topleft)
        draw_pose_on_image(screen, last_keypoints, DROP_AREA)

    draw_buttons(screen, buttons, mouse_pos)

   
        # ------------------------------
    # MENÚ DE SKINS: dibujar al final para que quede encima
    # ------------------------------
    if skin_menu_visible and skins:

        b2_rect = botones_cuadrados[1]
        start_x = b2_rect.x
        start_y = b2_rect.bottom + 10
        spacing = skin_thumbnail_size[0] + 10

        skin_thumbnails_rects.clear()  # limpiar cada frame

        for i, skin in enumerate(skins):
            x = start_x + i * spacing
            thumb_rect = pygame.Rect(x, start_y, *skin_thumbnail_size)
            pygame.draw.rect(screen, (220, 220, 220), thumb_rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, thumb_rect, 2, border_radius=6)
            screen.blit(skin["image"], thumb_rect.topleft)

            # Guardar rectángulo y skin para clic
            skin_thumbnails_rects.append((thumb_rect, skin))


     # ------------------------------
    # MENÚ DE SKINS: dibujar al final para que quede encima
    # ------------------------------



    if face_menu_visible and faces:
        b2_rect = botones_cuadrados[2]
        start_x = b2_rect.x
        start_y = b2_rect.bottom + 10
        spacing_x = face_thumbnail_size[0] + 10
        spacing_y = face_thumbnail_size[1] + 10
        max_per_row = 4  # máximo 4 miniaturas por fila

        face_thumbnails_rects.clear()  # limpiar rectángulos previos

        for i, face in enumerate(faces):
            # Calcular fila y columna
            row = i // max_per_row
            col = i % max_per_row

            x = start_x + col * spacing_x
            y = start_y + row * spacing_y

            thumb_rect = pygame.Rect(x, y, *face_thumbnail_size)

            # Dibujar fondo y borde
            pygame.draw.rect(screen, (220, 220, 220), thumb_rect, border_radius=6)
            pygame.draw.rect(screen, (0, 0, 0), thumb_rect, 2, border_radius=6)

            # Dibujar imagen
            screen.blit(face["image"], thumb_rect.topleft)

            # Guardar rectángulo y face
            face_thumbnails_rects.append((thumb_rect, face))




    # ------------------------------
    # Eventos
    # ------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.DROPFILE:
            file_path = event.file

            # -------------------------------
            # Rotar imagen y mapear pose
            # -------------------------------
            keypoints = detect_pose(file_path)
            if keypoints:


                map_pose_to_model(keypoints,partes,file_path,SCREEN_WIDTH, SCREEN_HEIGHT)
                
                last_keypoints = keypoints  # almacenar los puntos para redibujar el esqueleto


                # Cargar imagen y rotar 180° antes de mostrar
                img_cv2 = cv2.imread(file_path)
                #img_cv2 = cv2.rotate(img_cv2, cv2.ROTATE_180)  # <-- imagen volteada

                h, w, _ = img_cv2.shape
                scale_factor = min((DROP_AREA.width-10)/w, (DROP_AREA.height-10)/h)
                img_resized = cv2.resize(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB),
                                        (int(w*scale_factor), int(h*scale_factor)))
                image_preview = pygame.image.frombuffer(img_resized.tobytes(), img_resized.shape[:2][::-1], 'RGB')

            else:
                print("No se detectó ninguna postura en la imagen.")
                image_preview = None



        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # clic izquierdo
                # --- Restaurar posiciones si clic en B1 ---

                if botones_cuadrados[0].collidepoint(event.pos):
                    
                    for key, pos_dict in posiciones_iniciales.items():
                        partes[key]["pos"] = pos_dict["pos"][:]  # copiar la lista de posiciones inicial
                        
                        if "angle" in pos_dict:
                            partes[key]["angle"] = pos_dict["angle"]
                        
                        if "punto_verde" in pos_dict:
                            partes[key]["punto_verde"] = pos_dict["punto_verde"]
                            print("patata")
                        if "punto_rel" in pos_dict:
                            partes[key]["punto_rel"] = pos_dict["punto_rel"]
                            print("batata")
                    #coordenadas_verdes = coordenadas_verdes_guardado.copy()
                    print("Coordenadas restauradas a las iniciales")


                if botones_cuadrados[1].collidepoint(event.pos):
                    skin_menu_visible = not skin_menu_visible
                    if not skins:
                        skin_menu_visible = False
                
                if botones_cuadrados[2].collidepoint(event.pos):
                    face_menu_visible = not face_menu_visible
                    if not faces:
                        face_menu_visible = False


                if skin_menu_visible:
                    for thumb_rect, skin in skin_thumbnails_rects:
                        if thumb_rect.collidepoint(event.pos):
                            folder_name = os.path.basename(os.path.dirname(skin["path"]))
                            print("Miniatura clickeada:", folder_name)
                            print("Miniatura clickeada (ruta completa):", skin["path"])

                            skin_folder = folder_name  # actualizar la carpeta de skin

                            # Recargar imágenes de todas las partes desde la nueva carpeta
                            base_path = os.path.join(skins_dir, skin_folder)
                            partes["brazod1"]["imagen"] = pygame.image.load(os.path.join(base_path, "brazoDerecho1.png")).convert_alpha()
                            partes["brazod2"]["imagen"] = pygame.image.load(os.path.join(base_path, "brazoDerecho2.png")).convert_alpha()
                            partes["brazoi1"]["imagen"] = pygame.image.load(os.path.join(base_path, "brazoIzquierdo1.png")).convert_alpha()
                            partes["brazoi2"]["imagen"] = pygame.image.load(os.path.join(base_path, "brazoIzquierdo2.png")).convert_alpha()
                            partes["piernad1"]["imagen"] = pygame.image.load(os.path.join(base_path, "piernaDerecha1.png")).convert_alpha()
                            partes["piernad2"]["imagen"] = pygame.image.load(os.path.join(base_path, "piernaDerecha2.png")).convert_alpha()
                            partes["piernai1"]["imagen"] = pygame.image.load(os.path.join(base_path, "piernaIzquierda1.png")).convert_alpha()
                            partes["piernai2"]["imagen"] = pygame.image.load(os.path.join(base_path, "piernaIzquierda2.png")).convert_alpha()

                            partes["torso"]["imagen"] = pygame.image.load(os.path.join(base_path, r"faces\torzo00.png")).convert_alpha()
                            
                            dir_default = os.path.join(r".\models", skin_folder, "faces")
                            faces_dir = os.path.join(base_path, "faces")
                            faces.clear()

                            carga_expresiones(faces_dir,faces,face_thumbnail_size)

                            break


                if face_menu_visible:
                    for thumb_rect, face in face_thumbnails_rects:
                        if thumb_rect.collidepoint(event.pos):
                            folder_name = os.path.basename(os.path.dirname(face["path"]))
                            print("Miniatura clickeada:", folder_name)
                            print("Miniatura clickeada (ruta completa):", face["path"])

                            skin_folder = folder_name  # actualizar la carpeta actual del skin

                            # Cargar la face seleccionada como torso
                            base_path = os.path.join(skins_dir, skin_folder)
                            partes["torso"]["imagen"] = pygame.image.load(face["path"]).convert_alpha()

                            break







                # --- Botones laterales (guardar, etc.) ---


                for btn in buttons:
                    if btn["rect"].collidepoint(event.pos):
                        if btn["action"] == "guardar":
                            # --- Definir el área ---
                            left_rect = pygame.Rect(0, 0, int(SCREEN_WIDTH * 0.6), SCREEN_HEIGHT)

                            # --- Crear superficie según haya fondo ---
                            if 'imagen_fondo' in globals() and imagen_fondo:
                                # Si hay fondo, superficie normal
                                final_surface = pygame.Surface(left_rect.size)
                                # Redimensionar fondo al tamaño del área
                                fondo_redim = pygame.transform.scale(imagen_fondo, left_rect.size)
                                final_surface.blit(fondo_redim, (0, 0))
                            else:
                                # Si no hay fondo, superficie transparente
                                final_surface = pygame.Surface(left_rect.size, pygame.SRCALPHA)

                            # --- Dibujar el cuerpo encima ---
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            dibujar_cuerpo(partes, parte_activa,final_surface, (mouse_x - left_rect.x, mouse_y - left_rect.y))

                            # --- Guardar la imagen ---
                            pygame.image.save(final_surface, "cuerpo_guardado.png")

                            print("Imagen guardada como cuerpo_guardado.png")


                # --- Selección de parte para MOVER ---
                for key, parte in partes.items():
                    if parte["rect"] and parte["rect"].collidepoint(event.pos):
                        parte_activa = key
                        parte["modo"] = "mover"
                        offset_click = (event.pos[0] - parte["pos"][0], event.pos[1] - parte["pos"][1])
                        break

            # --- BOTÓN DERECHO -> ROTAR ---
            elif event.button == 3:
                for key, parte in partes.items():
                    if parte["rect"] and parte["rect"].collidepoint(event.pos): 
                        parte_activa = key
                        parte["modo"] = "rotar"
                        break


        elif event.type == pygame.MOUSEBUTTONUP:
            # Soltar cualquier modo
            if event.button in (1, 3) and parte_activa:
                partes[parte_activa]["modo"] = None
                parte_activa = None






    # --- ARRRASTRE (Mover con botón izquierdo) ---
    if parte_activa and partes[parte_activa]["modo"] == "mover":
        partes[parte_activa]["pos"][0] = mouse_pos[0] - offset_click[0]
        partes[parte_activa]["pos"][1] = mouse_pos[1] - offset_click[1]

    

    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
sys.exit()
