#!/bin/bash

BASE_DIR=$(cd $(dirname $0); pwd)

WORK_DIR="$BASE_DIR/build_tmp"
if [ ! -d "$WORK_DIR" ]
then
  mkdir "$WORK_DIR"
fi

VERSION="$1"
FAMILYNAME="$2"
DISP_FAMILYNAME="$3"
DISP_FAMILYNAME_JP="UDEV ゴシック"
LIGA_FLAG="$4"  # 0: リガチャなし 1: リガチャあり
JPDOC_FLAG="$5"  # 0: JetBrains Monoの記号優先 1: 日本語ドキュメントで使用頻度の高い記号はBIZ UDゴシック優先
NERD_FONTS_FLAG="$6"  # 0: Nerd Fonts なし 1: Nerd Fonts あり
W35_FLAG="$7"  # 0: 通常幅 1: 半角3:全角5幅

COPYRIGHT="Copyright (c) 2022, Yuko OTAWARA"

EM_ASCENT=1802
EM_DESCENT=246
EM=$(($EM_ASCENT + $EM_DESCENT))

ASCENT=$(($EM_ASCENT + 143))
DESCENT=$(($EM_DESCENT + 134))
TYPO_LINE_GAP=0

HALF_WIDTH=$(($EM / 2))
SHRINK_X=90
SHRINK_Y=99

if [ $W35_FLAG -eq 1 ]
then
  HALF_WIDTH=1227
  FULL_WIDTH=$(($HALF_WIDTH / 3 * 5))
  SHRINK_X=100
  SHRINK_Y=100
fi

FONTS_DIRECTORIES="${BASE_DIR}/source/"

SRC_FONT_JBMONO_REGULAR='JetBrainsMonoNL-Regular.ttf'
SRC_FONT_JBMONO_BOLD='JetBrainsMonoNL-Bold.ttf'
if [ "$LIGA_FLAG" == 1 ]
then
  SRC_FONT_JBMONO_REGULAR='JetBrainsMono-Regular.ttf'
  SRC_FONT_JBMONO_BOLD='JetBrainsMono-Bold.ttf'
fi
SRC_FONT_BIZUD_REGULAR='fontforge_export_BIZUDGothic-Regular.ttf'
SRC_FONT_BIZUD_BOLD='fontforge_export_BIZUDGothic-Bold.ttf'

PATH_JBMONO_REGULAR=`find $FONTS_DIRECTORIES -follow -name "$SRC_FONT_JBMONO_REGULAR"`
PATH_JBMONO_BOLD=`find $FONTS_DIRECTORIES -follow -name "$SRC_FONT_JBMONO_BOLD"`
PATH_BIZUD_REGULAR=`find $FONTS_DIRECTORIES -follow -name "$SRC_FONT_BIZUD_REGULAR"`
PATH_BIZUD_BOLD=`find $FONTS_DIRECTORIES -follow -name "$SRC_FONT_BIZUD_BOLD"`
PATH_IDEOGRAPHIC_SPACE=`find $FONTS_DIRECTORIES -follow -name 'ideographic_space.sfd'`
PATH_ZERO_REGULAR=`find $FONTS_DIRECTORIES -follow -name 'zero-Regular.sfd'`
PATH_ZERO_BOLD=`find $FONTS_DIRECTORIES -follow -name 'zero-Bold.sfd'`
PATH_NERD_FONTS=`find $FONTS_DIRECTORIES -follow -name 'JetBrains Mono Regular Nerd Font Complete.ttf'`

MODIFIED_FONT_JBMONO_REGULAR='modified_jbmono_regular.sfd'
MODIFIED_FONT_JBMONO_BOLD='modified_jbmono_bold.sfd'
MODIFIED_FONT_NERD_FONTS_REGULAR='tmp_nerd_fonts_regular.ttf'
MODIFIED_FONT_NERD_FONTS_BOLD='tmp_nerd_fonts_bold.ttf'
MODIFIED_FONT_BIZUD35_REGULAR='tmp_bizud_regular.ttf'
MODIFIED_FONT_BIZUD35_BOLD='tmp_bizud_bold.ttf'

