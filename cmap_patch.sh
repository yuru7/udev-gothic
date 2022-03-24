#!/bin/bash

# 異体字シーケンス用のパッチ。
# pyftmerge後にはGlyphIDが変わってしまうことから、機械的にcmapを復元させることが難しい。

BASE_DIR="$(cd $(dirname $0); pwd)"
BUILD_TMP_DIR="${BASE_DIR}/build_tmp"

FAMILYNAME="$1"
PREFIX="$2"

FONT_PATTERN=${PREFIX}${FAMILYNAME}'[^3]*.ttf'
FONT35_PATTERN=${PREFIX}${FAMILYNAME}35'*.ttf'

CMAP_MASTER="${BASE_DIR}/source/cmap_format_14_master"
TMP_CMAP_MASTER='tmp_cmap_format_14_master'
TMP_TTX='tmp_cmap_format_14'

CMAP_MASTER_XML="${BASE_DIR}/source/cmap_format_14.xml"

GENERATED_CMAP="${BUILD_TMP_DIR}/gen_cmap"

function buildCmap() {
  ttx_path="$1"
  # cmapマスタの作成
  # (
  #   awk 'NR > 1 {print}' "$CMAP_MASTER" | while read line
  #   do
  #     out_name=$(echo "$line" | awk -F, '{print $4}')
  #     grep_out_name=$(egrep -m1 "name=\"${out_name}[#\"]" "$ttx_path" | perl -pe 's/^.+name="([^"]+?)".+/$1/')
  #     if [ -z "$grep_out_name" ]; then
  #       continue
  #     fi
  #     echo "$line" | awk -F, '{print $1 "," $2 "," $3 "," "'$grep_out_name'"}'
  #   done
  # ) > "$TMP_CMAP_MASTER"

  # 追加するcmapタグを一時ファイルに書き出し
  # awk -F, '
  #   BEGIN {print "<cmap_format_14 platformID=\"0\" platEncID=\"5\">"}
  #   NR > 1 && $4 != "" {print "<map uv=\"" $1 "\" uvs=\"" $3 "\" name=\"" $4 "\"/>"}
  #   END {print "</cmap_format_14></cmap>"}
  # ' "$TMP_CMAP_MASTER" > "$TMP_TTX"

  # 適用するttxファイルを作成
  (
    egrep -v 'cmap_format_14| uvs=' "$ttx_path" | awk '/<\/cmap>/ {exit} {print}'
    cat "$CMAP_MASTER_XML" | egrep 'cmap_format_14|name='
    echo '</cmap>'
    awk 'BEGIN {prFlag = 0} /<post>/ {prFlag = 1} prFlag == 1 {print}' "$ttx_path"
  ) > $GENERATED_CMAP
}

function proc() {
  font="$1"

  if [ ! -f "$font" ]; then
    echo "File not found: $font"
    return
  fi

  ttx -t cmap -t post $font
  mv ${font} ${font}_orig
  buildCmap "${font%%.ttf}.ttx"
  ttx -o ${font} -m ${font}_orig $GENERATED_CMAP
}

echo '### Start cmap_patch ###'

for f in ${BUILD_TMP_DIR}/${FONT_PATTERN}; do
  proc "$f"
done

# for f in $(ls ${BUILD_TMP_DIR}/${FONT35_PATTERN}); do
#   proc "$f"
# done

#rm -f "${BUILD_TMP_DIR}/"*.ttx
