#!fontforge --lang=py -script

# 2つのフォントを合成する

import configparser
import math
import os
import shutil
import sys
import uuid
from decimal import ROUND_HALF_UP, Decimal

import fontforge
import psMat

# iniファイルを読み込む
settings = configparser.ConfigParser()
settings.read("build.ini", encoding="utf-8")

VERSION = settings.get("DEFAULT", "VERSION")
FONT_NAME = settings.get("DEFAULT", "FONT_NAME")
JP_FONT = settings.get("DEFAULT", "JP_FONT")
ENG_FONT = settings.get("DEFAULT", "ENG_FONT")
ENG_FONT_LG = settings.get("DEFAULT", "ENG_FONT_LG")
SOURCE_FONTS_DIR = settings.get("DEFAULT", "SOURCE_FONTS_DIR")
BUILD_FONTS_DIR = settings.get("DEFAULT", "BUILD_FONTS_DIR")
VENDER_NAME = settings.get("DEFAULT", "VENDER_NAME")
FONTFORGE_PREFIX = settings.get("DEFAULT", "FONTFORGE_PREFIX")
IDEOGRAPHIC_SPACE = settings.get("DEFAULT", "IDEOGRAPHIC_SPACE")
WIDTH_35_STR = settings.get("DEFAULT", "WIDTH_35_STR")
HIDDEN_ZENKAKU_SPACE_STR = settings.get("DEFAULT", "HIDDEN_ZENKAKU_SPACE_STR")
JPDOC_STR = settings.get("DEFAULT", "JPDOC_STR")
DOT_ZERO_STR = settings.get("DEFAULT", "DOT_ZERO_STR")
NERD_FONTS_STR = settings.get("DEFAULT", "NERD_FONTS_STR")
LIGA_STR = settings.get("DEFAULT", "LIGA_STR")
EM_ASCENT = int(settings.get("DEFAULT", "EM_ASCENT"))
EM_DESCENT = int(settings.get("DEFAULT", "EM_DESCENT"))
OS2_ASCENT = int(settings.get("DEFAULT", "OS2_ASCENT"))
OS2_DESCENT = int(settings.get("DEFAULT", "OS2_DESCENT"))
HALF_WIDTH_12 = int(settings.get("DEFAULT", "HALF_WIDTH_12"))
FULL_WIDTH_35 = int(settings.get("DEFAULT", "FULL_WIDTH_35"))
ITALIC_ANGLE = int(settings.get("DEFAULT", "ITALIC_ANGLE"))

COPYRIGHT = """[JetBrains Mono]
Copyright 2020 The JetBrains Mono Project Authors https://github.com/JetBrains/JetBrainsMono

[BIZ UDGothic]
Copyright 2022 The BIZ UDGothic Project Authors https://github.com/googlefonts/morisawa-biz-ud-mincho

[Nerd Fonts]
Copyright (c) 2014, Ryan L McIntyre https://ryanlmcintyre.com

[UDEV Gothic]
Copyright 2022 Yuko Otawara
"""  # noqa: E501

options = {}
hack_font = None
nerd_font = None


def main():
    # オプション判定
    get_options()
    if options.get("unknown-option"):
        usage()
        return

    # buildディレクトリを作成する
    if os.path.exists(BUILD_FONTS_DIR) and not options.get("do-not-delete-build-dir"):
        shutil.rmtree(BUILD_FONTS_DIR)
        os.mkdir(BUILD_FONTS_DIR)
    if not os.path.exists(BUILD_FONTS_DIR):
        os.mkdir(BUILD_FONTS_DIR)

    generate_font(
        jp_style="Regular",
        eng_style="Regular",
        merged_style="Regular",
    )
    generate_font(
        jp_style="Bold",
        eng_style="Bold",
        merged_style="Bold",
    )
    generate_font(
        jp_style="Regular",
        eng_style="Italic",
        merged_style="Italic",
    )
    generate_font(
        jp_style="Bold",
        eng_style="BoldItalic",
        merged_style="BoldItalic",
    )


