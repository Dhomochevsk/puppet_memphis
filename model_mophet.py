import mediapipe as mp
import pygame
import cv2
import math


GREEN = (0, 255, 0)
# --------------------------
# MEDIA PIPE
# --------------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)






offset_click = (0, 0)
coordenadas_verdes = []


image_preview = None

# función para dibujar una imagen con pivote interno
def cargar_imagen(x_pivot, y_pivot, x_pic, y_pic, imagen, angle, destino):
    pivot = pygame.math.Vector2(x_pivot, y_pivot)
    offset = pygame.math.Vector2(x_pic, y_pic)

    rotated_image = pygame.transform.rotate(imagen, angle - 90)
    rotated_offset = offset.rotate(-(angle - 90))
    rect = rotated_image.get_rect(center=(pivot + rotated_offset))
    destino.blit(rotated_image, rect)

    return rotated_image, rect


def detect_pose(image_path):
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)
    if not results.pose_landmarks:
        return None
    
    lm = results.pose_landmarks.landmark
    keypoints = {
        "LEFT_SHOULDER": (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                          lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y),
        "RIGHT_SHOULDER": (lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                           lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y),
        "LEFT_ELBOW": (lm[mp_pose.PoseLandmark.LEFT_ELBOW].x,
                       lm[mp_pose.PoseLandmark.LEFT_ELBOW].y),
        "RIGHT_ELBOW": (lm[mp_pose.PoseLandmark.RIGHT_ELBOW].x,
                        lm[mp_pose.PoseLandmark.RIGHT_ELBOW].y),
        "LEFT_WRIST": (lm[mp_pose.PoseLandmark.LEFT_WRIST].x,
                       lm[mp_pose.PoseLandmark.LEFT_WRIST].y),
        "RIGHT_WRIST": (lm[mp_pose.PoseLandmark.RIGHT_WRIST].x,
                        lm[mp_pose.PoseLandmark.RIGHT_WRIST].y),
        "LEFT_HIP": (lm[mp_pose.PoseLandmark.LEFT_HIP].x,
                     lm[mp_pose.PoseLandmark.LEFT_HIP].y),
        "RIGHT_HIP": (lm[mp_pose.PoseLandmark.RIGHT_HIP].x,
                      lm[mp_pose.PoseLandmark.RIGHT_HIP].y),
        "LEFT_KNEE": (lm[mp_pose.PoseLandmark.LEFT_KNEE].x,
                      lm[mp_pose.PoseLandmark.LEFT_KNEE].y),
        "RIGHT_KNEE": (lm[mp_pose.PoseLandmark.RIGHT_KNEE].x,
                       lm[mp_pose.PoseLandmark.RIGHT_KNEE].y),
        "LEFT_ANKLE": (lm[mp_pose.PoseLandmark.LEFT_ANKLE].x,
                       lm[mp_pose.PoseLandmark.LEFT_ANKLE].y),
        "RIGHT_ANKLE": (lm[mp_pose.PoseLandmark.RIGHT_ANKLE].x,
                        lm[mp_pose.PoseLandmark.RIGHT_ANKLE].y),
    }
    return keypoints