if [ -z "$SRC_FONT_JBMONO_REGULAR" -o \
-z "$SRC_FONT_JBMONO_BOLD" -o \
-z "$SRC_FONT_BIZUD_REGULAR" -o \
-z "$SRC_FONT_BIZUD_BOLD" ]
then
  echo 'ソースフォントファイルが存在しない'
  exit 1
fi

GEN_SCRIPT_JBMONO='gen_script_jbmono.pe'

NERD_ICON_LIST='
# Powerline フォント -> JetBrains Mono標準のものを使用する
#SelectMore(0ue0a0, 0ue0a2)
#SelectMore(0ue0b0, 0ue0b3)
# 拡張版 Powerline フォント
SelectMore(0ue0a3)
SelectMore(0ue0b4, 0ue0c8)
SelectMore(0ue0ca)
SelectMore(0ue0cc, 0ue0d2)
SelectMore(0ue0d4)
# IEC Power Symbols
SelectMore(0u23fb, 0u23fe)
SelectMore(0u2b58)
# Octicons
SelectMore(0u2665)
SelectMore(0u26A1)
SelectMore(0uf27c)
SelectMore(0uf400, 0uf4a9)
# Font Awesome Extension
SelectMore(0ue200, 0ue2a9)
# Weather
SelectMore(0ue300, 0ue3e3)
# Seti-UI + Custom
SelectMore(0ue5fa, 0ue62e)
# Devicons
SelectMore(0ue700, 0ue7c5)
# Font Awesome
SelectMore(0uf000, 0uf2e0)
# Font Logos (Formerly Font Linux)
SelectMore(0uf300, 0uf31c)
# Material Design Icons
SelectMore(0uf500, 0ufd46)
# Pomicons -> 商用不可のため除外
SelectFewer(0ue000, 0ue00d)
'

# JetBrains Monoの調整
cat > "${WORK_DIR}/${GEN_SCRIPT_JBMONO}" << _EOT_

# Set parameters
input_list = ["${PATH_JBMONO_REGULAR}", \\
  "${PATH_JBMONO_BOLD}"]
output_list = ["${MODIFIED_FONT_JBMONO_REGULAR}", \\
  "${MODIFIED_FONT_JBMONO_BOLD}"]
zero_list = ["${PATH_ZERO_REGULAR}", \\
  "${PATH_ZERO_BOLD}"]
fontstyle_list    = ["Regular", "Bold"]
fontweight_list = [400, 700]
panoseweight_list = [5, 8]