def usage():
    print(
        f"Usage: {sys.argv[0]} "
        "[--hidden-zenkaku-space] [--35] [--jpdoc] [--nerd-font] [--liga] [--dot-zero]"
    )


def get_options():
    """オプションを取得する"""

    global options

    # オプションなしの場合は何もしない
    if len(sys.argv) == 1:
        return

    for arg in sys.argv[1:]:
        # オプション判定
        if arg == "--do-not-delete-build-dir":
            options["do-not-delete-build-dir"] = True
        elif arg == "--hidden-zenkaku-space":
            options["hidden-zenkaku-space"] = True
        elif arg == "--35":
            options["35"] = True
        elif arg == "--jpdoc":
            options["jpdoc"] = True
        elif arg == "--nerd-font":
            options["nerd-font"] = True
        elif arg == "--liga":
            options["liga"] = True
        elif arg == "--dot-zero":
            options["dot-zero"] = True
        else:
            options["unknown-option"] = True
            return


def generate_font(jp_style, eng_style, merged_style):
    print(f"=== Generate {merged_style} ===")

    # 合成するフォントを開く
    jp_font, eng_font = open_fonts(jp_style, eng_style)

    # 0 をスラッシュゼロにする
    if not options.get("dot-zero"):
        slash_zero(eng_font, eng_style)

    # フォントのEMを揃える
    adjust_em(eng_font)

    # 日本語文書に頻出する記号を英語フォントから削除する
    if options.get("jpdoc"):
        remove_jpdoc_symbols(eng_font)

    # いくつかのグリフ形状に調整を加える
    adjust_some_glyph(jp_font, eng_font)

    # 重複するグリフを削除する
    delete_duplicate_glyphs(jp_font, eng_font)

    # 日本語グリフの斜体を生成する
    if "Italic" in merged_style:
        transform_italic_glyphs(jp_font)

    if options.get("35"):
        # eng_fontを3:5幅にする
        adjust_width_35_eng(eng_font)
        # jp_fontを3:5幅にする
        adjust_width_35_jp(jp_font)
    else:
        # 1:2 幅にする
        transform_half_width(eng_font)
        # 幅からはみ出たグリフを縮小する
        down_scale_redundant_size_glyph(eng_font)

    # GSUBテーブルを削除する (ひらがな等の全角文字が含まれる行でリガチャが解除される対策)
    if options.get("liga"):
        # ただしリガチャ版の合成の場合には日本語フォント側のGSUBテーブルが残っていると
        # なぜか「'あ' === data」のように日本語が含まれる行でリガチャが解除される
        # 不具合があるため、リガチャ版では問答無用でGSUBテーブルを削除する
        remove_lookups(jp_font, remove_gsub=True, remove_gpos=True)
    else:
        remove_lookups(jp_font, remove_gsub=False, remove_gpos=True)

    # 全角スペースを可視化する
    if not options.get("hidden-zenkaku-space"):
        visualize_zenkaku_space(jp_font)

    # Nerd Fontのグリフを追加する
    if options.get("nerd-font"):
        add_nerd_font_glyphs(jp_font, eng_font)

    # オプション毎の修飾子を追加する
    variant = WIDTH_35_STR if options.get("35") else ""
    variant += HIDDEN_ZENKAKU_SPACE_STR if options.get("hidden-zenkaku-space") else ""
    variant += DOT_ZERO_STR if options.get("dot-zero") else ""
    variant += JPDOC_STR if options.get("jpdoc") else ""
    variant += NERD_FONTS_STR if options.get("nerd-font") else ""
    variant += LIGA_STR if options.get("liga") else ""

    # macOSでのpostテーブルの使用性エラー対策
    # 重複するグリフ名を持つグリフをリネームする
    delete_glyphs_with_duplicate_glyph_names(eng_font)
    delete_glyphs_with_duplicate_glyph_names(jp_font)

    # メタデータを編集する
    cap_height = int(
        Decimal(str(eng_font[0x0048].boundingBox()[3])).quantize(
            Decimal("0"), ROUND_HALF_UP
        )
    )
    x_height = int(
        Decimal(str(eng_font[0x0078].boundingBox()[3])).quantize(
            Decimal("0"), ROUND_HALF_UP
        )
    )
    edit_meta_data(eng_font, merged_style, variant, cap_height, x_height)
    edit_meta_data(jp_font, merged_style, variant, cap_height, x_height)

    # ttfファイルに保存
    # ヒンティングが残っていると不具合に繋がりがちなので外す。
    # ヒンティングはあとで ttfautohint で行う。
    # flags=("no-hints", "omit-instructions") を使うとヒンティングだけでなく GPOS や GSUB も削除されてしまうので使わない
    eng_font.generate(
        f"{BUILD_FONTS_DIR}/{FONTFORGE_PREFIX}{FONT_NAME}{variant}-{merged_style}-eng.ttf",
    )
    jp_font.generate(
        f"{BUILD_FONTS_DIR}/{FONTFORGE_PREFIX}{FONT_NAME}{variant}-{merged_style}-jp.ttf",
    )

    # ttfを閉じる
    jp_font.close()
    eng_font.close()


