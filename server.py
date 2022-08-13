from flask import *
import get_image


app = Flask(__name__)
app.secret_key = "saobi23333"


@app.route("/", methods=["get"])
def home():
    return render_template("captcha.html")


@app.route("/api/number", methods=["get"])
def api_number():
    num = request.args.get("num")
    try:
        num = int(num)
    except:
        return abort(400)
    str1 = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="29.5" height="30.43125" viewBox="0,0,29.5,30.43125"><g transform="translate(-225.25,-164.31875)"><g data-paper-data="{&quot;isPaintingLayer&quot;:true}" fill-rule="nonzero" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" style="mix-blend-mode: normal"><path d="M226.5,180c0,-7.45584 6.04416,-13.5 13.5,-13.5c7.45584,0 13.5,6.04416 13.5,13.5c0,7.45584 -6.04416,13.5 -13.5,13.5c-7.45584,0 -13.5,-6.04416 -13.5,-13.5z" fill="#ffffff" stroke="#000000" stroke-width="2.5"/><text transform="translate(234.28,185.76875) scale(0.5,0.5)" font-size="40" xml:space="preserve" fill="#000000" fill-rule="nonzero" stroke="none" stroke-width="1" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" font-family="Sans Serif" font-weight="normal" text-anchor="start" style="mix-blend-mode: normal"><tspan x="0" dy="0">'
    str2 = '</tspan></text></g></g></svg>'
    ret = str1 + str(num) + str2
    return ret


@app.route("/api/get_token", methods=["post"])
def api_check_captcha():
    captcha_id = request.form.get("id")
    pos = request.form.get("pos")
    return get_image.get_token(captcha_id, pos)


@app.after_request
def add_header(r):
    if request.path == "/api/number":
        # r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        r.headers["Cache-Control"] = "max-age=315360000"
        # r.headers["Pragma"] = "no-cache"
        # r.headers["Expires"] = "0"
        r.headers["Content-Type"] = "image/svg+xml; charset=utf-8"
        r.headers["Content-Disposition"] = "inline; filename=number.svg"
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


@app.route("/api/get_image", methods=["post"])
def api_get_image():
    # time.sleep(3)
    return get_image.gen_captcha()


@app.route("/api/check_token", methods=["post"])
def api_check_token():
    token = request.form.get("s-captcha-token")
    return get_image.check_token(token)


if __name__ == "__main__":
    app.run(debug=True, port=9999)
