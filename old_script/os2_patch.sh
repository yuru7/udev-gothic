#!/bin/bash

BASE_DIR="$(cd $(dirname $0); pwd)/build_tmp"

FAMILYNAME="$1"
PREFIX="$2"
W35_FLAG="$3"

xAvgCharWidth_SETVAL=1024
FONT_PATTERN=${PREFIX}${FAMILYNAME}'*.ttf'

if [ $W35_FLAG -eq 1 ]
then
  xAvgCharWidth_SETVAL=2045
fi

for P in ${BASE_DIR}/${FONT_PATTERN}
do
  ttx -t OS/2 -t post "$P"

  xAvgCharWidth_value=$(grep xAvgCharWidth "${P%%.ttf}.ttx" | awk -F\" '{print $2}')
  sed -i.bak -e 's,xAvgCharWidth value="'$xAvgCharWidth_value'",xAvgCharWidth value="'${xAvgCharWidth_SETVAL}'",' "${P%%.ttf}.ttx"

  fsSelection_value=$(grep fsSelection "${P%%.ttf}.ttx" | awk -F\" '{print $2}')
  if [ `echo $P | grep Regular` ]; then
    fsSelection_sed_value='00000001 01000000'
  elif [ `echo $P | grep BoldItalic` ]; then
    fsSelection_sed_value='00000001 00100001'
  elif [ `echo $P | grep Bold` ]; then
    fsSelection_sed_value='00000001 00100000'
  elif [ `echo $P | grep Italic` ]; then
    fsSelection_sed_value='00000001 00000001'
  else
    fsSelection_sed_value='00000001 00000000'
  fi
  sed -i.bak -e 's,fsSelection value="'"$fsSelection_value"'",fsSelection value="'"$fsSelection_sed_value"'",' "${P%%.ttf}.ttx"

  underlinePosition_value=$(grep 'underlinePosition value' "${P%%.ttf}.ttx" | awk -F\" '{print $2}')
  sed -i.bak -e 's,underlinePosition value="'$underlinePosition_value'",underlinePosition value="-70",' "${P%%.ttf}.ttx"

  sed -i.bak -e 's,<isFixedPitch value="0"/>,<isFixedPitch value="1"/>,' "${P%%.ttf}.ttx"

  mv "$P" "${P}_orig"
  ttx -m "${P}_orig" "${P%%.ttf}.ttx"
done

rm -f "${BASE_DIR}/"*.ttx