def open_fonts(jp_style: str, eng_style: str):
    """フォントを開く"""
    jp_font = fontforge.open(
        SOURCE_FONTS_DIR + "/" + JP_FONT.replace("{style}", jp_style)
    )
    if options.get("liga"):
        eng_font = fontforge.open(
            SOURCE_FONTS_DIR + "/" + ENG_FONT_LG.replace("{style}", eng_style)
        )
    else:
        eng_font = fontforge.open(
            SOURCE_FONTS_DIR + "/" + ENG_FONT.replace("{style}", eng_style)
        )

    # fonttools merge エラー対処
    jp_font = altuni_to_entity(jp_font)

    # フォント参照を解除する
    for glyph in jp_font.glyphs():
        if glyph.isWorthOutputting():
            jp_font.selection.select(("more", None), glyph)
    jp_font.unlinkReferences()
    for glyph in eng_font.glyphs():
        if glyph.isWorthOutputting():
            eng_font.selection.select(("more", None), glyph)
    eng_font.unlinkReferences()
    jp_font.selection.none()
    eng_font.selection.none()

    return jp_font, eng_font


def altuni_to_entity(jp_font):
    """Alternate Unicodeで透過的に参照して表示している箇所を実体のあるグリフに変換する"""
    for glyph in jp_font.glyphs():
        if glyph.altuni is not None:
            # 以下形式のタプルで返ってくる
            # (unicode-value, variation-selector, reserved-field)
            # 第3フィールドは常に0なので無視
            altunis = glyph.altuni

            # variation-selectorがなく (-1)、透過的にグリフを参照しているものは実体のグリフに変換する
            before_altuni = ""
            for altuni in altunis:
                # 直前のaltuniと同じ場合はスキップ
                if altuni[1] == -1 and before_altuni != ",".join(map(str, altuni)):
                    glyph.altuni = None
                    copy_target_unicode = altuni[0]
                    try:
                        copy_target_glyph = jp_font.createChar(
                            copy_target_unicode,
                            f"uni{hex(copy_target_unicode).replace('0x', '').upper()}copy",
                        )
                    except Exception:
                        copy_target_glyph = jp_font[copy_target_unicode]
                    copy_target_glyph.clear()
                    copy_target_glyph.width = glyph.width
                    # copy_target_glyph.addReference(glyph.glyphname)
                    jp_font.selection.select(glyph.glyphname)
                    jp_font.copy()
                    jp_font.selection.select(copy_target_glyph.glyphname)
                    jp_font.paste()
                before_altuni = ",".join(map(str, altuni))
    # エンコーディングの整理のため、開き直す
    font_path = f"{BUILD_FONTS_DIR}/{jp_font.fullname}_{uuid.uuid4()}.ttf"
    jp_font.generate(font_path)
    jp_font.close()
    reopen_jp_font = fontforge.open(font_path)
    # 一時ファイルを削除
    os.remove(font_path)
    return reopen_jp_font


