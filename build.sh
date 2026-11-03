#!/bin/sh
# 把 index.html（Artifact 原始檔，無 <head> 骨架）包成完整 HTML，輸出到 docs/ 給 GitHub Pages
set -e
cd "$(dirname "$0")"
mkdir -p docs
{
  printf '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%%}[hidden]{display:none!important}</style>\n'
  printf '</head>\n<body>\n'
  cat index.html
  printf '\n</body>\n</html>\n'
} > docs/index.html
touch docs/.nojekyll
echo "built docs/index.html"
