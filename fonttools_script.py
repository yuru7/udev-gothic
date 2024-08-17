#!/bin/env python3

import configparser
import glob
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools import merge, ttLib, ttx
from ttfautohint import options, ttfautohint

# iniファイルを読み込む
settings = configparser.ConfigParser()
settings.read("build.ini", encoding="utf-8")

FONT_NAME = settings.get("DEFAULT", "FONT_NAME")
FONTFORGE_PREFIX = settings.get("DEFAULT", "FONTFORGE_PREFIX")
FONTTOOLS_PREFIX = settings.get("DEFAULT", "FONTTOOLS_PREFIX")
BUILD_FONTS_DIR = settings.get("DEFAULT", "BUILD_FONTS_DIR")
HALF_WIDTH_12 = int(settings.get("DEFAULT", "HALF_WIDTH_12"))
FULL_WIDTH_35 = int(settings.get("DEFAULT", "FULL_WIDTH_35"))
WIDTH_35_STR = settings.get("DEFAULT", "WIDTH_35_STR")


def main():
    # 第一引数を取得
    # 特定のバリエーションのみを処理するための指定
    specific_variant = sys.argv[1] if len(sys.argv) > 1 else None

    edit_fonts(specific_variant)


def edit_fonts(specific_variant: str):
    """フォントを編集する"""

    if specific_variant is None:
        specific_variant = ""

    # ファイルをパターンで指定
    file_pattern = f"{FONTFORGE_PREFIX}{FONT_NAME}{specific_variant}*-eng.ttf"
    filenames = glob.glob(f"{BUILD_FONTS_DIR}/{file_pattern}")
    # ファイルが見つからない場合はエラー
    if len(filenames) == 0:
        print(f"Error: {file_pattern} not found")
        return
    paths = [Path(f) for f in filenames]
    for path in paths:
        print(f"edit {str(path)}")
        style = path.stem.split("-")[1]
        variant = path.stem.split("-")[0].replace(f"{FONTFORGE_PREFIX}{FONT_NAME}", "")
        add_hinting(str(path), str(path).replace(".ttf", "-hinted.ttf"))
        merge_fonts(style, variant)
        fix_font_tables(style, variant)

    # 一時ファイルを削除
    # スタイル部分以降はワイルドカードで指定
    for filename in glob.glob(
        f"{BUILD_FONTS_DIR}/{FONTTOOLS_PREFIX}{FONT_NAME}{specific_variant}*"
    ):
        os.remove(filename)
    for filename in glob.glob(
        f"{BUILD_FONTS_DIR}/{FONTFORGE_PREFIX}{FONT_NAME}{specific_variant}*"
    ):
        os.remove(filename)


def add_hinting(input_font_path, output_font_path):
    """フォントにヒンティングを付ける"""
    args = [
        "-l",
        "6",
        "-r",
        "45",
        "-D",
        "latn",
        "-f",
        "none",
        "-S",
        "-W",
        "-X",
        "14-",
        "-x",
        "0",
        "-I",
        input_font_path,
        output_font_path,
    ]
    options_ = options.parse_args(args)
    print("exec hinting", options_)
    ttfautohint(**options_)


def merge_fonts(style, variant):
    """フォントを結合する"""
    eng_font_path = f"{BUILD_FONTS_DIR}/{FONTFORGE_PREFIX}{FONT_NAME}{variant}-{style}-eng-hinted.ttf"
    jp_font_path = (
        f"{BUILD_FONTS_DIR}/{FONTFORGE_PREFIX}{FONT_NAME}{variant}-{style}-jp.ttf"
    )
    # vhea, vmtxテーブルを削除
    jp_font_object = ttLib.TTFont(jp_font_path)
    if "vhea" in jp_font_object:
        del jp_font_object["vhea"]
    if "vmtx" in jp_font_object:
        del jp_font_object["vmtx"]
    jp_font_object.save(jp_font_path)
    # フォントを結合
    merger = merge.Merger()
    merged_font = merger.merge([eng_font_path, jp_font_path])
    merged_font.save(
        f"{BUILD_FONTS_DIR}/{FONTTOOLS_PREFIX}{FONT_NAME}{variant}-{style}_merged.ttf"
    )


def fix_font_tables(style, variant):
    """フォントテーブルを編集する"""

    input_font_name = f"{FONTTOOLS_PREFIX}{FONT_NAME}{variant}-{style}_merged.ttf"
    output_name_base = f"{FONTTOOLS_PREFIX}{FONT_NAME}{variant}-{style}"
    completed_name_base = f"{FONT_NAME.replace(' ', '')}{variant}-{style}"

    # OS/2, post テーブルのみのttxファイルを出力
    xml = dump_ttx(input_font_name, output_name_base)
    # OS/2 テーブルを編集
    fix_os2_table(xml, style, flag_35=WIDTH_35_STR in variant)
    # post テーブルを編集
    fix_post_table(xml, flag_35=WIDTH_35_STR in variant)
    # cmap テーブルを編集
    fix_cmap_table(xml, style, variant)

    # ttxファイルを上書き保存
    xml.write(
        f"{BUILD_FONTS_DIR}/{output_name_base}.ttx",
        encoding="utf-8",
        xml_declaration=True,
    )

    # ttxファイルをttfファイルに適用
    ttx.main(
        [
            "-o",
            f"{BUILD_FONTS_DIR}/{output_name_base}_os2_post.ttf",
            "-m",
            f"{BUILD_FONTS_DIR}/{input_font_name}",
            f"{BUILD_FONTS_DIR}/{output_name_base}.ttx",
        ]
    )

    # ファイル名を変更
    os.rename(
        f"{BUILD_FONTS_DIR}/{output_name_base}_os2_post.ttf",
        f"{BUILD_FONTS_DIR}/{completed_name_base}.ttf",
    )