def adjust_some_glyph(jp_font, eng_font):
    """いくつかのグリフ形状に調整を加える"""
    # FULLWIDTH RIGHT CURLY BRACKET は全角優先にするため削除
    eng_font.selection.select("U+FF5B")
    eng_font.selection.select(("more", None), "U+FF5D")
    for glyph in eng_font.selection.byGlyphs:
        glyph.clear()
    eng_font.selection.none()
    # 全角括弧の開きを広くする
    full_width = jp_font[0x3042].width
    for glyph_name in [0xFF08, 0xFF3B, 0xFF5B]:
        glyph = jp_font[glyph_name]
        glyph.transform(psMat.translate(-(full_width / 6), 0))
        glyph.width = full_width
    for glyph_name in [0xFF09, 0xFF3D, 0xFF5D]:
        glyph = jp_font[glyph_name]
        glyph.transform(psMat.translate((full_width / 6), 0))
        glyph.width = full_width
    # LEFT SINGLE QUOTATION MARK (U+2018) ～ DOUBLE LOW-9 QUOTATION MARK (U+201E) の幅を全角幅にする
    for uni in range(0x2018, 0x201E + 1):
        try:
            glyph = jp_font[uni]
            if glyph.isWorthOutputting():
                glyph.transform(psMat.translate((full_width - glyph.width) / 2, 0))
                glyph.width = full_width
        except TypeError:
            # グリフが存在しない場合は継続する
            continue
    jp_font.selection.none()


def slash_zero(eng_font, style):
    eng_font.selection.select("zero.zero")
    eng_font.copy()
    eng_font.selection.select("zero")
    eng_font.clear()
    eng_font.paste()
    eng_font.selection.none()


def adjust_em(font):
    """フォントのEMを揃える"""
    font.em = EM_ASCENT + EM_DESCENT


def delete_duplicate_glyphs(jp_font, eng_font):
    """jp_fontとeng_fontのグリフを比較し、重複するグリフを削除する"""

    eng_font.selection.none()
    jp_font.selection.none()

    for glyph in jp_font.glyphs("encoding"):
        try:
            if glyph.isWorthOutputting() and glyph.unicode > 0:
                eng_font.selection.select(("more", "unicode"), glyph.unicode)
        except ValueError:
            # Encoding is out of range のときは継続する
            continue
    for glyph in eng_font.selection.byGlyphs:
        # if glyph.isWorthOutputting():
        jp_font.selection.select(("more", "unicode"), glyph.unicode)
    for glyph in jp_font.selection.byGlyphs:
        glyph.clear()

    jp_font.selection.none()
    eng_font.selection.none()


def remove_lookups(font, remove_gsub=True, remove_gpos=True):
    """GSUB, GPOSテーブルを削除する"""
    if remove_gsub:
        for lookup in font.gsub_lookups:
            font.removeLookup(lookup)
    if remove_gpos:
        for lookup in font.gpos_lookups:
            font.removeLookup(lookup)


def transform_italic_glyphs(font):
    # 傾きを設定する
    font.italicangle = -ITALIC_ANGLE
    # 全グリフを斜体に変換
    for glyph in font.glyphs():
        orig_width = glyph.width
        glyph.transform(psMat.skew(ITALIC_ANGLE * math.pi / 180))
        glyph.transform(psMat.translate(-94, 0))
        glyph.width = orig_width


