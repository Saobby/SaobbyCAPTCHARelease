from PIL import Image, ImageDraw, ImageFont
import random
import base64
import time
import json
from io import BytesIO
import database_action
from config import *


def gen_captcha():
    def check_pos(npos, char_pos, min_distance):
        nx, ny = npos
        for i in char_pos:
            ox, oy = i[1], i[2]
            d = ((nx - ox) ** 2 + (ny - oy) ** 2) ** 0.5
            if d < min_distance:
                return False
        return True

    def get_random_color():
        return random.randint(0, 128), random.randint(0, 128), random.randint(0, 128), 255

    def get_random_str(lens):
        ret = ""
        char = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(lens):
            ret = ret + char[random.randint(0, len(char)-1)]
        return ret

    bg_img = Image.open("captcha-bg/{}.png".format(random.randint(1, BG_COUNT)))
    bg_img = bg_img.convert("RGBA")
    bg_img = bg_img.resize((300, 225))
    with open("captcha-words.txt", "r", encoding="utf-8") as f:
        words_list = f.readlines()
    word = random.choice(words_list).replace("\n", "")
    char_pos = []  # [("字", x, y), ("字", x, y)]
    for char in word:
        ci = Image.new("RGBA", (int(FONT_SIZE*1.2), int(FONT_SIZE*1.2)), (255, 255, 255, 255))
        ci_draw = ImageDraw.Draw(ci)
        font = ImageFont.truetype("captcha-font/{}.ttf".format(random.randint(1, FONT_COUNT)), size=FONT_SIZE)
        ci_draw.text((0, 0), char, font=font, fill=get_random_color())
        ci = ci.rotate(random.randint(-MAX_SPIN_ANGLE, MAX_SPIN_ANGLE), expand=True)
        while True:
            px = random.randint(0, bg_img.size[0] - ci.size[0])
            py = random.randint(0, bg_img.size[1] - ci.size[1])
            if check_pos((px, py), char_pos, FONT_SIZE*2):
                break
        for y in range(ci.size[1]):
            for x in range(ci.size[0]):
                if ci.getpixel((x, y)) == (0, 0, 0, 0) or ci.getpixel((x, y)) == (255, 255, 255, 255):
                    pass
                else:
                    bg_img.putpixel((px+x, py+y), (ci.getpixel((x, y))))
        char_pos.append((char, px+0.5*ci.size[0], py+0.5*ci.size[1]))
    captcha_img = BytesIO()
    bg_img.save(captcha_img, format="png")
    captcha_img.seek(0)
    captcha_b64 = base64.b64encode(captcha_img.read())
    info = {"answer": word, "pos": char_pos, "time": time.time(), "is_used": False}
    cid = get_random_str(64)
    db_session = database_action.get_session()
    database_action.save_captcha_info(cid, json.dumps(info), db_session)
    db_session.close()
    return {"captcha_id": cid, "captcha_img": "data:image/png;base64,"+str(captcha_b64)[2:-1],
            "captcha_lens": len(word)}


def get_distance(x0, y0, x1, y1):
    return ((x0-x1)**2+(y0-y1)**2)**0.5


def get_token(captcha_id: str, pos: str):
    def get_random_str(lens):
        ret = ""
        char = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(lens):
            ret = ret + char[random.randint(0, len(char)-1)]
        return ret
    if captcha_id is None or pos is None:
        return json.dumps({"validity": False, "message": "参数错误", "token": None})
    db_session = database_action.get_session()
    c_info_ = database_action.get_captcha_info(captcha_id, db_session)
    if c_info_ is None:
        db_session.close()
        return json.dumps({"validity": False, "message": "无效的验证码ID", "token": None})
    c_info = json.loads(c_info_.data)
    if c_info["is_used"]:
        db_session.close()
        return json.dumps({"validity": False, "message": "无效的验证码ID", "token": None})
    new_info = c_info.copy()
    new_info["is_used"] = True
    c_info_.data = json.dumps(new_info)
    db_session.commit()
    if abs(time.time() - c_info["time"]) > 300:
        db_session.close()
        return json.dumps({"validity": False, "message": "此验证码已过期", "token": None})
    c_answer = c_info["answer"]
    c_pos = c_info["pos"]
    u_pos = pos.split(",")[:-1]
    u_answer = ""
    if len(u_pos) / 2 != len(c_answer):
        db_session.close()
        return json.dumps({"validity": False, "message": "坐标参数无效", "token": None})
    for i in range(0, len(u_pos), 2):
        u_pos_x = float(u_pos[i])
        u_pos_y = float(u_pos[i + 1])
        u_now_chr = ""
        for j in c_pos:
            if get_distance(u_pos_x, u_pos_y, j[1], j[2]) < FONT_SIZE / 2 * 1.3:
                u_now_chr = j[0]
                c_pos.remove(j)
                break
        if u_now_chr == "":
            db_session.close()
            return json.dumps({"validity": False, "message": "验证码错误", "token": None})
        u_answer += u_now_chr
    if u_answer != c_answer:
        db_session.close()
        return json.dumps({"validity": False, "message": "验证码错误", "token": None})
    token = get_random_str(64)
    t_info = {"captcha_id": captcha_id, "time": time.time(), "is_used": False}
    database_action.save_captcha_token(token, json.dumps(t_info), db_session)
    db_session.close()
    return json.dumps({"validity": True, "message": None, "token": token})


def check_token(token: str):
    if token is None:
        return json.dumps({"validity": False, "message": "参数错误"})
    db_session = database_action.get_session()
    t_info_ = database_action.get_captcha_token(token, db_session)
    if t_info_ is None:
        db_session.close()
        return json.dumps({"validity": False, "message": "无效的token"})
    t_info = json.loads(t_info_.data)
    if t_info["is_used"]:
        db_session.close()
        return json.dumps({"validity": False, "message": "无效的token"})
    new_info = t_info.copy()
    new_info["is_used"] = True
    t_info_.data = json.dumps(new_info)
    db_session.commit()
    t_time = t_info["time"]
    if abs(time.time() - t_time) > 600:
        db_session.close()
        return json.dumps({"validity": False, "message": "此token已过期"})
    db_session.close()
    return json.dumps({"validity": True, "message": None})


if __name__ == "__main__":
    t = time.time()
    print(gen_captcha())
    print(time.time()-t)
