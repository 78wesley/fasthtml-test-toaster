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
    add_toast(sess, "This is a toast message from a HTMX button click.", "info", dismiss=True)
    add_toast(sess, "This is a toast message from a HTMX button click.", "success", dismiss=True)
    add_toast(sess, "This is a toast message from a HTMX button click.", "warning", dismiss=True)
    add_toast(sess, "This is a toast message from a HTMX button click.", "error", dismiss=True)
    print(sess)


@app.route("/")
def index(req: Request, sess):
    ws_not_possible = "Websockets doesnt work ❌" if "fasthtml-test-toaster.vercel.app" in req.headers.get(":authority", "") else "Websockets ✅"
    add_toast(sess, "This is a toast message on page load.", typ="info", dismiss=True)
    return (
        Div(
            Button("Send Toast", hx_get="/toast", hx_swap="none"),
            A("Go to Second Page", href="/second", type="button"),
            A("Redirect", href="/redirect", type="button"),
            A("RedirectResponse", href="/redirectresponse", type="button"),
            P(ws_not_possible),
            Form(mk_input(), ws_send=True),  # reset input field
            H5("Messages:"),
            Div(render_messages(messages), id="msg-list"),
            hx_ext="ws",
            ws_connect="ws",
        ),
    )


@app.route("/second")
def page_second(sess):
    add_toast(sess, "Welcome to the second page!", typ="info", dismiss=True)
    return Div(
        H1("Second Page"),
        P("This is the second page."),
        P('When this page got loaded you should see the toast message "Welcome to the second page!".'),
        P('When you got Redirect to this page you should see the toast message "Toast from Redirect("/second")".'),
        P('When you got RedirectResponse to this page you should see the toast message "Toast from RedirectResponse("/second")".'),
        A("Go back to Home", href="/"),
    )


@app.route("/redirect")
def redirect(sess):
    add_toast(sess, 'Toast from Redirect("/second")', typ="warning", dismiss=True)
    return Redirect("/second")


@app.route("/redirectresponse")
def redirectresponse(sess):
    add_toast(sess, 'Toast from RedirectResponse("/second")', typ="warning", dismiss=True)
    return RedirectResponse("/second")


def on_connect(ws, send):
    users[id(ws)] = send


def on_disconnect(ws):
    users.pop(id(ws), None)


@app.ws("/ws", conn=on_connect, disconn=on_disconnect)
async def ws(msg: str, send, sess):
    if not msg:
        return
    await send(mk_input())  # reset the input field immediately
    await send(add_toast(sess, f"This is a toast message from a websocket. Msg: {msg}", typ="info", dismiss=True))
    await send(render_toasts(sess))
    messages.appendleft(msg)  # New messages first
    for user in users.values():  # Get `send` function for a user
        await user(render_messages(messages))  # Send the message to that user


serve()