def remove_jpdoc_symbols(eng_font):
    """日本語文書に頻出する記号を削除する"""
    eng_font.selection.none()
    # § (U+00A7)
    eng_font.selection.select(("more", "unicode"), 0x00A7)
    # ± (U+00B1)
    eng_font.selection.select(("more", "unicode"), 0x00B1)
    # ¶ (U+00B6)
    eng_font.selection.select(("more", "unicode"), 0x00B6)
    # ÷ (U+00F7)
    eng_font.selection.select(("more", "unicode"), 0x00F7)
    # × (U+00D7)
    eng_font.selection.select(("more", "unicode"), 0x00D7)
    # ⇒ (U+21D2)
    eng_font.selection.select(("more", "unicode"), 0x21D2)
    # ⇔ (U+21D4)
    eng_font.selection.select(("more", "unicode"), 0x21D4)
    # ■-□ (U+25A0-U+25A1)
    eng_font.selection.select(("more", "ranges"), 0x25A0, 0x25A1)
    # ▲-△ (U+25B2-U+25B3)
    eng_font.selection.select(("more", "ranges"), 0x25A0, 0x25B3)
    # ▼-▽ (U+25BC-U+25BD)
    eng_font.selection.select(("more", "ranges"), 0x25BC, 0x25BD)
    # ◆-◇ (U+25C6-U+25C7)
    eng_font.selection.select(("more", "ranges"), 0x25C6, 0x25C7)
    # ○ (U+25CB)
    eng_font.selection.select(("more", "unicode"), 0x25CB)
    # ◎-● (U+25CE-U+25CF)
    eng_font.selection.select(("more", "ranges"), 0x25CE, 0x25CF)
    # ◥ (U+25E5)
    eng_font.selection.select(("more", "unicode"), 0x25E5)
    # ◯ (U+25EF)
    eng_font.selection.select(("more", "unicode"), 0x25EF)
    # √ (U+221A)
    eng_font.selection.select(("more", "unicode"), 0x221A)
    # ∞ (U+221E)
    eng_font.selection.select(("more", "unicode"), 0x221E)
    # ‐ (U+2010)
    eng_font.selection.select(("more", "unicode"), 0x2010)
    # ‘-‚ (U+2018-U+201A)
    eng_font.selection.select(("more", "ranges"), 0x2018, 0x201A)
    # “-„ (U+201C-U+201E)
    eng_font.selection.select(("more", "ranges"), 0x201C, 0x201E)
    # †-‡ (U+2020-U+2021)
    eng_font.selection.select(("more", "ranges"), 0x2020, 0x2021)
    # … (U+2026)
    eng_font.selection.select(("more", "unicode"), 0x2026)
    # ‰ (U+2030)
    eng_font.selection.select(("more", "unicode"), 0x2030)
    # ←-↓ (U+2190-U+2193)
    eng_font.selection.select(("more", "ranges"), 0x2190, 0x2193)
    # ∀ (U+2200)
    eng_font.selection.select(("more", "unicode"), 0x2200)
    # ∂-∃ (U+2202-U+2203)
    eng_font.selection.select(("more", "ranges"), 0x2202, 0x2203)
    # ∈ (U+2208)
    eng_font.selection.select(("more", "unicode"), 0x2208)
    # ∋ (U+220B)
    eng_font.selection.select(("more", "unicode"), 0x220B)
    # ∑ (U+2211)
    eng_font.selection.select(("more", "unicode"), 0x2211)
    # ∥ (U+2225)
    eng_font.selection.select(("more", "unicode"), 0x2225)
    # ∧-∬ (U+2227-U+222C)
    eng_font.selection.select(("more", "ranges"), 0x2227, 0x222C)
    # ≠-≡ (U+2260-U+2261)
    eng_font.selection.select(("more", "ranges"), 0x2260, 0x2261)
    # ⊂-⊃ (U+2282-U+2283)
    eng_font.selection.select(("more", "ranges"), 0x2282, 0x2283)
    # ⊆-⊇ (U+2286-U+2287)
    eng_font.selection.select(("more", "ranges"), 0x2286, 0x2287)
    # ─-╿ (Box Drawing) (U+2500-U+257F)
    eng_font.selection.select(("more", "ranges"), 0x2500, 0x257F)
    for glyph in eng_font.selection.byGlyphs:
        if glyph.isWorthOutputting():
            glyph.clear()
    eng_font.selection.none()


def adjust_width_35_eng(eng_font):
    """英語フォントを半角3:全角5幅になるように変換する"""
    original_half_width = eng_font[0x0030].width
    after_width = int(FULL_WIDTH_35 * 3 / 5)
    x_scale = after_width / original_half_width
    for glyph in eng_font.glyphs():
        if 0 < glyph.width < after_width:
            # after_width より幅が狭い場合は位置合わせしてから幅を設定
            glyph.transform(psMat.translate((after_width - glyph.width) / 2, 0))
            glyph.width = after_width
        elif after_width < glyph.width <= original_half_width:
            # after_width より幅が広い、かつ元の半角幅より狭い場合は縮小してから幅を設定
            glyph.transform(psMat.scale(x_scale, 1))
            glyph.width = after_width
        elif original_half_width < glyph.width:
            # after_width より幅が広い (おそらく全てリガチャ) の場合は倍数にする
            multiply_number = round(glyph.width / original_half_width)
            glyph.transform(psMat.scale(x_scale, 1))
            glyph.width = after_width * multiply_number


