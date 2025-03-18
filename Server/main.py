# Importar librerias
import os
import cv2
import requests
import numpy as np
from flask import Flask, request, jsonify

# Configuración del bot de Telegram (Temporal)
TELEGRAM_BOT_TOKEN = 'TU_TOKEN_AQUI'
TELEGRAM_CHAT_ID = 'TU_CHAT_ID_AQUI'
MENSAJE_ALERTA = "¡Atención! Es hora de limpiar el arenero del gato."

# Función para enviar mensaje por Telegram
def enviar_alerta():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": MENSAJE_ALERTA}
    requests.post(url, data=payload)

# Función para detectar heces en la imagen
def detectar_heces(imagen_path):
    # Cargar imagen
    imagen = cv2.imread(imagen_path)

    # Aplicar filtro de suavizado
    suavizado = cv2.GaussianBlur(imagen, (15,15), 0)

    # Aplicar detección de bordes
    bordes = cv2.Canny(suavizado, 20, 40, L2gradient=True)

    # Aplicar operaciones morfologicas
    dilatado = cv2.dilate(bordes, None, iterations=3)
    erosi = cv2.erode(dilatado, None, iterations=3)

    #cv2.imshow('Bordes', erosi)

    countours, _ = cv2.findContours(erosi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # Dibujar los contornos detectados (opcional para depuración)
    cv2.drawContours(imagen, countours, -1, (0, 255, 0), 2)


    # Verificar si se detectaron 3 heces
    if len(countours) >= 3:
        print("🔔 ¡Tres heces detectadas! Enviando alerta...")
        enviar_alerta()
    else:
        print(f"✅ Número de heces detectadas: {len(countours)}")

# ----------------- PROGRAMA PRINCIPAL -----------------
app = Flask(__name__)
@app.route('/upload', methods=['POST'])
def upload():
    if 'imagen' not in request.files:
        return jsonify({"error": "No se encontró la imagen en la solicitud."}), 400

    imagen = request.files['imagen']
    ruta_imagen = os.path.join("images", "imagen_arenero.jpg")
    imagen.save(ruta_imagen)

    # Detectar heces en la imagen recibida
    detectar_heces(ruta_imagen)

    return jsonify({"mensaje": "Imagen recibida y procesada correctamente."})

if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
