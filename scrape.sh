#!/bin/bash
#
# Gather OASIS doc tarballs and versions from the website.
#

set -e
set -x

readonly TMPFILE=$(mktemp)
readonly FORGE_BASE="http://forge.ocamlcore.org"
readonly CACHE_DIR="cache"
readonly HTML_DIR="html"
readonly JENKINS_DIST="http://deci.ovh.le-gall.net:8080/job/ocaml-oasis/lastSuccessfulBuild/artifact/dist/"
readonly INC="Makefile.scrape"

clean_exit () {
  if [ -n "$TMPFILE" ] && [ -e "$TMPFILE" ]; then
    rm "$TMPFILE"
  fi
}

trap clean_exit EXIT

rm "$INC" || true

curl -o "$TMPFILE" "$FORGE_BASE/frs/?group_id=54"
URLS=( $(sed "$TMPFILE" -ne "s/.*\(\/frs\/download.php\/[0-9]*\/oasis-[^\"]*\.tar\.gz\)\".*/\1/p") )

mkdir -p "$CACHE_DIR"

forge_download () {
  local URL="$1"
  local DSTFN="$CACHE_DIR/$(basename $URL)"
  if ! [ -e "$DSTFN" ]; then
    curl -o "$DSTFN" "$FORGE_BASE$URL"
  fi
}

extract_version () {
  local PREFIX="$1"
  shift
  echo "$*" | sed -e "s,.*/$PREFIX-\(.*\)\.tar\.gz,\1,"
}

for url in "${URLS[@]}"; do
  case $(basename "$url") in
    oasis-doc-*)
      forge_download $url
      ;;
    oasis-bundle-*)
      true
      ;;
    oasis-*)
      if [ -z "$OASIS_LATEST_URL" ]; then
        OASIS_LATEST_URL="$url"
        OASIS_LATEST_VERSION=$(extract_version "oasis" "$url")
      fi
      ;;
  esac
done

curl -o "$CACHE_DIR/oasis-doc-dev.tar.gz" "$JENKINS_DIST/oasis-doc-dev.tar.gz"

echo "OASIS_LATEST_URL=$OASIS_LATEST_URL" >> "$INC"
echo "OASIS_LATEST_VERSION=$OASIS_LATEST_VERSION" >> "$INC"

OASIS_DOC_VERSIONS=()
for i in $CACHE_DIR/oasis-doc-*.tar.gz ; do
  OASIS_DOC_VERSION=$(extract_version "oasis-doc" $i)
  OASIS_DOC_VERSIONS=( "${OASIS_DOC_VERSIONS[@]}" "$OASIS_DOC_VERSION" )
  tar xzf $(readlink -f "$i") -C "$HTML_DIR"
  DOC_DIR="$HTML_DIR/oasis-doc-$OASIS_DOC_VERSION/doc"
  cp "$DOC_DIR/MANUAL.mkd" $CACHE_DIR/MANUAL-$OASIS_DOC_VERSION.mkd
  echo "$HTML_DIR/MANUAL-$OASIS_DOC_VERSION.html: $CACHE_DIR/MANUAL-$OASIS_DOC_VERSION.mkd" >> "$INC"
  rm -rf "$DOC_DIR"
done
echo "OASIS_DOC_VERSIONS=${OASIS_DOC_VERSIONS[*]}" >> "$INC"
