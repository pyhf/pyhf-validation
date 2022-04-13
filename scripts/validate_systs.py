"""
  Date:     200325
  History:
    - Originally written as a python notebook by Lukas Heinrich
    - Adapted for the 3L-RJ likelihood validation by Giordon Stark (https://github.com/kratsg/3L-RJ-mimic-likelihood-validation/blob/master/OutlierPlot.ipynb)
    - Adapted and generalized to script by Danika MacDonell [March 25, 2020]
    - Adapted and fixed up more to run on patchsets [April 13, 2022]

  Details:  Script to visualize the relative size of the systematics for pyhf likelihoods at each mass point, where the systematics are added together in quadrature. Should be run in a directory containing the background-only json likelihood file, along with a patch json likelihood file for each signal point. Assumes that all the json patch file are located at the same directory level as this script.

  Usage:
  >> python OutlierPlot.py --signal_template <signal_template_{a}_{b}_{c}_for_masses> --x_var <which variable in signal name template to plot on x axis (defaults to 'a')> --y_var <which variable in signal name template to plot on x axis (defaults to 'b')> --v_max <max colourbar amplitude> --x_label <x axis label> --y_label <y axis label>

  Example for 1Lbb Wh analysis (https://glance.cern.ch/atlas/analysis/analyses/details.php?id=2969):

  >> python OutlierPlot.py --signal_template C1N2_Wh_hbb_{a}_{b} --x_var a --y_var b --v_max 10 --x_label '$m(\tilde{\\chi}_{1}^{\\pm}/\tilde{\\chi}_{2}^{0})$ [GeV]' --y_label '$m(\tilde{\\chi}_{1}^{0})$ [GeV]'

  The signal template is the name of an arbitrary signal in the json patch files, with the signal masses left as {}. Given a background-only file and a patch file, the signal name can be found under "samples" in the output of:
  >> jsonpatch BkgOnly.json patch_XXX.json | pyhf inspect

  If, for example, one of the signals is called C1N2_Wh_hbb_550_200, where 550 and 200 are the variable model masses, the signal template would be C1N2_Wh_hbb_{}_{}.
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


def handle_deltas(delta_up, delta_dn):
    nom_is_center = np.bitwise_or(
        np.bitwise_and(delta_up > 0, delta_dn > 0),
        np.bitwise_and(delta_up <= 0, delta_dn <= 0),
    )
    span = delta_dn + delta_up
    maxdel = np.maximum(np.abs(delta_dn), np.abs(delta_dn))
    abs_unc = np.where(nom_is_center, span, maxdel)
    return abs_unc


def process_patch(p):
    nom = np.asarray(p["value"]["data"])

    # histosys
    hid = np.asarray(
        [
            m["data"]["hi_data"]
            for m in p["value"]["modifiers"]
            if m["type"] == "histosys"
        ]
    )
    lod = np.asarray(
        [
            m["data"]["lo_data"]
            for m in p["value"]["modifiers"]
            if m["type"] == "histosys"
        ]
    )
    delta_up = hid - nom
    delta_dn = nom - lod
    histo_deltas = handle_deltas(delta_up, delta_dn)

    hi = np.asarray(
        [m["data"]["hi"] for m in p["value"]["modifiers"] if m["type"] == "normsys"]
    )
    lo = np.asarray(
        [m["data"]["lo"] for m in p["value"]["modifiers"] if m["type"] == "normsys"]
    )
    delta_up = np.asarray([delta * nom - nom for delta in hi])
    delta_dn = np.asarray([delta * nom - nom for delta in lo])
    norm_deltas = handle_deltas(delta_up, delta_dn)
    norm_deltas = norm_deltas if norm_deltas.size else np.ones_like(histo_deltas)

    stat_deltas = np.zeros_like(
        histo_deltas
    )  # Don't consider the stat error for this calculation

    systs = np.concatenate([histo_deltas, norm_deltas, stat_deltas])
    inquad = np.sqrt(np.sum(np.square(systs), axis=0))
    rel = inquad / nom
    rel = np.where(nom == 0, np.ones_like(nom), rel)
    return rel, nom


def plot_rel_systs(p, channel_names, channel_bins):

    signal_name = p["value"]["name"]
    channel_name = channel_names[p["path"]]
    nom = np.asarray(p["value"]["data"])
    n_bins = channel_bins[p["path"]]

    # Collect syst names and deltas for histo systs
    sys_names_histo = [
        np.asarray(
            [m["name"] for m in p["value"]["modifiers"] if m["type"] == "histosys"]
        )
    ][0].tolist()
    hid = np.asarray(
        [
            m["data"]["hi_data"]
            for m in p["value"]["modifiers"]
            if m["type"] == "histosys"
        ]
    )
    lod = np.asarray(
        [
            m["data"]["lo_data"]
            for m in p["value"]["modifiers"]
            if m["type"] == "histosys"
        ]
    )
    delta_up = hid - nom
    delta_dn = nom - lod
    histo_deltas = handle_deltas(delta_up, delta_dn)
    histo_rel_size = np.absolute(histo_deltas) / (1.0 * nom)

    # Collect syst names and deltas for norm systs
    sys_names_norm = [
        np.asarray(
            [m["name"] for m in p["value"]["modifiers"] if m["type"] == "normsys"]
        )
    ][0].tolist()
    hi = np.asarray(
        [m["data"]["hi"] for m in p["value"]["modifiers"] if m["type"] == "normsys"]
    )
    lo = np.asarray(
        [m["data"]["lo"] for m in p["value"]["modifiers"] if m["type"] == "normsys"]
    )
    delta_up = np.asarray([delta * nom - nom for delta in hi])
    delta_dn = np.asarray([delta * nom - nom for delta in lo])
    norm_deltas = handle_deltas(delta_up, delta_dn)
    norm_rel_size = np.absolute(norm_deltas) / (1.0 * nom)

    sys_names = sys_names_histo + sys_names_norm

    for iBin in range(n_bins):
        bin_number = iBin + 1
        rel_size = (
            np.concatenate((histo_rel_size[:, iBin], norm_rel_size[:, iBin]))
            if norm_deltas.size
            else histo_rel_size[:, iBin]
        )
        sys_names_bin = [
            sys_names[idx]
            for idx, size in enumerate(rel_size)
            if size > 0.5 and np.isfinite(size)
        ]  # Select for relative systematics above 0.5 (i.e. >50% variation from nominal)
        rel_size = rel_size[(rel_size > 0.5) & (np.isfinite(rel_size))]

        # Only make a plot if there are any relative systematics above 0.5
        if len(sys_names_bin) > 0:
            x = np.arange(len(sys_names_bin))  # the label locations
            width = 0.5  # the width of the bars
            fig = plt.figure(figsize=(12, 6))
            ax = fig.add_subplot(1, 1, 1)
            ax.set_ylabel("Relative Syst Size", fontsize=16)
            ax.set_title(
                f"{signal_name}: {channel_name} (Bin {bin_number}), Norm & Histo",
                fontsize=20,
            )
            ax.bar(x - width / 2, rel_size, width)
            ax.set_xticks(x)
            ax.set_xticklabels(sys_names_bin, rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(
                f"plots/rel_systs_{signal_name}_{channel_name}_bin{bin_number}.png"
            )
            plt.close()


@click.command()
@click.option(
    "--signal_template",
    help="Signal name template, with signal masses as variables. Signal masses must be denoted by {a}, {b}, {c}, ... (eg. signal_{a}_{b}_more_info)",
)
@click.option(
    "--x_var",
    help="Which variable from the signal name template to plot on the x axis (defaults to 'a')",
    default="a",
    required=False,
)
@click.option(
    "--y_var",
    help="Which variable from the signal name template to plot on the y axis (defaults to 'b')",
    default="b",
    required=False,
)
@click.option(
    "--v_max",
    help="Maximum amplitude of the colourbar for plotting interpolated relative syst sizes",
    default=10,
    required=False,
)
@click.option(
    "--x_label",
    help="x label for interpolated plot of relative systematics",
    default=None,
    required=False,
)
@click.option(
    "--y_label",
    help="y label for interpolated plot of relative systematics",
    default=None,
    required=False,
)
def outlier_plot(signal_template, v_max, x_var, y_var, x_label, y_label):

    patchset = pyhf.PatchSet(json.load(open("patchsets_SlepSlep.json")))

    data = {
        x.patch[0]["value"]["name"]: {
            p["path"]: process_patch(p) for p in x.patch if p["op"] == "add"
        }
        for x in patchset
        if "value" in x.patch[0]
    }

    # Make the mapping of json channel names to analysis region names
    spec_sig = patchset.patches[0].patch
    spec_bkg = json.load(open("bkgonly.json"))

    channel_names = {}
    names_json = []
    for channel in spec_bkg["channels"]:
        names_json.append(channel["name"])

    for patch in patchset:
        for op in patch.patch:
            path = op["path"]
            channel_index = int(path.split("/")[2])
            channel_names[path] = names_json[channel_index]

    # Make the mapping of number of json channel name to number of bins
    workspace_bkg = pyhf.Workspace(spec_bkg)
    channel_bins = {}
    for key, value in channel_names.items():
        channel_bins[key] = workspace_bkg.channel_nbins[value]

    outliers = []
    for k, v in data.items():
        for kk, vv in v.items():
            for b, (r, n) in enumerate(zip(*vv)):
                if r > 1.0:
                    outliers.append((k, kk, b, r, n))

    # Make plots of relative syst for each signal point and bin
    for x in patchset.patches:
        if "value" in x.patch[0]:
            for p in x.patch:
                if p["op"] == "add":
                    plot_rel_systs(p, channel_names, channel_bins)

    print("Outliers (> 1.0):")
    for o in list(reversed(sorted(outliers, key=lambda x: x[-1]))):
        print("\t", o[-1], o[-2], o[0], channel_names[o[1]], o[2])
    """
    missing_signal = []
    # missing signal in signal region
    print("Missing signal in signal region:")
    for k, v in data.items():
        if not '/channels/2/samples/5' in v or not '/channels/2/samples/5' in v:
            missing_signal.append(k)
            print('\t',k)
    """

    data = {
        x.patch[0]["value"]["name"]: {
            p["path"]: process_patch(p)[0] for p in x.patch if p["op"] == "add"
        }
        for x in patchset.patches
        if "value" in x.patch[0]
    }

    sig_name_template = signal_template

    for channel in channel_names.keys():
        rel_systs = np.asarray(
            [
                [
                    float(m)
                    for m in [
                        parse.parse(sig_name_template, k).named[x_var],
                        parse.parse(sig_name_template, k).named[y_var],
                    ]
                ]
                + v.get(channel, np.array([0.0] * channel_bins[channel])).tolist()
                for k, v in data.items()
            ]
        )
        x_min, x_max = min(rel_systs[:, 0]), max(rel_systs[:, 0])
        y_min, y_max = min(rel_systs[:, 1]), max(rel_systs[:, 1])
        x, y = np.mgrid[x_min:x_max:100j, y_min:y_max:100j]
        for jbin in range(2, 2 + channel_bins[channel]):
            f = plt.figure(figsize=(12, 6))
            ax = f.add_subplot(1, 1, 1)
            if x_label is not None:
                ax.set_xlabel(x_label, fontsize=20)
            if y_label is not None:
                ax.set_ylabel(y_label, fontsize=20)
            ax.set_xlim(x_min - 25, x_max + 25)
            ax.set_ylim(y_min - 25, y_max + 25)
            bin_number = jbin - 1
            rel_systs = rel_systs[
                rel_systs[:, jbin] != 0
            ]  # Remove any points with zero relative syst

            if len(rel_systs) > 0:
                z = scipy.interpolate.griddata(
                    rel_systs[:, :2], rel_systs[:, jbin], (x, y)
                )

                vmin, vmax = 0, v_max
                ax.scatter(
                    rel_systs[:, 0],
                    rel_systs[:, 1],
                    c=rel_systs[:, jbin],
                    edgecolors="w",
                    vmin=vmin,
                    vmax=vmax,
                )
                im = ax.contourf(x, y, z, levels=np.linspace(vmin, vmax, 100))
                cb = plt.colorbar(im, ax=ax)
                cb.set_label(
                    label=r"$\oplus$ (histosys, normsys, staterr)", fontsize=18
                )
                if channel_bins[channel] < 2:
                    ax.set_title(channel_names[channel], fontsize=20)
                else:
                    ax.set_title(
                        f"{channel_names[channel]} (Bin {bin_number})", fontsize=20
                    )

                outliers_chan = np.asarray(
                    [
                        [
                            float(parse.parse(sig_name_template, o[0]).named[x_var]),
                            float(parse.parse(sig_name_template, o[0]).named[y_var]),
                        ]
                        + [o[-2]]
                        for o in outliers
                        if o[1] == channel and o[2] == jbin - 2
                    ]
                )

                if outliers_chan.shape[0]:
                    ax.scatter(
                        outliers_chan[:, 0],
                        outliers_chan[:, 1],
                        c=outliers_chan[:, 2],
                        vmin=0,
                        vmax=20,
                        cmap="cool",
                    )
                for o in outliers_chan:
                    ax.text(o[0] + 5, o[1] + 5, f"{o[2]:.2f}", c="r")

                plt.tight_layout()
                plt.savefig(f"plots/{channel_names[channel]}_bin{bin_number}.png")
                plt.close()


if __name__ == "__main__":
    outlier_plot()
