#!/bin/bash

ROOT_WORKSPACE=$1
PYHF_JSON=$2

# Get the location of this testing script to make other paths relative to it
scriptDir=$(dirname -- "$(readlink -f -- "${BASH_SOURCE[@]}")")

# Test the python script compare_nuisance.py
echo "################## Testing python script compare_nuisance.py with sample input files ##################"
python "${scriptDir}"/../scripts/compare_nuisance.py \
  --root-workspace "${ROOT_WORKSPACE}" \
  --pyhf-json "${PYHF_JSON}" \
#  | tee compare_nuisance_output.txt

echo "#######################################################################################################"

# Test the python script compare_fitted_nuisance.py
echo "############### Testing python script compare_fitted_nuisance.py with sample input files ##############"
python "${scriptDir}"/../scripts/compare_fitted_nuisance.py \
  --root-workspace "${ROOT_WORKSPACE}" \
  --pyhf-json "${PYHF_JSON}"