i = 0
while (i < SizeOf(input_list))
  # フォントファイルを開く
  Print("Open " + input_list[i])
  Open(input_list[i])

  # 0 をスラッシュゼロにする
  Select(0u0030); Clear()
  MergeFonts(zero_list[i])

  # サイズ調整
  SelectWorthOutputting()
  UnlinkReference()
  ScaleToEm(${EM_ASCENT}, ${EM_DESCENT})
  if (${W35_FLAG} == 0)
    Scale(${SHRINK_X}, ${SHRINK_Y}, 0, 0)
  endif

  # 半角スペースから幅を取得
  Select(0u0020)
  glyphWidth = GlyphInfo("Width")

  # 幅の調整
  SelectWorthOutputting()
  move_x = (${HALF_WIDTH} - glyphWidth) / 2
  Move(move_x, 0)
  SetWidth(${HALF_WIDTH}, 0)

  # JPDOC版では、日本語ドキュメントで使用頻度の高い記号はBIZ UDゴシックを優先して適用する
  if ($JPDOC_FLAG == 1)
    Select(0u00F7) # ÷
    SelectMore(0u00D7) # ×
    SelectMore(0u21D2) # ⇒
    SelectMore(0u21D4) # ⇔
    SelectMore(0u21E7, 0u21E8) # ⇧-⇨
    SelectMore(0u25A0, 0u25A1) # ■-□
    SelectMore(0u25B2, 0u25B3) # ▲-△
    SelectMore(0u25B6, 0u25B7) # ▶-▷
    SelectMore(0u25BC, 0u25BD) # ▼-▽
    SelectMore(0u25C0, 0u25C1) # ◀-◁
    SelectMore(0u25C6, 0u25C7) # ◆-◇
    SelectMore(0u25CE, 0u25CF) # ◎-●
    SelectMore(0u25EF) # ◯
    SelectMore(0u221A) # √
    SelectMore(0u221E) # ∞
    SelectMore(0u2010, 0u2022) # ‐-•
    SelectMore(0u2026) # …
    SelectMore(0u2190, 0u2194) # ←-↔
    SelectMore(0u2196, 0u2199) # ↖-↙
    SelectMore(0u2200) # ∀
    SelectMore(0u2202, 0u2203) # ∂-∃
    SelectMore(0u2208, 0u220C) # ∈-∌
    SelectMore(0u2211, 0u2212) # ∑-−
    SelectMore(0u2225, 0u222B) # ∥-∫
    SelectMore(0u2260, 0u2262) # ≠-≢
    SelectMore(0u2282, 0u2287) # ⊂-⊇
    Clear()
  endif

  # パスの小数点以下を切り捨て
  SelectWorthOutputting()
  RoundToInt()

  # 修正後のフォントファイルを保存
  Print("Save " + output_list[i])
  Save("${WORK_DIR}/" + output_list[i])
  Close()

  # 出力フォントファイルの作成
  New()
  Reencode("unicode")
  ScaleToEm(${EM_ASCENT}, ${EM_DESCENT})

  MergeFonts("${PATH_IDEOGRAPHIC_SPACE}")
  MergeFonts("${WORK_DIR}/" + output_list[i])

  Print("Save " + output_list[i])
  SetOS2Value("Weight", fontweight_list[i]) # Book or Bold
  SetOS2Value("Width",                   5) # Medium
  SetOS2Value("FSType",                  0)
  SetOS2Value("VendorID",           "twr")
  SetOS2Value("IBMFamily",            2057) # SS Typewriter Gothic
  SetOS2Value("WinAscentIsOffset",       0)
  SetOS2Value("WinDescentIsOffset",      0)
  SetOS2Value("TypoAscentIsOffset",      0)
  SetOS2Value("TypoDescentIsOffset",     0)
  SetOS2Value("HHeadAscentIsOffset",     0)
  SetOS2Value("HHeadDescentIsOffset",    0)
  SetOS2Value("WinAscent",             ${ASCENT})
  SetOS2Value("WinDescent",            ${DESCENT})
  SetOS2Value("TypoAscent",            ${ASCENT})
  SetOS2Value("TypoDescent",          -${DESCENT})
  SetOS2Value("TypoLineGap",           ${TYPO_LINE_GAP})
  SetOS2Value("HHeadAscent",           ${ASCENT})
  SetOS2Value("HHeadDescent",         -${DESCENT})
  SetOS2Value("HHeadLineGap",            0)
  if (${W35_FLAG} == 0)
    SetPanose([2, 11, panoseweight_list[i], 9, 2, 2, 3, 2, 2, 7])
  else
    SetPanose([2, 11, panoseweight_list[i], 3, 2, 2, 3, 2, 2, 7])
  endif

  fontfamily = "$FAMILYNAME"
  disp_fontfamily = "$DISP_FAMILYNAME"
  fontname_style = fontstyle_list[i]
  base_style = fontstyle_list[i]
  copyright = "$COPYRIGHT"
  version = "$VERSION"

  SetFontNames(fontfamily + "-" + fontname_style, \\
    disp_fontfamily, \\
    disp_fontfamily + " " + fontstyle_list[i], \\
    base_style, \\
    copyright, version)

  # TTF名設定 - 英語
  SetTTFName(0x409, 2, fontstyle_list[i])
  SetTTFName(0x409, 3, "FontForge 2.0 : " + \$fullname + " : " + Strftime("%d-%m-%Y", 0))
  # TTF名設定 - 日本語
  # SetTTFName(0x411, 1, "${DISP_FAMILYNAME_JP}")
  # SetTTFName(0x411, 2, fontstyle_list[i])
  # SetTTFName(0x411, 3, "FontForge 2.0 : " + \$fullname + " : " + Strftime("%d-%m-%Y", 0))
  # SetTTFName(0x411, 4, "${DISP_FAMILYNAME_JP}" + " " + fontstyle_list[i])

  #Generate("${WORK_DIR}/" + output_list[i], '')
  Generate("${WORK_DIR}/" + fontfamily + "-" + fontname_style + ".ttf", "")
  Close()

  i += 1