def dump_ttx(input_name_base, output_name_base) -> ET:
    """OS/2, post テーブルのみのttxファイルを出力"""
    ttx.main(
        [
            "-t",
            "OS/2",
            "-t",
            "post",
            "-t",
            "cmap",
            "-f",
            "-o",
            f"{BUILD_FONTS_DIR}/{output_name_base}.ttx",
            f"{BUILD_FONTS_DIR}/{input_name_base}",
        ]
    )

    return ET.parse(f"{BUILD_FONTS_DIR}/{output_name_base}.ttx")


def fix_os2_table(xml: ET, style: str, flag_35: bool = False):
    """OS/2 テーブルを編集する"""
    # xAvgCharWidthを編集
    # タグ形式: <xAvgCharWidth value="1000"/>
    if flag_35:
        x_avg_char_width = FULL_WIDTH_35
    else:
        x_avg_char_width = HALF_WIDTH_12
    xml.find("OS_2/xAvgCharWidth").set("value", str(x_avg_char_width))

    # fsSelectionを編集
    # タグ形式: <fsSelection value="00000000 11000000" />
    # スタイルに応じたビットを立てる
    fs_selection = None
    if style == "Regular":
        fs_selection = "00000001 01000000"
    elif style == "Italic":
        fs_selection = "00000001 00000001"
    elif style == "Bold":
        fs_selection = "00000001 00100000"
    elif style == "BoldItalic":
        fs_selection = "00000001 00100001"

    if fs_selection is not None:
        xml.find("OS_2/fsSelection").set("value", fs_selection)

    # panoseを編集
    # タグ形式:
    # <panose>
    #   <bFamilyType value="2" />
    #   <bSerifStyle value="11" />
    #   <bWeight value="6" />
    #   <bProportion value="9" />
    #   <bContrast value="6" />
    #   <bStrokeVariation value="3" />
    #   <bArmStyle value="0" />
    #   <bLetterForm value="2" />
    #   <bMidline value="0" />
    #   <bXHeight value="4" />
    # </panose>
    if style == "Regular" or style == "Italic":
        bWeight = 5
    else:
        bWeight = 8
    if flag_35:
        panose = {
            "bFamilyType": 2,
            "bSerifStyle": 11,
            "bWeight": bWeight,
            "bProportion": 3,
            "bContrast": 2,
            "bStrokeVariation": 2,
            "bArmStyle": 3,
            "bLetterForm": 2,
            "bMidline": 2,
            "bXHeight": 7,
        }
    else:
        panose = {
            "bFamilyType": 2,
            "bSerifStyle": 11,
            "bWeight": bWeight,
            "bProportion": 9,
            "bContrast": 2,
            "bStrokeVariation": 2,
            "bArmStyle": 3,
            "bLetterForm": 2,
            "bMidline": 2,
            "bXHeight": 7,
        }

    for key, value in panose.items():
        xml.find(f"OS_2/panose/{key}").set("value", str(value))


def fix_post_table(xml: ET, flag_35):
    """post テーブルを編集する"""
    # isFixedPitchを編集
    # タグ形式: <isFixedPitch value="0"/>
    is_fixed_pitch = 0 if flag_35 else 1
    xml.find("post/isFixedPitch").set("value", str(is_fixed_pitch))
    # underlinePosition, underlineThicknessを編集
    # <underlinePosition value="-155"/>
    # <underlineThickness value="50"/>
    # EM 1000 -> 2048 の拡大率に合わせて値を調整
    xml.find("post/underlinePosition").set("value", "-317")
    xml.find("post/underlineThickness").set("value", "102")


def fix_cmap_table(xml: ET, style: str, variant: str):
    """異体字シーケンスを搭載するために cmap テーブルを編集する。
    pyftmerge で結合すると異体字シーケンスを司るテーブル cmap_format_14 が
    消えてしまうため、マージする前の編集済み日本語フォントから該当テーブル情報を取り出して適用する。"""
    # タグ形式:
    # <cmap_format_14 platformID="0" platEncID="5">
    #   <map uv="0x4fae" uvs="0xfe00" name="uniFA30"/>
    #   <map uv="0x50e7" uvs="0xfe00" name="uniFA31"/>
    # </cmap_format_14>
    source_xml = dump_ttx(
        f"{FONTFORGE_PREFIX}{FONT_NAME}{variant}-{style}-jp.ttf",
        f"{FONTFORGE_PREFIX}{FONT_NAME}{variant}-{style}-jp",
    )
    source_cmap_format_14 = source_xml.find("cmap/cmap_format_14")
    target_cmap = xml.find("cmap")
    target_cmap.append(source_cmap_format_14)


if __name__ == "__main__":
    main()
