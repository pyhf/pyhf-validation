#!/bin/bash
# Script to test validate_systs.py with test input located in test_syst_validation_input. This script has been tested in the python:3.7 docker container with pyhf, parse, and matplotlib installed
# Note: this script is assumed to be run from one level above the directory containing the script.

cd tests

# Download the published likelihoods from the sbottom publication
wget -O sbottom.tar.gz https://www.hepdata.net/record/resource/997020?view=true

# Grab the likelihoods from one of the analysis regions
tar -xvzf sbottom.tar.gz RegionA
rm sbottom.tar.gz

# Change the name of the dir to something more sensible for the validation output
mv RegionA test_syst_validation_dir
cd test_syst_validation_dir
mkdir -p Plots

# Run the validate_systs.py script on the test sbottom likelihoods
python ../../scripts/validate_systs.py --signal_template sbottom_{a}_{b}_{c} --x_var a --y_var b --v_max 4 --x_label 'x label' --y_label 'y label'

# Return to the original working directory
cd ../..
