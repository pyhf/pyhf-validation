"""
  History:
    - Requested by Jeff Shahinian as part of EWK Compressed Wave 1 validation

  Details:  Script to visualize the outputs of the scripts/compare_fitted_nuisance.py

  Usage:
  >> python plot_compare_fitted_nuisance.py <file> <file> ... <file>
  """

import json
import glob
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate
import parse
import click
import pyhf

plt.rc("xtick", labelsize=14)
plt.rc("ytick", labelsize=14)

@click.command()
@click.argument('files', type=click.Path(exists=True), nargs=-1)
@click.option(
    "--output",
    help="Path to file to output nuisance parameter comparison to.",
    default="compare_fitted_nuisance.png",
)
def plot_compare_fitted_nuisance(files, output):
    data = {}

    for filename in files:
        for p_param, p_pyhf, p_root, p_abs, p_rel in np.loadtxt(files[0], dtype={'names': ['param', 'pyhf', 'root', 'abs', 'rel'], 'formats': ['|S42', float, float, float, float]}, skiprows=2):
            data.setdefault(p_param, {'abs': [], 'rel': []})
            data[p_param]['abs'].append(p_abs)
            data[p_param]['rel'].append(p_rel)

    print(f'Loaded {len(data)} nuisance parameters from {len(files)} files')

    data_abs, data_rel = list(zip(*[i for k,v in data.items() for i in zip(v['abs'], v['rel'])]))
    fig, ax = plt.subplots(2, 1, figsize=(10,20))
    ax[0].hist(np.abs(data_rel), bins=np.logspace(0, 5, 50))
    ax[0].set_xscale('log')
    ax[0].set_xlabel(r'$\left|\ \frac{\mathrm{pyhf} - \mathrm{ROOT}}{\mathrm{pyhf}}\ \right|$')

    ax[1].hist(np.clip(data_abs, -1, 1), bins=np.linspace(-1, 1, 200))

    fig.savefig(output)

if __name__ == "__main__":
    plot_compare_fitted_nuisance()
