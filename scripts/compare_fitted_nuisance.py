import ROOT
import json
import pyhf
import click


@click.command()
@click.option(
    "--root-workspace",
    help="The location of the root file containing the combined root workspace",
)
@click.option(
    "--pyhf-json",
    help="The location of the json file containing the pyhf likelihood info",
)
@click.option(
    "--outfile",
    help="Path to file to output nuisance parameter comparison to. Will print to screen if left blank.",
    default="",
)
def compare_fitted_nuisance(root_workspace, pyhf_json, outfile):

    # Get the root fit results
    infile = ROOT.TFile.Open(root_workspace)
    workspace = infile.Get("combined")

    mc = workspace.obj("ModelConfig")

    def exhaust_argset(s):
        it = s.fwdIterator()
        while True:
            n = it.next()
            if not n:
                break
            yield n

    pars = [x.GetName() for x in exhaust_argset(mc.GetNuisanceParameters())] + [
        x.GetName() for x in exhaust_argset(mc.GetParametersOfInterest())
    ]

    model = workspace.pdf("simPdf")
    data = workspace.data("obsData")
    model.fitTo(data)

    params_root = {}
    for par in pars:
        params_root[par] = workspace.var(par).getVal()

    # Get the pyhf fit results
    ws = pyhf.Workspace(json.load(open(pyhf_json)))
    model = ws.model(
        modifier_settings={
            "normsys": {"interpcode": "code4"},
            "histosys": {"interpcode": "code4p"},
        },
    )
    data = ws.data(model)
    bestfit = pyhf.infer.mle.fit(data, model)

    params_pyhf = {}
    for k, v in model.config.par_map.items():
        sl = v["slice"]
        npars = sl.stop - sl.start
        value = bestfit[sl]
        if npars > 1 or "staterror" in k:
            for i in range(npars):
                params_pyhf[f"{k}_{i}"] = float(value[i])
        else:
            params_pyhf[k] = float(value[0])

    nuisance_dict = {"root": params_root, "pyhf": params_pyhf}

    # Compare the fitted nuisance params, and print them out, either to the specified file or to the screen
    if outfile != "":
        f_comp = open(outfile, "w")
    else:
        f_comp = None
        print(
            "\n\n########### Printing nuisance parameter comparisons to screen #############\n"
        )

    param_str = "param"
    pyhf_val_str = "pyhf val"
    root_val_str = "root val"
    abs_diff_str = "abs diff"
    perc_diff_str = "% diff"
    print(
        f"{param_str:<42}{pyhf_val_str:<18}{root_val_str:<18}{abs_diff_str:<18}{perc_diff_str:<18}\n",
        file=f_comp,
    )

    for param in nuisance_dict["root"]:
        # Replace some strings to match root nuisance param names to pyhf naming scheme
        pyhf_param = (
            param.replace("alpha_", "")
            .replace("gamma_stat_", "staterror_")
            .replace("lumi", "Lumi")
            .replace("_bin", "")
        )

        root_val = float(nuisance_dict["root"][param])
        try:
            pyhf_val = float(nuisance_dict["pyhf"][pyhf_param])
        except KeyError:
            print("Parameter %s missing from pyhf file" % pyhf_param)
            continue
        try:
            perc_diff = 100 * (pyhf_val - root_val) / pyhf_val
        except ZeroDivisionError:
            perc_diff = 0
        abs_diff = pyhf_val - root_val
        print(
            f"{pyhf_param:<42}{pyhf_val:<18.6e}{root_val:<18.6e}{abs_diff:<18.6e}{perc_diff:<18.6f}",
            file=f_comp,
        )
    if f_comp is None:
        print(
            "\n###########################################################################\n"
        )


if __name__ == "__main__":
    compare_fitted_nuisance()
