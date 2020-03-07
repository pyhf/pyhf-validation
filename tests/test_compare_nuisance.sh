#!/bin/bash

# Get the location of this testing script to make other paths relative to it
scriptDir=$(dirname -- "$(readlink -f -- "${BASH_SOURCE[@]}")")

# Download test files
curl https://cernbox.cern.ch/index.php/s/eDsgyIlqhu1OVTP/download --output sample_root_workspace.root
curl https://cernbox.cern.ch/index.php/s/lPGCNT5ytWSxk4I/download --output sample_pyhf_likelihood.json

# Download expected output for compare_nuisance_output_expected.txt
curl https://cernbox.cern.ch/index.php/s/YoCnn78sIwWCSoV/download --output compare_nuisance_output_expected.txt

# Test the python script compare_nuisance.py
echo "################## Testing python script compare_nuisance.py with sample input files ##################"
python "${scriptDir}"/../scripts/compare_nuisance.py --root-workspace sample_root_workspace.root --pyhf-json sample_pyhf_likelihood.json | tee compare_nuisance_output.txt

# Compare the output files with the expected ones
if cmp -s "compare_nuisance_output_expected.txt" "compare_nuisance_output.txt" ; then
echo "------------> compare_nuisance.py gives expected output :)"
  else
echo "------------> compare_nuisance.py DOES NOT give expected output"
  exit 1
fi
echo "#######################################################################################################"

# Test the python script compare_fitted_nuisance.py
echo "############### Testing python script compare_fitted_nuisance.py with sample input files ##############"
python "${scriptDir}"/../scripts/compare_fitted_nuisance.py --root-workspace sample_root_workspace.root --pyhf-json sample_pyhf_likelihood.json


# Remove the test files and output files now that we're done with them
rm sample_root_workspace.root sample_pyhf_likelihood.json compare_nuisance_output.txt