endloop

# Nerd Fonts グリフの準備
if (${NERD_FONTS_FLAG} == 1)
  input_list = ["${PATH_BIZUD_REGULAR}", \\
    "${PATH_BIZUD_BOLD}"]
  output_list = ["${MODIFIED_FONT_NERD_FONTS_REGULAR}", \\
    "${MODIFIED_FONT_NERD_FONTS_BOLD}"]

  i = 0
  while (i < SizeOf(input_list))
    Open("$PATH_NERD_FONTS")

    # 必要なグリフのみ残し、残りを削除
    SelectNone()
    $NERD_ICON_LIST
    # 選択していない箇所を選択して削除する
    SelectInvert(); Clear()

    lookups = GetLookups("GSUB"); numlookups = SizeOf(lookups); j = 0;
    while (j < numlookups)
      RemoveLookup(lookups[j]); j++
    endloop
    lookups = GetLookups("GPOS"); numlookups = SizeOf(lookups); j = 0;
    while (j < numlookups)
      RemoveLookup(lookups[j]); j++
    endloop

    # サイズ調整
    SelectWorthOutputting()
    ScaleToEm(${EM_ASCENT}, ${EM_DESCENT})
    if (${W35_FLAG} == 0)
      Scale(${SHRINK_X}, ${SHRINK_Y}, 0, 0)
    endif
    SetWidth(${HALF_WIDTH}, 0)

    MergeFonts(input_list[i])
    if (${W35_FLAG} == 1)
      SelectNone()
      $NERD_ICON_LIST
      SelectInvert()
      move_x = ${FULL_WIDTH} - 2048
      Move(move_x, 0)
    endif

    # 高さ調整
    SetOS2Value("WinAscentIsOffset",       0)
    SetOS2Value("WinDescentIsOffset",      0)
    SetOS2Value("TypoAscentIsOffset",      0)
    SetOS2Value("TypoDescentIsOffset",     0)
    SetOS2Value("HHeadAscentIsOffset",     0)
    SetOS2Value("HHeadDescentIsOffset",    0)
    SetOS2Value("WinAscent",             ${ASCENT})
    SetOS2Value("WinDescent",            ${DESCENT})
    SetOS2Value("TypoAscent",            ${ASCENT})
    SetOS2Value("TypoDescent",          -${DESCENT})
    SetOS2Value("TypoLineGap",           ${TYPO_LINE_GAP})
    SetOS2Value("HHeadAscent",           ${ASCENT})
    SetOS2Value("HHeadDescent",         -${DESCENT})
    SetOS2Value("HHeadLineGap",            0)

    Generate("${WORK_DIR}/" + output_list[i], "")
    Close()

    i += 1
  endloop
