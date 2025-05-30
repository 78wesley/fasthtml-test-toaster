from fasthtml.common import *
from collections import deque


picocss = "https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css"
picolink = (Link(rel="stylesheet", href=picocss), Style(":root { --pico-font-size: 100%; }"))

app = FastHTML(exts="ws", hdrs=picolink)
setup_toasts(app, duration=5000)


messages = deque(maxlen=5)
users = {}


def render_messages(messages):
    messages = [m for m in messages if m]  # Remove empty messages
    box_style = "border: 1px solid #ccc; border-radius: 10px; padding: 10px; margin: 5px 0;"
    return Div(*[Div(m, style=box_style) for m in messages], id="msg-list")


def mk_input():
    return Input(id="msg", placeholder="Type your message here...")


@app.route("/toast")
def test_toast(sess):
    add_toast(sess, "This is a toast message from a button click.", "info", dismiss=True)
    add_toast(sess, "This is a toast message from a button click.", "success", dismiss=True)
    add_toast(sess, "This is a toast message from a button click.", "warning", dismiss=True)
    add_toast(sess, "This is a toast message from a button click.", "error", dismiss=True)
    print(sess)


@app.route("/")
def index(sess):
    add_toast(sess, "This is a toast message on page load.", typ="info", dismiss=True)
    return (
        Div(
            Button("Send Toast", hx_get="/toast", hx_swap="none"),
            P(),
            Form(mk_input(), ws_send=True),  # reset input field
            H5("Messages:"),
            Div(render_messages(messages), id="msg-list"),
            hx_ext="ws",
            ws_connect="ws",
        ),
    )


def on_connect(ws, send):
    users[id(ws)] = send


def on_disconnect(ws):
    users.pop(id(ws), None)


@app.ws("/ws", conn=on_connect, disconn=on_disconnect)
async def ws(msg: str, send, sess):
    if not msg:
        return
    await send(mk_input())  # reset the input field immediately
    await send(add_toast(sess, f"This is a toast message from a websocket. Msg: {msg}", typ="info"))
    await send(render_toasts(sess))
    messages.appendleft(msg)  # New messages first
    for user in users.values():  # Get `send` function for a user
        await user(render_messages(messages))  # Send the message to that user


serve()
