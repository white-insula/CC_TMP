# -*- coding: utf-8 -*-
"""生成第 34、35 讲用的合成答题卡（合成教学样本，不是学生答题卡，也不是 [GA] 原 template）。

坐标体系（与第 34 讲脚本一致）：
  拉正后的卡 600×800；四个定位块的外角分别对应 (0,0)、(599,0)、(599,799)、(0,799)。
  template_synthetic.json：
    choice_roi_rect  —— 选择题区域在 600×800 卡上的 (x, y, w, h)；裁出后缩放到 600×400
    choice_pos_list  —— 每题 4 个选项格在 600×400 选择题区域里的 (x, y, w, h)
    number_roi_rect / number_pos_list —— 学号区域（缩放到 400×300）与每列 0—9 的格子
扫描图：把 600×800 的版面放大 1.5 倍画在白纸上，再整体旋转 1°、轻微模糊并加噪声，保存为 JPG。
定位块在扫描图上约 30×15 像素（面积约 450，宽高比约 2），满足脚本 1.6 ≤ w/h ≤ 2.3、300 ≤ 面积 ≤ 600。

用法：python make_synthetic_cards.py      （在本目录运行；同时生成 ../35/ 的批量样本）
"""
import json
import os
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = 1.5                    # 版面 → 扫描图的放大倍数
OFF = (60, 60)             # 版面在扫描纸上的左上偏移
PAGE = (int(600 * S) + 120, int(800 * S) + 120)
N_Q = 20
CHOICE_ROI = (40, 380, 520, 380)          # 600×800 卡上
NUMBER_ROI = (60, 110, 300, 220)
N_DIGITS = 6


def layout():
    """返回模板（600×400 / 400×300 坐标）以及每个格子在 600×800 卡上的位置。"""
    cx0, cy0, cw0, ch0 = CHOICE_ROI
    sx, sy = 600 / cw0, 400 / ch0
    choice_pos, choice_card = [], []
    for q in range(N_Q):
        col, r = divmod(q, 5)
        gx, gy = cx0 + 20 + col * 128, cy0 + 40 + r * 66               # 每题起点（卡坐标）
        group, gcard = [], []
        for j in range(4):
            x, y, w, h = gx + 24 + j * 24, gy, 18, 18                  # 18×18 方格（宽高比 1，不会被当成定位块）
            gcard.append((x, y, w, h))
            group.append([int(round((x - cx0) * sx)), int(round((y - cy0) * sy)), int(round(w * sx)), int(round(h * sy))])
        choice_pos.append(group); choice_card.append(gcard)
    nx0, ny0, nw0, nh0 = NUMBER_ROI
    ux, uy = 400 / nw0, 300 / nh0
    number_pos, number_card = [], []
    for k in range(N_DIGITS):
        col, ccard = [], []
        for d in range(10):
            x, y, w, h = nx0 + 20 + k * 44, ny0 + 16 + d * 20, 16, 16
            ccard.append((x, y, w, h))
            col.append([int(round((x - nx0) * ux)), int(round((y - ny0) * uy)), int(round(w * ux)), int(round(h * uy))])
        number_pos.append(col); number_card.append(ccard)
    t = {"说明": "合成教学样本模板，不是 [GA] 学生项目的 template.json",
         "choice_roi_rect": list(CHOICE_ROI), "choice_pos_list": choice_pos,
         "number_roi_rect": list(NUMBER_ROI), "number_pos_list": number_pos}
    return t, choice_card, number_card


def to_raw(x, y):
    return int(round(OFF[0] + x * S)), int(round(OFF[1] + y * S))


def rect(img, x, y, w, h, color, thick):
    p, q = to_raw(x, y), to_raw(x + w, y + h)
    cv2.rectangle(img, p, (q[0] - 1, q[1] - 1), color, thick)