elseif (${W35_FLAG} == 1)
  # 35幅版の準備

  input_list = ["${PATH_BIZUD_REGULAR}", \\
    "${PATH_BIZUD_BOLD}"]
  output_list = ["${MODIFIED_FONT_BIZUD35_REGULAR}", \\
    "${MODIFIED_FONT_BIZUD35_BOLD}"]

  i = 0
  while (i < SizeOf(input_list))
    New()
    Reencode("unicode")
    ScaleToEm(${EM_ASCENT}, ${EM_DESCENT})

    MergeFonts(input_list[i])

    # 各グリフの幅調整
    SelectWorthOutputting()
    move_x = ${FULL_WIDTH} - 2048
    Move(move_x, 0)

    # 高さ調整
    SetOS2Value("WinAscentIsOffset",       0)
    SetOS2Value("WinDescentIsOffset",      0)
    SetOS2Value("TypoAscentIsOffset",      0)
    SetOS2Value("TypoDescentIsOffset",     0)
    SetOS2Value("HHeadAscentIsOffset",     0)
    SetOS2Value("HHeadDescentIsOffset",    0)
    SetOS2Value("WinAscent",             ${ASCENT})
    SetOS2Value("WinDescent",            ${DESCENT})
    SetOS2Value("TypoAscent",            ${ASCENT})
    SetOS2Value("TypoDescent",          -${DESCENT})
    SetOS2Value("TypoLineGap",           ${TYPO_LINE_GAP})
    SetOS2Value("HHeadAscent",           ${ASCENT})
    SetOS2Value("HHeadDescent",         -${DESCENT})
    SetOS2Value("HHeadLineGap",            0)

    Generate("${WORK_DIR}/" + output_list[i], "")
    Close()

    i += 1
  endloop
endif
_EOT_

/usr/local/bin/fontforge -script ${WORK_DIR}/${GEN_SCRIPT_JBMONO}

for f in `ls "${WORK_DIR}/${FAMILYNAME}"*.ttf`
do
  ttfautohint -l 6 -r 45 -a nnn -D latn -W -X "13-" -I "$f" "${f}_hinted"
done

# vhea, vmtxテーブル削除
for f in "${PATH_BIZUD_REGULAR}" "${PATH_BIZUD_BOLD}"
do
  cp "$f" "$WORK_DIR"
  target="${WORK_DIR}/${f##*/}"
  pyftsubset "${target}" '*' --drop-tables+=vhea --drop-tables+=vmtx --layout-features='*' --glyph-names --symbol-cmap --legacy-cmap --notdef-glyph --notdef-outline --recommended-glyphs --name-IDs='*' --name-legacy --name-languages='*'
done

if [ $NERD_FONTS_FLAG -eq 1 ]
then
  pyftmerge "${WORK_DIR}/${FAMILYNAME}-Regular.ttf_hinted" "${WORK_DIR}/${MODIFIED_FONT_NERD_FONTS_REGULAR}"
  mv -f merged.ttf "${WORK_DIR}/${FAMILYNAME}-Regular.ttf"

  pyftmerge "${WORK_DIR}/${FAMILYNAME}-Bold.ttf_hinted" "${WORK_DIR}/${MODIFIED_FONT_NERD_FONTS_BOLD}"
  mv -f merged.ttf "${WORK_DIR}/${FAMILYNAME}-Bold.ttf"
elif [ $W35_FLAG -eq 1 ]
then
  pyftmerge "${WORK_DIR}/${FAMILYNAME}-Regular.ttf_hinted" "${WORK_DIR}/${MODIFIED_FONT_BIZUD35_REGULAR}"
  mv -f merged.ttf "${WORK_DIR}/${FAMILYNAME}-Regular.ttf"

  pyftmerge "${WORK_DIR}/${FAMILYNAME}-Bold.ttf_hinted" "${WORK_DIR}/${MODIFIED_FONT_BIZUD35_BOLD}"
  mv -f merged.ttf "${WORK_DIR}/${FAMILYNAME}-Bold.ttf"
else
  pyftmerge "${WORK_DIR}/${FAMILYNAME}-Regular.ttf_hinted" "${WORK_DIR}/${SRC_FONT_BIZUD_REGULAR%%.ttf}.subset.ttf"
  mv -f merged.ttf "${WORK_DIR}/${FAMILYNAME}-Regular.ttf"

  pyftmerge "${WORK_DIR}/${FAMILYNAME}-Bold.ttf_hinted" "${WORK_DIR}/${SRC_FONT_BIZUD_BOLD%%.ttf}.subset.ttf"
  mv -f merged.ttf "${WORK_DIR}/${FAMILYNAME}-Bold.ttf"
fi
