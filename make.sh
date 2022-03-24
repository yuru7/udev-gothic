#!/bin/bash

BASE_DIR=$(cd $(dirname $0); pwd)
WORK_DIR="$BASE_DIR/build_tmp"
BUILD_DIR="$BASE_DIR/build"

VERSION='0.0.3'

FAMILYNAME="UDEVGothic"
DISP_FAMILYNAME="UDEV Gothic"
FAMILYNAME_LIGA="UDEVGothicLG"
DISP_FAMILYNAME_LIGA="UDEV Gothic LG"

# リガチャなし版の生成
"${BASE_DIR}/generator.sh" 0 "$VERSION" "$FAMILYNAME" "$DISP_FAMILYNAME"
"${BASE_DIR}/os2_patch.sh" "$FAMILYNAME"
"${BASE_DIR}/cmap_patch.sh" "$FAMILYNAME"
if [ ! -d "$BUILD_DIR" ]
then
  mkdir "$BUILD_DIR"
fi
mv "$WORK_DIR/$FAMILYNAME"*.ttf "$BUILD_DIR"
rm -rf "$WORK_DIR"

# リガチャあり版の生成
"${BASE_DIR}/generator.sh" 1 "$VERSION" "$FAMILYNAME_LIGA" "$DISP_FAMILYNAME_LIGA"
"${BASE_DIR}/os2_patch.sh" "$FAMILYNAME_LIGA"
"${BASE_DIR}/cmap_patch.sh" "$FAMILYNAME_LIGA"
mv "$WORK_DIR/$FAMILYNAME_LIGA"*.ttf "$BUILD_DIR"
rm -rf "$WORK_DIR"