def adjust_width_35_jp(jp_font):
    """日本語フォントを半角3:全角5幅になるように変換する"""
    after_width = int(FULL_WIDTH_35 * 3 / 5)
    jp_half_width = jp_font[0x3000].width / 2
    jp_full_width = jp_font[0x3000].width
    for glyph in jp_font.glyphs():
        if glyph.width == jp_half_width:
            glyph.transform(psMat.translate((after_width - glyph.width) / 2, 0))
            glyph.width = after_width
        elif glyph.width == jp_full_width:
            glyph.transform(psMat.translate((FULL_WIDTH_35 - glyph.width) / 2, 0))
            glyph.width = FULL_WIDTH_35


def transform_half_width(eng_font):
    """1:2幅になるように変換する"""
    before_width_eng = eng_font[0x0030].width
    after_width_eng = HALF_WIDTH_12
    # 単純 縮小後幅 / 元の幅 だと狭くなりすりぎるので、倍率を考慮する
    x_scale = 1106 / before_width_eng
    for glyph in eng_font.glyphs():
        if glyph.width > 0:
            # リガチャ考慮
            after_width_eng_multiply = after_width_eng * round(
                glyph.width / before_width_eng
            )
            # 縮小
            glyph.transform(psMat.scale(x_scale, 0.99))
            # 幅を設定
            glyph.transform(
                psMat.translate((after_width_eng_multiply - glyph.width) / 2, 0)
            )
            glyph.width = after_width_eng_multiply
            # 幾何学模様 (U+25A0-U+25FF) グリフが横幅をはみ出しすぎるので縮小する
            if 0x25A0 <= glyph.unicode <= 0x25FF:
                glyph.transform(psMat.scale(0.91, 0.91))
                glyph.width = after_width_eng_multiply


def down_scale_redundant_size_glyph(eng_font):
    """規定の幅からはみ出したグリフサイズを縮小する"""

    for glyph in eng_font.glyphs():
        xmin = glyph.boundingBox()[0]
        xmax = glyph.boundingBox()[2]

        if (
            glyph.width > 0
            and -45
            < xmin
            < 0  # 特定幅より左にはみ出している場合、意図的にはみ出しているものと見なして無視
            and abs(xmin) - 40
            < xmax - glyph.width
            < abs(xmin) + 40  # はみ出し幅が左側と右側で極端に異なる場合は無視
            and not (
                0x0020 <= glyph.unicode <= 0x02AF
            )  # latin 系のグリフ 0x0020 - 0x0192 は無視
            and not (
                0xE0B0 <= glyph.unicode <= 0xE0D4
            )  # Powerline系のグリフ 0xE0B0 - 0xE0D4 は無視
            and not (
                0x2500 <= glyph.unicode <= 0x257F
            )  # 罫線系のグリフ 0x2500 - 0x257F は無視
            and not (
                0x2591 <= glyph.unicode <= 0x2593
            )  # SHADE グリフ 0x2591 - 0x2593 は無視
        ):
            scale_glyph(glyph, 1 + (xmin / glyph.width) * 2, 1)


def scale_glyph(glyph, scale_x, scale_y):
    """グリフのスケールを調整する"""
    original_width = glyph.width
    # スケール前の中心位置を求める
    before_bb = glyph.boundingBox()
    before_center_x = (before_bb[0] + before_bb[2]) / 2
    before_center_y = (before_bb[1] + before_bb[3]) / 2
    # スケール変換
    glyph.transform(psMat.scale(scale_x, scale_y))
    # スケール後の中心位置を求める
    after_bb = glyph.boundingBox()
    after_center_x = (after_bb[0] + after_bb[2]) / 2
    after_center_y = (after_bb[1] + after_bb[3]) / 2
    # 拡大で増えた分を考慮して中心位置を調整
    glyph.transform(
        psMat.translate(
            before_center_x - after_center_x,
            before_center_y - after_center_y,
        )
    )
    glyph.width = original_width


