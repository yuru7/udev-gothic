#!/bin/bash

BASE_DIR=$(cd $(dirname $0); pwd)

WORK_DIR="$BASE_DIR/build_tmp"
if [ ! -d "$WORK_DIR" ]
then
  mkdir "$WORK_DIR"
fi

LIGA_FLAG="$1"
VERSION="$2"
FAMILYNAME="$3"
DISP_FAMILYNAME="$4"
DISP_FAMILYNAME_JP="UDEV ゴシック"

COPYRIGHT="Copyright (c) 2022, Yuko OTAWARA"

EM_ASCENT=1802
EM_DESCENT=246
EM=$(($EM_ASCENT + $EM_DESCENT))

ASCENT=$(($EM_ASCENT + 143))
DESCENT=$(($EM_DESCENT + 134))
TYPO_LINE_GAP=0

HALF_WIDTH=$(($EM / 2))

SHRINK_X=88
SHRINK_Y=100

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

MODIFIED_FONT_JBMONO_REGULAR='modified_jbmono_regular.sfd'
MODIFIED_FONT_JBMONO_BOLD='modified_jbmono_bold.sfd'

if [ -z "$SRC_FONT_JBMONO_REGULAR" -o \
-z "$SRC_FONT_JBMONO_BOLD" -o \
-z "$SRC_FONT_BIZUD_REGULAR" -o \
-z "$SRC_FONT_BIZUD_BOLD" ]
then
  echo 'ソースフォントファイルが存在しない'
  exit 1
fi

GEN_SCRIPT_JBMONO='gen_script_jbmono.pe'

# JetBrains Monoの調整
cat > "${WORK_DIR}/${GEN_SCRIPT_JBMONO}" << _EOT_

# Set parameters
input_list = ["${PATH_JBMONO_REGULAR}", \\
  "${PATH_JBMONO_BOLD}"]
output_list = ["${MODIFIED_FONT_JBMONO_REGULAR}", \\
  "${MODIFIED_FONT_JBMONO_BOLD}"]
fontstyle_list    = ["Regular", "Bold"]
fontweight_list = [400, 700]
panoseweight_list = [5, 8]

i = 0
while (i < SizeOf(input_list))
  # フォントファイルを開く
  Print("Open " + input_list[i])
  Open(input_list[i])

  # サイズ調整
  SelectWorthOutputting()
  #UnlinkReference()
  ScaleToEm(${EM_ASCENT}, ${EM_DESCENT})
  Scale(${SHRINK_X}, ${SHRINK_Y}, 0, 0)

  # 半角スペースから幅を取得
  Select(0u0020)
  glyphWidth = GlyphInfo("Width")

  # 幅の調整
  SelectWorthOutputting()
  move_x = (${HALF_WIDTH} - glyphWidth) / 2
  width = ${HALF_WIDTH}
  Move(move_x, 0)
  SetWidth(width, 0)

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
  SetPanose([2, 11, panoseweight_list[i], 9, 2, 2, 3, 2, 2, 7])

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

pyftmerge "${WORK_DIR}/${FAMILYNAME}-Regular.ttf_hinted" "${WORK_DIR}/${SRC_FONT_BIZUD_REGULAR%%.ttf}.subset.ttf"
mv -f merged.ttf "${WORK_DIR}/${FAMILYNAME}-Regular.ttf"
pyftmerge "${WORK_DIR}/${FAMILYNAME}-Bold.ttf_hinted" "${WORK_DIR}/${SRC_FONT_BIZUD_BOLD%%.ttf}.subset.ttf"
mv -f merged.ttf "${WORK_DIR}/${FAMILYNAME}-Bold.ttf"
