import requests
import json
import os

VITE_PROXY_URL = "http://127.0.0.1:5173/api/v1"

def test_text_ingestion():
    print("\n==========================================")
    print("1. PROBANDO INGESTA DE TEXTO VÍA PROXY VITE")
    print("==========================================")
    url = f"{VITE_PROXY_URL}/reviews/text"
    payload = {
        "texto": "La Sopa Azteca estuvo deliciosa y muy caliente, pero el Ribeye a la Parrilla llegó frío y un poco salado.",
        "canal_origen": "FORMULARIO_WEB",
        "autor_nombre": "Frontend Test User (Texto)",
        "calificacion_general": 4
    }
    resp = requests.post(url, json=payload)
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    print(f"ID Reseña: {data['id']}")
    print(f"Autor: {data['autor_nombre']}")
    print(f"Tipo Input: {data['tipo_input']}")
    print(f"Canal: {data['canal_origen']}")
    print(f"Calificación: {data['calificacion_general']}/5")
    print(f"Total Sentimientos: {len(data['sentimientos'])}")
    for s in data['sentimientos']:
        print(f"  * Platillo: {s['platillo_nombre_referenciado']} | Polaridad: {s['polaridad']} | Score: {s['score_numerico']}")
        if s.get('justificacion'):
            print(f"    Justificación: {s['justificacion']}")
        for a in s['atributos']:
            print(f"      - Atributo [{a['categoria_atributo']}]: {a['valor_mencionado']} ({a['polaridad']})")
    return data

def test_audio_ingestion():
    print("\n==========================================")
    print("2. PROBANDO INGESTA DE AUDIO .WEBM VÍA PROXY VITE")
    print("==========================================")
    url = f"{VITE_PROXY_URL}/reviews/upload-audio"
    
    # Usar el audio real .webm que probamos previamente
    audio_path = "backend/storage/audios/test_speech.webm"
    if not os.path.exists(audio_path):
        print(f"Archivo {audio_path} no encontrado.")
        return None
        
    with open(audio_path, "rb") as f:
        files = {"file": ("grabacion_navegador.webm", f, "audio/webm")}
        data = {
            "canal_origen": "AUDIO_IN_SITU",
            "autor_nombre": "Frontend Browser User (.webm)",
            "calificacion_general": 3
        }
        resp = requests.post(url, files=files, data=data)
        
    print(f"Status Code: {resp.status_code}")
    result = resp.json()
    print(f"ID Reseña: {result['id']}")
    print(f"Autor: {result['autor_nombre']}")
    print(f"Tipo Input: {result['tipo_input']}")
    print(f"Canal: {result['canal_origen']}")
    
    trans = result.get('transcripcion')
    if trans:
        print(f"Transcripción Faster-Whisper: \"{trans['texto_transcrito']}\"")
        print(f"Duración: {trans['duracion_segundos']}s")
        print(f"Confianza: {trans['confianza']:.4f}")
        print(f"Estado Procesamiento: {trans['estado_procesamiento']}")
        
    print(f"Total Sentimientos: {len(result['sentimientos'])}")
    for s in result['sentimientos']:
        print(f"  * Platillo: {s['platillo_nombre_referenciado']} | Polaridad: {s['polaridad']} | Score: {s['score_numerico']}")
        for a in s['atributos']:
            print(f"      - Atributo [{a['categoria_atributo']}]: {a['valor_mencionado']} ({a['polaridad']})")
    return result

def test_audio_failure_handling():
    print("\n==========================================")
    print("3. PROBANDO MANEJO DE ERROR / FALLIDO (SILENCIO)")
    print("==========================================")
    url = f"{VITE_PROXY_URL}/reviews/upload-audio"
    
    silence_path = "backend/test_silence.wav"
    if not os.path.exists(silence_path):
        # Crear un archivo wav con silencio breve para probar el fallo de STT
        import wave
        with wave.open(silence_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b"\x00" * 32000) # 1 segundo de silencio
            
    with open(silence_path, "rb") as f:
        files = {"file": ("silencio.wav", f, "audio/wav")}
        data = {
            "canal_origen": "AUDIO_IN_SITU",
            "autor_nombre": "Usuario Silencio",
        }
        resp = requests.post(url, files=files, data=data)
        
    print(f"Status Code esperada (Error STT): {resp.status_code}")
    print(f"Respuesta JSON del backend: {resp.text}")

if __name__ == "__main__":
    test_text_ingestion()
    test_audio_ingestion()
    test_audio_failure_handling()