def visualize_zenkaku_space(jp_font):
    """全角スペースを可視化する"""
    # 全角スペースを差し替え
    glyph = jp_font[0x3000]
    width_to = glyph.width
    glyph.clear()
    jp_font.mergeFonts(fontforge.open(f"{SOURCE_FONTS_DIR}/{IDEOGRAPHIC_SPACE}"))
    # 幅を設定し位置調整
    jp_font.selection.select("U+3000")
    for glyph in jp_font.selection.byGlyphs:
        width_from = glyph.width
        glyph.transform(psMat.translate((width_to - width_from) / 2, 0))
        glyph.width = width_to
    jp_font.selection.none()


def add_box_drawing_block_elements(jp_font, eng_font):
    """Box Drawing, Block Elements を追加する"""
    global hack_font
    if hack_font is None:
        hack_font = fontforge.open(f"{SOURCE_FONTS_DIR}/hack/Hack-Regular.ttf")
        hack_font.em = EM_ASCENT + EM_DESCENT
        half_width = eng_font[0x0030].width
        # 対象記号を選択
        for uni in range(0x2500, 0x259F + 1):
            hack_font.selection.select(("more", "unicode"), uni)
        # マージする記号のみを残す
        hack_font.selection.invert()
        for glyph in hack_font.selection.byGlyphs:
            hack_font.removeGlyph(glyph)
        # 位置合わせ
        for glyph in hack_font.glyphs():
            if glyph.isWorthOutputting():
                glyph.transform(psMat.translate((half_width - glyph.width) / 2, 0))
                glyph.width = half_width
    # マージする範囲をあらかじめ削除
    eng_font.selection.none()
    for uni in range(0x2500, 0x259F + 1):
        try:
            eng_font.selection.select(("more", "unicode"), uni)
        except Exception:
            pass
    for glyph in eng_font.selection.byGlyphs:
        glyph.clear()
    # jpdoc 版の場合は罫線を日本語フォント優先にする
    if not options.get("jpdoc"):
        jp_font.selection.none()
        for uni in range(0x2500, 0x259F + 1):
            try:
                jp_font.selection.select(("more", "unicode"), uni)
            except Exception:
                pass
        for glyph in jp_font.selection.byGlyphs:
            glyph.clear()
    jp_font.mergeFonts(hack_font)


