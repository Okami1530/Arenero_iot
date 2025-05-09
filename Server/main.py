import cv2
import os
from flask import Flask, jsonify, request
from twilio.rest import Client
import time

# Configuración de Twilio
account_sid = '*'
auth_token = '*'
client = Client(account_sid, auth_token)

# Función para enviar mensaje por WhatsApp
def enviar_alerta():
    message = client.messages.create(
        from_='whatsapp:*',
        body='Arenero Sucio!, favor de limpiarlo',
        to='whatsapp:*'
    )
    print(message.sid)

# Función para detectar heces en la imagen
def detectar_heces(imagen_path):
    # Cargar imagen
    imagen = cv2.imread(imagen_path)
    if imagen is None:
        print(f"❌ Error: no se pudo cargar la imagen en {imagen_path}")
        return
    
    #Convertir imagen a escala de grices
    grayscale = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Aplicar filtro de suavizado
    suavizado = cv2.GaussianBlur(grayscale, (7,7), 0)

    # Aplicar detección de bordes
    bordes = cv2.Canny(suavizado, 100, 200)

    # Aplicar operaciones morfologicas
    dilatado = cv2.dilate(bordes, None, iterations=3)
    erosi = cv2.erode(dilatado, (5,5), iterations=3)

    countours, _ = cv2.findContours(erosi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Dibujar los contornos detectados (opcional para depuración)
    cv2.drawContours(imagen, countours, -1, (0, 255, 0), 2)

    # Mostrar la imagen (opcional para depuración)
    cv2.imshow('Detección de Heces', imagen)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()

    # Verificar si se detectaron 3 heces
    if len(countours) >= 3:
        print("🔔 ¡Tres heces detectadas! Enviando alerta...")
        print(f"✅ Número de heces detectadas: {len(countours)}")
        enviar_alerta()
    else:
        print(f"✅ Número de heces detectadas: {len(countours)}")

# ----------------- PROGRAMA PRINCIPAL -----------------
app = Flask(__name__)
@app.route("/upload", methods=["POST"])    
def upload():
    if 'file' not in request.files and request.data == b'':
        return "No se encontró el archivo", 400

    # Si se envió como archivo (form-data)
    if 'file' in request.files:
        file = request.files['file']
        file.save(f"images/{file.filename}")
        detectar_heces(f"images/{file.filename}")
        return "Imagen recibida correctamente", 200

    # Si se envió como datos binarios (raw data)
    with open("images/imagen_recibida.jpg", "wb") as f:
        f.write(request.data)
        time.sleep(1)
    return "Imagen recibida correctamente", 200

@app.route("/detectar", methods=["GET"])
def detectar():
    detectar_heces("images/imagen_recibida.jpg")
    return "Imagen detectada correctamente", 200

if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
