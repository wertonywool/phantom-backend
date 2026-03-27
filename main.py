import os
import google.generativeai as genai
from fastapi import FastAPI
import socketio

# Configuración de IA (Tu llave de Gemini)
genai.configure(api_key="AIzaSyBpHDh4EFJydoOTcTXv1-aNXU4yAOV0_gg")
model = genai.GenerativeModel('gemini-1.5-flash')

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
app_sio = socketio.ASGIApp(sio, app)

SYSTEM_PROMPT = """Eres el asistente de IA de 'The Workers', liderado por Josué. 
Habla con estilo de Persona 5 (misterioso, elegante y rebelde).
Si Josué te pide algo que requiera ejecutar un comando en su Kali Linux, responde 
ÚNICAMENTE con el comando entre etiquetas [CMD]comando[/CMD].
Si solo te saluda o charla, responde como su asistente personal."""

@sio.on('sio_message')
async def handle_message(sid, data):
    user_input = data.get('cmd')
    print(f"Mensaje recibido: {user_input}")
    
    # Lista de comandos directos para no pasar por la IA si no es necesario
    comandos_directos = ['ls', 'sudo', 'cd', 'python', 'cat', './', 'whoami', 'ifconfig']
    es_comando_manual = any(user_input.startswith(c) for c in comandos_directos)

    if es_comando_manual:
        await sio.emit('execute', {'cmd': user_input})
    else:
        # Aquí es donde la IA "piensa"
        try:
            response = model.generate_content(f"{SYSTEM_PROMPT}\nUsuario: {user_input}")
            bot_response = response.text
            
            # Si la IA decide ejecutar un comando
            if "[CMD]" in bot_response:
                cmd = bot_response.split("[CMD]")[1].split("[/CMD]")[0]
                await sio.emit('execute', {'cmd': cmd})
            
            await sio.emit('web_display', {'output': bot_response})
        except Exception as e:
            await sio.emit('web_display', {'output': f"Error en el Cerebro: {str(e)}"})

@sio.on('sio_response')
async def handle_response(sid, data):
    await sio.emit('web_display', data)

app.mount("/", app_sio)
