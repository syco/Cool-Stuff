#!/bin/bash

for x in "plugin.video.italy-tv" "plugin.video.uk-tv" "script.module.streamlink"; do
  rm -Rf ${x}*
  curl -s -L https://github.com/syco/${x}/archive/master.zip > ${x}.zip
  unzip ${x}.zip
  mv ${x}-master ${x}
  rm -f ${x}.zip
done
python3 _repo_xml_generator.py
for x in "plugin.video.italy-tv" "plugin.video.uk-tv" "script.module.streamlink"; do
  rm -Rf ${x}*
done

