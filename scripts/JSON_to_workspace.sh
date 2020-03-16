#!/usr/bin/env bash

set -e

function JSON_to_workspace() {
  # 1: the analysis name
  # 2: the url of the JSON workspaces
  # 3: the background only workspace
  # 4: the signal workspace patch
  # 5: the patched background + signal workspace
  local ANALYSIS_NAME=$1
  local HEPDATA_URL=$2
  local BACKGROUND_ONLY=$3
  local SIGNAL_PATCH=$4
  local JSON_WORKSPACE=$5

  if [[ ! -d "${ANALYSIS_NAME}" ]]; then
    mkdir "${ANALYSIS_NAME}"
  fi

  # Download from HEPData
  curl -sL -o "${ANALYSIS_NAME}/workspaces.tar.gz" "${HEPDATA_URL}"
  # Unpack tarball
  if [[ ! -d "${ANALYSIS_NAME}/workspaces" ]]; then
    mkdir "${ANALYSIS_NAME}/workspaces"
  fi
  tar xvzf "${ANALYSIS_NAME}/workspaces.tar.gz" -C "${ANALYSIS_NAME}/workspaces"

  # Create a full signal+background workspace
  jsonpatch \
    "${ANALYSIS_NAME}/workspaces/${BACKGROUND_ONLY}" \
    "${ANALYSIS_NAME}/workspaces/${SIGNAL_PATCH}" > \
    "${ANALYSIS_NAME}/workspaces/${JSON_WORKSPACE}"

  # Convert to ROOT + XML
  if [[ -d "${ANALYSIS_NAME}/xml" ]]; then
    rm -rf "${ANALYSIS_NAME}/xml"
  fi
  mkdir "${ANALYSIS_NAME}/xml"
  pyhf json2xml \
    --output-dir "${ANALYSIS_NAME}/xml" \
    "${ANALYSIS_NAME}/workspaces/${JSON_WORKSPACE}"

  # Generate ROOT workspace
  hist2workspace "${ANALYSIS_NAME}/xml"/FitConfig.xml
}

function main() {
  # 1: the analysis name
  # 2: the url of the JSON workspaces
  # 3: the background only workspace
  # 4: the signal workspace patch
  # 5: the patched background + signal workspace
  local ANALYSIS_NAME=$1
  local HEPDATA_URL=$2
  local BACKGROUND_ONLY=$3
  local SIGNAL_PATCH=$4
  local JSON_WORKSPACE=$5

  JSON_to_workspace "${ANALYSIS_NAME}" "${HEPDATA_URL}" "${BACKGROUND_ONLY}" "${SIGNAL_PATCH}" "${JSON_WORKSPACE}"
}

main "$@" || exit 1
