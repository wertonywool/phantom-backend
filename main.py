from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
app_sio = socketio.ASGIApp(sio, app)

@sio.on('sio_message')
async def handle_message(sid, data):
    await sio.emit('execute', data)

@sio.on('sio_response')
async def handle_response(sid, data):
    await sio.emit('web_display', data)

app.mount("/", app_sio)
