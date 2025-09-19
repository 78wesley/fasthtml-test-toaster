from fasthtml.common import *
from collections import deque
from fasthtml import __version__ as fasthtml__version
from fastlite import __version__ as fastlite_version
from fastcore import __version__ as fastcore_version
from urllib.parse import urlencode

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



def GenButton(hx_get="", cls="", title="Generic Button"):
    id=title.lower().replace(" ", "-")
    return A(title, cls=cls, hx_get=hx_get, type="button", id=id, hx_swap="outerHTML", hx_target=f"#{id}", hx_trigger="click")

def FtResponseButton(hx_get="", cls=""):
    return GenButton(hx_get=hx_get, cls=cls, title="Ft Response Button")

def Ftbutton(hx_get="", cls=""):
    return GenButton(hx_get=hx_get, cls=cls, title="Ft Button")

def TupleButton(hx_get="", cls=""):
    return GenButton(hx_get=hx_get, cls=cls, title="Tuple Button")

@app.route("/")
def index(req, sess):
    add_toast(sess, "This is a toast message on page load.", typ="info", dismiss=True)
    return (
        Div(
            H1("Welcome to the FastHTML Toaster Test!"),
            H5("Toast messages should be floating at the top of the page!!"),

            Div(
                B("Versions", style="margin:0;"),
                P("fasthtml: " + fasthtml__version, style="margin:0;"),
                P("fastlite: " + fastlite_version, style="margin:0;"),
                P("fastcore: " + fastcore_version, style="margin:0;"),
                style="margin-bottom: 1rem;"
            ),
            P("Websockets supported? " + ("❌" if req.get("scheme", "") == "https" else "✅"), style="margin:0;"),
            A("Source code (Github)", href="https://github.com/78wesley/fasthtml-test-toaster", target="_blank"),
            Hr(),
            P("Display all the toasts:"),
            A("Display Toast", hx_get="/toast", hx_swap="none", type="button"),
            P("These buttons should trigger toast messages on the new page:"),
            Div(
                A("Go to Second Page", href="/second", type="button"),
                A("Redirect", href="/redirect", type="button"),
                A("RedirectResponse", href="/redirectresponse", type="button"),
                cls="grid",
            ),
            P("If these buttons disapear then there is something wrong with the toasts:"),
            Div(
                Ftbutton(hx_get="/ftbutton", cls="primary"),
                FtResponseButton(hx_get="/ftresponsebutton", cls="primary"),
                TupleButton(hx_get="/tuplebutton"),
                cls="grid",
            ),
            P("Send a message to all connected clients (including yourself):"),
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
        Hgroup(
            H1("Second Page"),
            P("Toast messages should be floating at the top of the page."),
        ),
        P("This is the second page."),
        P('When this page got loaded you should see the toast message "Welcome to the second page!".'),
        P('- When you got Redirect to this page you should also see the toast message "Toast from Redirect("/second")".'),
        P('- When you got RedirectResponse to this page you should also see the toast message "Toast from RedirectResponse("/second")".'),
        A("Go back to Home", href="/", type="button"),
    )


@app.route("/ftbutton")
def ftbutton_route(sess):
    add_toast(sess, "This is a toast message from the Ft Button. The button should be gray now.", typ="info", dismiss=True)
    return Ftbutton(hx_get="/ftbutton2", cls="secondary")


@app.route("/ftbutton2")
def ftbutton_route(sess):
    add_toast(sess, "This is a toast message from the Ft Button. The button should be blue now.", typ="info", dismiss=True)
    return Ftbutton(hx_get="/ftbutton", cls="primary")


@app.route("/ftresponsebutton")
def ftresponsebutton_route(sess):
    add_toast(sess, "This is a toast message from a Ft Response Button. The button should be gray now.", typ="info", dismiss=True)
    return FtResponse(FtResponseButton(hx_get="/ftresponsebutton2", cls="secondary"),)


@app.route("/ftresponsebutton2")
def ftresponsebutton2_route(sess):
    add_toast(sess, "This is a toast message from a Ft Response Button. The button should be blue now.", typ="info", dismiss=True)
    return FtResponse(FtResponseButton(hx_get="/ftresponsebutton", cls="primary"),)

@app.route("/tuplebutton")
def tuplebutton_route(sess):
    add_toast(sess, "This is a toast message from a Tuple Button. The button should be gray now.", typ="info", dismiss=True)
    return tuple(TupleButton(hx_get="/tuplebutton2", cls="secondary"))

@app.route("/tuplebutton2")
def tuplebutton2_route(sess):
    add_toast(sess, "This is a toast message from a Tuple Button. The button should be blue now.", typ="info", dismiss=True)
    return tuple(TupleButton(hx_get="/tuplebutton", cls="primary"))

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
    await send(add_toast(sess, f"Websocket Message: {msg}", typ="info", dismiss=True))
    await send(render_toasts(sess))
    messages.appendleft(msg)  # New messages first
    for user in users.values():  # Get `send` function for a user
        await user(render_messages(messages))  # Send the message to that user


serve()