# --------------------------
# FUNCIONES NUEVAS PARA MEDIA PIPE
# --------------------------
def map_pose_to_model(keypoints,partes,file_path,SCREEN_WIDTH, SCREEN_HEIGHT):
    if not keypoints:
        return


    # Escalar y ajustar coordenadas

    def scale(pt):
        base_w, base_h = SCREEN_WIDTH - 300, SCREEN_HEIGHT
        x = int(pt[0]*base_w*0.9 + 40)
        y = int(pt[1]*base_h*0.9 + 40)  # NO invertir Y
        return x, y


    # Detecta keypoints
    keypoints = detect_pose(file_path)

    if keypoints:
        # Intercambio de izquierda/derecha
        left_shoulder = scale(keypoints["RIGHT_SHOULDER"])
        right_shoulder = scale(keypoints["LEFT_SHOULDER"])
        left_elbow = scale(keypoints["RIGHT_ELBOW"])
        right_elbow = scale(keypoints["LEFT_ELBOW"])
        left_wrist = scale(keypoints["RIGHT_WRIST"])
        right_wrist = scale(keypoints["LEFT_WRIST"])
        left_hip = scale(keypoints["RIGHT_HIP"])
        right_hip = scale(keypoints["LEFT_HIP"])
        left_knee = scale(keypoints["RIGHT_KNEE"])
        right_knee = scale(keypoints["LEFT_KNEE"])
        left_ankle = scale(keypoints["RIGHT_ANKLE"])
        right_ankle = scale(keypoints["LEFT_ANKLE"])

        # Ahora asignas al modelo normalmente:

        partes["brazod1"]["pos"] = list(left_shoulder)
        partes["brazod2"]["pos"] = list(left_elbow)
        partes["brazod2"]["punto_verde"] = (left_wrist[0]-left_elbow[0], left_wrist[1]-left_elbow[1])

        partes["brazoi1"]["pos"] = list(right_shoulder)
        partes["brazoi2"]["pos"] = list(right_elbow)
        partes["brazoi2"]["punto_verde"] = (right_wrist[0]-right_elbow[0], right_wrist[1]-right_elbow[1])

        partes["piernad1"]["pos"] = list(left_hip)
        partes["piernad2"]["pos"] = list(left_knee)
        partes["piernad2"]["punto_verde"] = (left_ankle[0]-left_knee[0], left_ankle[1]-left_knee[1])

        partes["piernai1"]["pos"] = list(right_hip)
        partes["piernai2"]["pos"] = list(right_knee)
        partes["piernai2"]["punto_verde"] = (right_ankle[0]-right_knee[0], right_ankle[1]-right_knee[1])



    # ---- POSICIONES TORSO ----
    left_shoulder = scale(keypoints["LEFT_SHOULDER"])
    right_shoulder = scale(keypoints["RIGHT_SHOULDER"])
    left_hip = scale(keypoints["LEFT_HIP"])
    right_hip = scale(keypoints["RIGHT_HIP"])

    partes["torso"]["pos"] = [(left_shoulder[0]+right_shoulder[0]+left_hip[0]+right_hip[0])//4,
                              (left_shoulder[1]+right_shoulder[1]+left_hip[1]+right_hip[1])//4]

    # Ángulo torso: hombro izquierdo → hombro derecho
    # -------------------------------
    # Ajuste del ángulo del torso
    # -------------------------------
    dx = right_shoulder[0] - left_shoulder[0]
    dy = right_shoulder[1] - left_shoulder[1]
    #partes["torso"]["angle"] = math.degrees(math.atan2(dy, dx)) -90 # <-- corregido
    partes["torso"]["angle"] = math.degrees(math.atan2(dy, dx))*0.9 # <-- corregido
    


    # ---- EXTREMIDADES ----
    # Brazos 1
    partes["brazod1"]["pos"] = list(right_shoulder)
    partes["brazoi1"]["pos"] = list(left_shoulder)
    # Brazos 2
    partes["brazod2"]["pos"] = list(scale(keypoints["RIGHT_ELBOW"]))
    partes["brazoi2"]["pos"] = list(scale(keypoints["LEFT_ELBOW"]))
    # Brazos 2 pivote verde (muñeca)
    partes["brazod2"]["punto_verde"] = (scale(keypoints["RIGHT_WRIST"])[0]-partes["brazod2"]["pos"][0],
                                        scale(keypoints["RIGHT_WRIST"])[1]-partes["brazod2"]["pos"][1])
    partes["brazoi2"]["punto_verde"] = (scale(keypoints["LEFT_WRIST"])[0]-partes["brazoi2"]["pos"][0],
                                        scale(keypoints["LEFT_WRIST"])[1]-partes["brazoi2"]["pos"][1])

    # Piernas 1
    partes["piernad1"]["pos"] = list(right_hip)
    partes["piernai1"]["pos"] = list(left_hip)
    # Piernas 2
    partes["piernad2"]["pos"] = list(scale(keypoints["RIGHT_KNEE"]))
    partes["piernai2"]["pos"] = list(scale(keypoints["LEFT_KNEE"]))
    # Piernas 2 pivote verde (tobillo)
    partes["piernad2"]["punto_verde"] = (scale(keypoints["RIGHT_ANKLE"])[0]-partes["piernad2"]["pos"][0],
                                        scale(keypoints["RIGHT_ANKLE"])[1]-partes["piernad2"]["pos"][1])
    partes["piernai2"]["punto_verde"] = (scale(keypoints["LEFT_ANKLE"])[0]-partes["piernai2"]["pos"][0],
                                        scale(keypoints["LEFT_ANKLE"])[1]-partes["piernai2"]["pos"][1])

    # ---- CALCULO ÁNGULOS DE TODAS LAS PARTES ----
    def calc_angle(p_start, p_end):
        dx = p_end[0] - p_start[0]
        dy = p_end[1] - p_start[1]
        return math.degrees(math.atan2(-dy, dx))

    for parte_name in ["brazod1","brazod2","brazoi1","brazoi2",
                       "piernad1","piernad2","piernai1","piernai2"]:
        parte = partes[parte_name]
        if "punto_verde" in parte:
            end = [parte["pos"][0]+parte["punto_verde"][0],
                   parte["pos"][1]+parte["punto_verde"][1]]
        else:
            # conectar a la parte 2 correspondiente
            mapping = {"brazod1":"brazod2","brazoi1":"brazoi2","piernad1":"piernad2","piernai1":"piernai2"}
            end = partes[mapping.get(parte_name,parte_name)]["pos"] if parte_name in mapping else parte["pos"]
        parte["angle"] = calc_angle(parte["pos"], end)


    partes["brazod1"]["angle"] = calc_angle(partes["brazod1"]["pos"], partes["brazod2"]["pos"])+180
    partes["brazod2"]["angle"] = calc_angle(partes["brazod2"]["pos"],
                                           [partes["brazod2"]["pos"][0]+partes["brazod2"]["punto_verde"][0],
                                            partes["brazod2"]["pos"][1]+partes["brazod2"]["punto_verde"][1]])+180
    partes["brazoi1"]["angle"] = calc_angle(partes["brazoi1"]["pos"], partes["brazoi2"]["pos"])+180
    partes["brazoi2"]["angle"] = calc_angle(partes["brazoi2"]["pos"],
                                           [partes["brazoi2"]["pos"][0]+partes["brazoi2"]["punto_verde"][0],
                                            partes["brazoi2"]["pos"][1]+partes["brazoi2"]["punto_verde"][1]])+180
    partes["piernad1"]["angle"] = calc_angle(partes["piernad1"]["pos"], partes["piernad2"]["pos"])+180
    partes["piernad2"]["angle"] = calc_angle(partes["piernad2"]["pos"],
                                            [partes["piernad2"]["pos"][0]+partes["piernad2"]["punto_verde"][0],
                                             partes["piernad2"]["pos"][1]+partes["piernad2"]["punto_verde"][1]])+180
    partes["piernai1"]["angle"] = calc_angle(partes["piernai1"]["pos"], partes["piernai2"]["pos"])+180
    partes["piernai2"]["angle"] = calc_angle(partes["piernai2"]["pos"],
                                            [partes["piernai2"]["pos"][0]+partes["piernai2"]["punto_verde"][0],
                                             partes["piernai2"]["pos"][1]+partes["piernai2"]["punto_verde"][1]])+180


# --------------------------
# FUNCIÓN dibujar_cuerpo (SIN CAMBIOS)
# --------------------------
coordenadas_verdes_guardado = []


def dibujar_cuerpo(partes, parte_activa, destino, mouse_pos):
    """Dibuja torso y todas las partes en la surface de destino, incluyendo pivotes y manejo de rotación"""
    coordenadas_verdes.clear()
    torso = partes["torso"]

    # Rotar torso si está activo
    if parte_activa == "torso" and torso["modo"] == "rotar":
        rel_x = mouse_pos[0] - torso["pos"][0]
        rel_y = mouse_pos[1] - torso["pos"][1]
        torso["angle"] = math.degrees(math.atan2(-rel_y, rel_x))

    # Dibujar torso
    imagen_rotada, rect = cargar_imagen(
        torso["pos"][0],
        torso["pos"][1],
        torso["offset"][0],
        torso["offset"][1],
        torso["imagen"],
        torso["angle"],
        destino
    )
    torso["rect"] = rect

    # Puntos verdes del torso (pivotes para brazos y piernas)
    torso_w, torso_h = torso["imagen"].get_size()
    pivot_x, pivot_y = torso["pos"]
    esquinas = [
        pygame.math.Vector2(-35, -11),
        pygame.math.Vector2(30, -11),
        pygame.math.Vector2(20, torso_h/2),
        pygame.math.Vector2(-20, torso_h/2),
    ]
    for esquina in esquinas:
        rotada = esquina.rotate(-(torso["angle"] - 90))
        ex, ey = pivot_x + rotada.x, pivot_y + rotada.y
        pygame.draw.circle(destino, (0, 255, 0), (int(ex), int(ey)), 5)
        coordenadas_verdes.append((ex, ey))

    # Actualizar posiciones iniciales de brazos y piernas 1
    if len(coordenadas_verdes) >= 4:
        partes["brazod1"]["pos"] = list(coordenadas_verdes[0])
        partes["brazoi1"]["pos"] = list(coordenadas_verdes[1])
        partes["piernai1"]["pos"] = list(coordenadas_verdes[2])
        partes["piernad1"]["pos"] = list(coordenadas_verdes[3])

    # Conectar las partes 2 a las 1 mediante sus puntos relativos
    conexiones = {"brazod2":"brazod1","brazoi2":"brazoi1","piernad2":"piernad1","piernai2":"piernai1"}
    for key2, parte2 in partes.items():
        if key2 in conexiones:
            parte1 = partes[conexiones[key2]]
            if "punto_rel" in parte1:
                rel = pygame.math.Vector2(parte1["punto_rel"])
                rel_rot = rel.rotate(-(parte1["angle"] - 90))
                px, py = parte1["pos"][0] + rel_rot.x, parte1["pos"][1] + rel_rot.y
                parte2["pos"] = [px, py]

    # Dibujar todas las partes restantes
    for key, parte in partes.items():
        if key == "torso":
            continue

        # Rotación de parte activa
        if parte["modo"] == "rotar" and parte_activa == key:
            rel_x = mouse_pos[0] - parte["pos"][0]
            rel_y = mouse_pos[1] - parte["pos"][1]
            parte["angle"] = math.degrees(math.atan2(-rel_y, rel_x))

        # Dibujar imagen de la parte
        imagen_rotada, rect = cargar_imagen(
            parte["pos"][0],
            parte["pos"][1],
            parte["offset"][0],
            parte["offset"][1],
            parte["imagen"],
            parte["angle"],
            destino
        )
        parte["rect"] = rect

        # Dibujar pivotes y puntos relativos
        bx, by = parte["pos"]
        if key.startswith(("brazod","brazoi","pierna","piernai")):
            pygame.draw.circle(destino, (0, 0, 255), (int(bx), int(by)), 5)
            if "punto_rel" in parte:
                rel = pygame.math.Vector2(parte["punto_rel"])
                rel_rot = rel.rotate(-(parte["angle"] - 90))
                px, py = bx + rel_rot.x, by + rel_rot.y
                pygame.draw.circle(destino, (255, 0, 0), (int(px), int(py)), 5)

        if key.endswith("2") and "punto_verde" in parte:
            rel = pygame.math.Vector2(parte["punto_verde"])
            rel_rot = rel.rotate(-(parte["angle"] - 90))
            vx, vy = parte["pos"][0] + rel_rot.x, parte["pos"][1] + rel_rot.y
            pygame.draw.circle(destino, (0, 255, 0), (int(vx), int(vy)), 5)

        # Resaltar parte activa
        if parte_activa == key:
            pygame.draw.rect(destino, (255, 0, 0), rect, 3)

