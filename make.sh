#!/bin/bash


BASE_DIR=$(cd $(dirname $0); pwd)
WORK_DIR="$BASE_DIR/build_tmp"
BUILD_DIR="$BASE_DIR/build"

VERSION='0.0.1'
FAMILYNAME="UDEVGothic"

"${BASE_DIR}/generator.sh" $FAMILYNAME $VERSION
"${BASE_DIR}/os2_patch.sh" $FAMILYNAME
"${BASE_DIR}/cmap_patch.sh" $FAMILYNAME

if [ ! -d "$BUILD_DIR" ]
then
  mkdir "$BUILD_DIR"
fi
mv "$WORK_DIR"/UDEVGothic*.ttf "$BUILD_DIR"
rm -rf "$WORK_DIR"
