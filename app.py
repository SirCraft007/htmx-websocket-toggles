from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

app = FastAPI()

# Global variable to store LED state
led_state = False

led_state1 = False


# Class to manage WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "led_state": led_state}
    )


@app.get("/toggle/{state}")
async def toggle(state: bool):
    global led_state1
    led_state1 = state
    button = f'<button hx-get="/toggle/{not state}" hx-swap="outerHTML">Turn LED {"OFF" if state else "ON"} </button>'
    print(button)
    return HTMLResponse(content=button)


@app.websocket("/toggle")
async def toggle_button(websocket: WebSocket):
    await manager.connect(websocket)
    global led_state1
    await websocket.send_text(
        f'<button id="toggle-btn" name="{"off" if led_state1 else "on"}" hx-swap="outerHTML " hx-ws="send:submit">Turn LED {"OFF" if led_state1 else "ON"} </button>'
    )
    try:
        while True:
            data = await websocket.receive_json()
            data = data["HEADERS"]
            if "HX-Trigger-Name" in data:
                if data["HX-Trigger-Name"] == "off":
                    led_state1 = False
                    # Here you would typically control the actual LED
                    # For example: GPIO.output(LED_PIN, led_state)
                    response = '<button id="toggle-btn" name="on" hx-swap="outerHTML " hx-ws="send:submit">Turn LED ON </button>'
                    await manager.broadcast(response)
                elif data["HX-Trigger-Name"] == "on":
                    led_state1 = True
                    # Here you would typically control the actual LED
                    # For example: GPIO.output(LED_PIN, led_state)
                    response = '<button id="toggle-btn" name="off" hx-swap="outerHTML " hx-ws="send:submit">Turn LED OFF </button>'
                    await manager.broadcast(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws")
async def toggle_checkbox(websocket: WebSocket):
    await manager.connect(websocket)
    global led_state
    await websocket.send_text(
        f'<input id="toggle-cbox" name="toggle" type="checkbox" hx-ws="send:submit" hx-swap="outerHTML" {"checked" if led_state else ""}/>'
    )
    try:
        while True:
            data = await websocket.receive_json()
            if "toggle" in data:
                led_state = True
                # Here you would typically control the actual LED
                # For example: GPIO.output(LED_PIN, led_state)
                response = '<input id="toggle-cbox" name="toggle" type="checkbox" hx-ws="send:submit" hx-swap="outerHTML" checked />'
                await manager.broadcast(response)
            else:
                led_state = False
                # Here you would typically control the actual LED
                # For example: GPIO.output(LED_PIN, led_state)
                response = '<input id="toggle-cbox" name="toggle" type="checkbox" hx-ws="send:submit" hx-swap="outerHTML"/>'
                await manager.broadcast(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
