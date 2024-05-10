import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# Dictionary to store connected WebSocket clients and their usernames
connected_clients = {}

# HTML template for the client interface
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Collaborative Writing App</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div id="app" class="container">
        <h1>Collaborative Writing App</h1>
        <input type="text" v-model="username" placeholder="Enter your username" class="form-control mb-2">
        <textarea @input="sendText" v-model="text" rows="10" cols="50" class="form-control mb-2"></textarea>
        <button @click="connectWebSocket" class="btn btn-primary mb-2">Connect</button>
        <div v-if="connected" class="alert alert-success mb-2">Connected to WebSocket</div>
        <div v-else class="alert alert-danger mb-2">Not connected to WebSocket</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/vue@2"></script>
    <script>
        new Vue({
            el: '#app',
            data: {
                username: '',
                text: '',
                socket: null,
                connected: false
            },
            methods: {
                connectWebSocket() {
                    if (this.username.trim() === "") {
                        alert("Please enter a username");
                        return;
                    }

                    this.socket = new WebSocket(`ws://${window.location.host}/ws?username=${encodeURIComponent(this.username)}`);
                    this.socket.onmessage = this.handleMessage;
                    this.socket.onopen = this.handleOpen;
                    this.socket.onclose = this.handleClose;
                },
                sendText() {
                    // Send the current text to the server
                    if (this.socket && this.connected) {
                        this.socket.send(this.text);
                    }
                },
                handleMessage(event) {
    const [char, sender] = event.data.split('|');
    if (sender !== this.username) {
        console.log(char);
        // Update the text only if the sender is not the current user
        this.text = char;
    }
},


                handleOpen() {
                    this.connected = true;
                },
                handleClose() {
                    this.connected = false;
                }
            }
        });
    </script>
</body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(websocket)  # Use the WebSocket instance as the client ID

    # Get the username from the query string
    username = websocket.query_params.get("username", "Anonymous")

    # Add the connected client and its username to the dictionary
    connected_clients[client_id] = (websocket, username)

    try:
        while True:
            # Receive data from the client
            data = await websocket.receive_text()

            # Broadcast the received data and sender's username to all connected clients
            await broadcast(data, client_id, username)

    except WebSocketDisconnect:
        # Remove the disconnected client from the dictionary
        connected_clients.pop(client_id)


async def broadcast(char: str, sender_id: str, username: str):
    """Broadcast the character and sender's username to all connected clients."""
    message = f"{char}|{username}"
    for client_id, (websocket, _) in connected_clients.items():
        await websocket.send_text(message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8045)