def draw_card(sid, marks, choice_card, number_card, locators="ok", seed=0, angle=1.0):
    """marks: {题号(1起): [(选项索引, 方式)]}，方式 full / light / half。
    locators: ok / missing_one / extra_one（多一个与定位块同尺寸的干扰块）"""
    rng = np.random.RandomState(seed)
    img = np.full((PAGE[1], PAGE[0], 3), 250, np.uint8)
    # 四个定位块：外角正好在版面四角
    blocks = [(0, 0), (580, 0), (580, 790), (0, 790)]
    if locators == "missing_one":
        blocks = blocks[:3]
    for (x, y) in blocks:
        rect(img, x, y, 20, 10, (20, 20, 20), -1)
    if locators == "extra_one":
        rect(img, 300, 360, 20, 10, (20, 20, 20), -1)                   # 版面中间多出的同尺寸黑块
    cv2.putText(img, "SYNTHETIC ANSWER CARD  (teaching sample)", to_raw(40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (60, 60, 60), 2)
    # 学号区
    rect(img, *NUMBER_ROI, (120, 120, 120), 1)
    for k, col in enumerate(number_card):
        for d, (x, y, w, h) in enumerate(col):
            rect(img, x, y, w, h, (110, 110, 110), 1)
            if int(sid[k]) == d:
                rect(img, x + 2, y + 2, w - 4, h - 4, (25, 25, 25), -1)
    # 选择题区
    rect(img, *CHOICE_ROI, (120, 120, 120), 1)
    for q, group in enumerate(choice_card):
        x0, y0 = group[0][0] - 22, group[0][1] + 13
        cv2.putText(img, str(q + 1), to_raw(x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (90, 90, 90), 1)
        for j, (x, y, w, h) in enumerate(group):
            rect(img, x, y, w, h, (110, 110, 110), 1)
        for j, how in marks.get(q + 1, []):
            x, y, w, h = group[j]
            if how == "full":
                rect(img, x + 2, y + 2, w - 4, h - 4, (25, 25, 25), -1)
            elif how == "light":                                         # 铅笔涂得很淡：灰度约 160，高于阈值 127
                rect(img, x + 2, y + 2, w - 4, h - 4, (160, 160, 160), -1)
            elif how == "half":                                          # 只涂了左半边
                rect(img, x + 2, y + 2, (w - 4) // 2, h - 4, (25, 25, 25), -1)
    M = cv2.getRotationMatrix2D((PAGE[0] / 2, PAGE[1] / 2), angle, 1.0)
    img = cv2.warpAffine(img, M, PAGE, borderValue=(250, 250, 250))
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = np.clip(img.astype(np.int16) + rng.randint(-6, 7, img.shape), 0, 255).astype(np.uint8)
    return img


def save_jpg(path, img):
    cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])


def main():
    t, choice_card, number_card = layout()
    with open(os.path.join(HERE, "template_synthetic.json"), "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False)
    # 34 讲：一张卡覆盖各种填涂情况
    marks34 = {1: [(0, "full")], 2: [(3, "full")], 3: [(2, "full")], 4: [(1, "full")], 5: [(0, "full"), (2, "full")],   # 第 5 题多涂
               6: [(1, "light")],                                                                                     # 第 6 题浅涂
               7: [(3, "half")],                                                                                      # 第 7 题只涂一半
               8: [(2, "full")], 9: [], 10: [(0, "full")]}                                                            # 第 9 题空白
    for q in range(11, N_Q + 1):
        marks34[q] = [((q * 7) % 4, "full")]
    sid34 = "012345"
    save_jpg(os.path.join(HERE, "card_synthetic_01.jpg"), draw_card(sid34, marks34, choice_card, number_card, seed=34))
    truth34 = {"说明": "合成教学样本真值（填涂意图）；light=浅涂、half=只涂一半、多个选项=多涂、空列表=空白",
               "sid": sid34, "marks": {str(k): [["ABCD"[j], how] for j, how in v] for k, v in marks34.items()}}
    with open(os.path.join(HERE, "card_synthetic_01_truth.json"), "w", encoding="utf-8") as f:
        json.dump(truth34, f, ensure_ascii=False, indent=1)
    # 34 讲：两张故意出问题的卡（定位应失败并可检测）
    save_jpg(os.path.join(HERE, "card_synthetic_missing_locator.jpg"), draw_card(sid34, marks34, choice_card, number_card, "missing_one", seed=35))
    save_jpg(os.path.join(HERE, "card_synthetic_extra_block.jpg"), draw_card(sid34, marks34, choice_card, number_card, "extra_one", seed=36))
    print("  34/ template_synthetic.json、card_synthetic_01.jpg（+truth）、card_synthetic_missing_locator.jpg、card_synthetic_extra_block.jpg")

    # 35 讲：批量样本（虚构学号保留前导 0）
    d35 = os.path.join(os.path.dirname(HERE), "35", "cards_synthetic")
    os.makedirs(d35, exist_ok=True)
    for f in os.listdir(d35):
        os.remove(os.path.join(d35, f))
    rng = np.random.RandomState(350)
    students = ["000123", "004560", "012034", "100200", "250009"]
    truth35 = {"说明": "合成教学样本：5 张正常卡 + 1 张缺定位块的坏卡 + 1 个非 jpg 文件（应被跳过）", "cards": {}}
    for i, sid in enumerate(students):
        picks = {q: int(rng.randint(0, 4)) for q in range(1, N_Q + 1)}
        marks = {q: [(j, "full")] for q, j in picks.items()}
        name = f"card_{i + 1:02d}_synthetic.jpg"
        save_jpg(os.path.join(d35, name), draw_card(sid, marks, choice_card, number_card, seed=400 + i, angle=[1.0, -0.8, 0.5, 1.2, -1.0][i]))
        truth35["cards"][name] = {"sid": sid, "picks": ["ABCD"[picks[q]] for q in range(1, N_Q + 1)]}
    bad = "card_06_synthetic_bad.jpg"
    save_jpg(os.path.join(d35, bad), draw_card("999999", {1: [(0, "full")]}, choice_card, number_card, "missing_one", seed=499))
    truth35["cards"][bad] = {"sid": None, "picks": None, "expect": "定位失败"}
    with open(os.path.join(d35, "readme_not_a_card.txt"), "w", encoding="utf-8") as f:
        f.write("这不是答题卡，批量程序应跳过非 .jpg 文件。\n")
    with open(os.path.join(os.path.dirname(HERE), "35", "cards_synthetic_truth.json"), "w", encoding="utf-8") as f:
        json.dump(truth35, f, ensure_ascii=False, indent=1)
    # 标准答案：题号乱序、不连续（缺 7、15 题）、分值不同
    order = [3, 1, 2, 20, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19]
    rng2 = np.random.RandomState(351)
    lines = [f"{q}-{'ABCD'[int(rng2.randint(0, 4))]}-{[1, 2, 3][q % 3]}" for q in order]
    with open(os.path.join(os.path.dirname(HERE), "35", "答案_synthetic.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("  35/ cards_synthetic/（6 张 jpg + 1 个 txt）、cards_synthetic_truth.json、答案_synthetic.txt")


if __name__ == "__main__":
    main()
