import ROOT
import sys
import json
import pyhf
import click

@click.command()
@click.option(
    '--root-workspace',
    help='The location of the root file containing the combined root workspace'
)
@click.option(
    '--pyhf-json',
    help='The location of the json file containing the pyhf likelihood info'
)

@click.option(
    '--outfile',
    help='Path to file to output nuisance parameter comparison to. Will print to screen if left blank.',
    default=""
)

def compare_fitted_nuisance(root_workspace, pyhf_json, outfile):
  # Get the root fit results 
  infile = ROOT.TFile.Open(root_workspace)
  workspace = infile.Get("combined")

  mc = workspace.obj('ModelConfig')

  def exhaust_argset(s):
    it = s.fwdIterator()
    pars = []
    while True:
      n = it.next()
      if not n:
        break
      yield n

  pars = [
    x.GetName() for x in exhaust_argset(mc.GetNuisanceParameters())
   ] + [
    x.GetName() for x in exhaust_argset(mc.GetParametersOfInterest())]

  p = workspace.pdf('simPdf')
  d = workspace.data('obsData')
  p.fitTo(d)

  params_root = {}
  for p in pars:
    params_root[p] = workspace.var(p).getVal()

  # Get the pyhf fit results
  w = pyhf.Workspace(json.load(open(pyhf_json)))
  m = w.model(        modifier_settings={
            'normsys': {'interpcode': 'code4'},
            'histosys': {'interpcode': 'code4p'},
        },
   )
  d = w.data(m)

  bestfit = pyhf.infer.mle.fit(d,m)

  params_pyhf = {}
  for k,v in m.config.par_map.items():
    sl = v['slice']
    npars = sl.stop-sl.start
    value = bestfit[sl]
    if npars > 1:
      for i in range(npars):
        params_pyhf['{}_{}'.format(k,i)] = float(value[i])
    else:
      params_pyhf[k] = float(value[0])

  nuisance_dict = {
  'root': params_root,
  'pyhf': params_pyhf
   }

  # Compare the fitted nuisance params, and print them out, either to the specified file or to the screen
  if outfile != "": f_comp = open(outfile, 'w')
  else: 
    f_comp = None
    print("\n\n########### Printing nuisance parameter comparisons to screen #############\n")

  print("%42s%18s%18s%18s%18s\n"%("param", "pyhf val", "root val", "abs diff", "% diff"), file=f_comp)
  for param in nuisance_dict['root']:
    # Replace some strings to match root nuisance param names to pyhf naming scheme
    pyhf_param = param.replace('alpha_', '').replace('gamma_stat_', 'staterror_').replace('lumi', 'Lumi').replace('_bin', '').replace('_cuts_0', '_cuts')

    root_val = float(nuisance_dict['root'][param])
    try:
      pyhf_val = float(nuisance_dict['pyhf'][pyhf_param])
    except:
      print("Parameter %s missing from pyhf file"%pyhf_param)
      continue
    try: perc_diff = 100*(pyhf_val-root_val)/pyhf_val
    except ZeroDivisionError: perc_diff = 0
    abs_diff = pyhf_val-root_val
    print("%42s%18e%18e%18e%18f\n"%(pyhf_param, pyhf_val, root_val, abs_diff, perc_diff), file=f_comp)
  if f_comp == None: print("\n###########################################################################\n")

if __name__ == '__main__':
    compare_fitted_nuisance()