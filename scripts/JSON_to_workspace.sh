#!/usr/bin/env bash

set -e

function JSON_to_workspace() {
  # 1: the analysis pallet name
  # 2: the url of the JSON workspaces
  # 3: the background only workspace
  # 4: the name of the signal patch
  # 5: the patched background + signal workspace
  local PALLET_NAME=$1
  local HEPDATA_URL=$2
  local BACKGROUND_ONLY=$3
  local PATCH_NAME=$4
  local JSON_WORKSPACE=$5

  # Download from HEPData
  pyhf contrib download "${HEPDATA_URL}" "${PALLET_NAME}"

  # Create a full signal+background workspace
  workspace_dir="${BACKGROUND_ONLY%/*}"
  pyhf patchset extract \
    --name "${PATCH_NAME}" \
    --output-file "${PALLET_NAME}/${workspace_dir}/${PATCH_NAME}.json" \
    "${PALLET_NAME}/${workspace_dir}/patchset.json"
  jsonpatch \
    "${PALLET_NAME}/${BACKGROUND_ONLY}" \
    "${PALLET_NAME}/${workspace_dir}/${PATCH_NAME}.json" > \
    "${PALLET_NAME}/${JSON_WORKSPACE}"

  # Convert to ROOT + XML
  if [[ -d "${PALLET_NAME}/xml" ]]; then
    rm -rf "${PALLET_NAME}/xml"
  fi
  mkdir "${PALLET_NAME}/xml"
  pyhf json2xml \
    --output-dir "${PALLET_NAME}/xml" \
    "${PALLET_NAME}/${JSON_WORKSPACE}"

  # Generate ROOT workspace
  hist2workspace "${PALLET_NAME}/xml/FitConfig.xml"
}

function main() {
  # 1: the analysis pallet name
  # 2: the url of the JSON workspaces
  # 3: the background only workspace
  # 4: the name of the signal patch
  # 5: the patched background + signal workspace
  local PALLET_NAME=$1
  local HEPDATA_URL=$2
  local BACKGROUND_ONLY=$3
  local PATCH_NAME=$4
  local JSON_WORKSPACE=$5

  JSON_to_workspace "${PALLET_NAME}" "${HEPDATA_URL}" "${BACKGROUND_ONLY}" "${PATCH_NAME}" "${JSON_WORKSPACE}"
}

main "$@" || exit 1
