#!/usr/bin/env bash
find . -type f -name "*.mid" -print0 | xargs -0 -I {} bash -c 'file="{}"; filename="${file##*/}"; filename_no_ext="${filename%.mid}"; ./title.py "$filename_no_ext"'
