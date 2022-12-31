#!/bin/bash

BASE_DIR="$(cd $(dirname $0); pwd)/build_tmp"

FAMILYNAME="$1"
PREFIX="$2"

FONT_PATTERN=${PREFIX}${FAMILYNAME}'*.ttf'

COPYRIGHT='[BIZ UDGothic]
Copyright 2022 The BIZ UDGothic Project Authors (https://github.com/googlefonts/morisawa-biz-ud-gothic)

[JetBrains Mono]
Copyright 2020 The JetBrains Mono Project Authors (https://github.com/JetBrains/JetBrainsMono)

[Nerd Fonts]
Copyright (c) 2014, Ryan L McIntyre (https://ryanlmcintyre.com).

[UDEV Gothic]
Copyright (c) 2022, Yuko Otawara'

for P in ${BASE_DIR}/${FONT_PATTERN}
do
  ttx -t name -t post "$P"
  mv "${P%%.ttf}.ttx" ${BASE_DIR}/tmp.ttx
  cat ${BASE_DIR}/tmp.ttx | perl -pe "s?###COPYRIGHT###?$COPYRIGHT?" > "${P%%.ttf}.ttx"

  mv "$P" "${P}_orig"
  ttx -m "${P}_orig" "${P%%.ttf}.ttx"
done

rm -f "${BASE_DIR}/"*.ttx