def add_nerd_font_glyphs(jp_font, eng_font):
    """Nerd Fontのグリフを追加する"""
    global nerd_font
    # Nerd Fontのグリフを追加する
    if nerd_font is None:
        nerd_font = fontforge.open(f"{SOURCE_FONTS_DIR}/SymbolsNerdFont-Regular.ttf")
        nerd_font.em = EM_ASCENT + EM_DESCENT
        glyph_names = set()
        for nerd_glyph in nerd_font.glyphs():
            # Nerd Fontsのグリフ名をユニークにするため接尾辞を付ける
            nerd_glyph.glyphname = f"{nerd_glyph.glyphname}-nf"
            # postテーブルでのグリフ名重複対策
            # fonttools merge で合成した後、MacOSで `'post'テーブルの使用性` エラーが発生することへの対処
            if nerd_glyph.glyphname in glyph_names:
                nerd_glyph.glyphname = f"{nerd_glyph.glyphname}-{nerd_glyph.encoding}"
            glyph_names.add(nerd_glyph.glyphname)
            # 幅を調整する
            half_width = eng_font[0x0030].width
            # Powerline Symbols の調整
            if 0xE0B0 <= nerd_glyph.unicode <= 0xE0D4:
                # なぜかズレている右付きグリフの個別調整 (EM 1000 に変更した後を想定して調整)
                original_width = nerd_glyph.width
                if nerd_glyph.unicode == 0xE0B2:
                    nerd_glyph.transform(psMat.translate(-353 * 2.024, 0))
                elif nerd_glyph.unicode == 0xE0B6:
                    nerd_glyph.transform(psMat.translate(-414 * 2.024, 0))
                elif nerd_glyph.unicode == 0xE0C5:
                    nerd_glyph.transform(psMat.translate(-137 * 2.024, 0))
                elif nerd_glyph.unicode == 0xE0C7:
                    nerd_glyph.transform(psMat.translate(-214 * 2.024, 0))
                elif nerd_glyph.unicode == 0xE0D4:
                    nerd_glyph.transform(psMat.translate(-314 * 2.024, 0))
                nerd_glyph.width = original_width
                # 位置と幅合わせ
                if nerd_glyph.width < half_width:
                    nerd_glyph.transform(
                        psMat.translate((half_width - nerd_glyph.width) / 2, 0)
                    )
                elif nerd_glyph.width > half_width:
                    nerd_glyph.transform(psMat.scale(half_width / nerd_glyph.width, 1))
                # グリフの高さ・位置を調整する
                nerd_glyph.transform(psMat.scale(1, 1.21))
                nerd_glyph.transform(psMat.translate(0, -24))
            elif nerd_glyph.width < (EM_ASCENT + EM_DESCENT) * 0.6:
                # 幅が狭いグリフは中央寄せとみなして調整する
                nerd_glyph.transform(
                    psMat.translate((half_width - nerd_glyph.width) / 2, 0)
                )
            # 幅を設定
            nerd_glyph.width = half_width
    # 日本語フォントにマージするため、既に存在する場合は削除する
    for nerd_glyph in nerd_font.glyphs():
        if nerd_glyph.unicode != -1:
            # 既に存在する場合は削除する
            try:
                for glyph in jp_font.selection.select(
                    ("unicode", None), nerd_glyph.unicode
                ).byGlyphs:
                    glyph.clear()
            except Exception:
                pass
            try:
                for glyph in eng_font.selection.select(
                    ("unicode", None), nerd_glyph.unicode
                ).byGlyphs:
                    glyph.clear()
            except Exception:
                pass
    jp_font.mergeFonts(nerd_font)
    jp_font.selection.none()
    eng_font.selection.none()


def delete_glyphs_with_duplicate_glyph_names(font):
    """重複するグリフ名を持つグリフをリネームする"""
    glyph_name_set = set()
    for glyph in font.glyphs():
        if glyph.glyphname in glyph_name_set:
            glyph.glyphname = f"{glyph.glyphname}_{glyph.encoding}"
        else:
            glyph_name_set.add(glyph.glyphname)


def edit_meta_data(font, weight: str, variant: str, cap_height: int, x_height: int):
    """フォント内のメタデータを編集する"""
    font.ascent = EM_ASCENT
    font.descent = EM_DESCENT

    font.os2_typoascent = OS2_ASCENT
    font.os2_typodescent = -OS2_DESCENT
    font.os2_winascent = OS2_ASCENT
    font.os2_windescent = OS2_DESCENT
    font.os2_typolinegap = 0

    font.hhea_ascent = OS2_ASCENT
    font.hhea_descent = -OS2_DESCENT
    font.hhea_linegap = 0

    font.os2_xheight = x_height
    font.os2_capheight = cap_height

    if "Regular" == weight or "Italic" == weight:
        font.os2_weight = 400
    elif "Bold" in weight:
        font.os2_weight = 700

    font.sfnt_names = (
        (
            "English (US)",
            "License",
            """This Font Software is licensed under the SIL Open Font License,
Version 1.1. This license is available with a FAQ
at: http://scripts.sil.org/OFL""",
        ),
        ("English (US)", "License URL", "http://scripts.sil.org/OFL"),
        ("English (US)", "Version", VERSION),
    )
    font.familyname = f"{FONT_NAME} {variant}".strip()
    font.fontname = f"{FONT_NAME}{variant}-{weight}".replace(" ", "").strip()
    font.fullname = f"{FONT_NAME} {variant}".strip() + f" {weight}"
    font.os2_vendor = VENDER_NAME
    font.copyright = COPYRIGHT


if __name__ == "__main__":
    main()
