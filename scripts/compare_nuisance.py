import ROOT
import pyhf
import sys
import click
import json

@click.command()
@click.option(
    '--root-workspace',
    help='The location of the root file containing the combined root workspace'
)
@click.option(
    '--pyhf-json',
    help='The location of the json file containing the pyhf likelihood info'
)

def compare_nuisance(root_workspace, pyhf_json):
   # Get the root nuisance params
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
      x.GetName() for x in exhaust_argset(mc.GetParametersOfInterest())
  ]

  # Replace some strings to match root nuisance param names to pyhf naming scheme
  pars_root = [sub.replace('alpha_', '') \
              .replace('gamma_stat_', 'staterror_') \
	      .replace('gamma_stat_', 'staterror_') \
	      .replace('lumi', 'Lumi') \
	      .replace('_bin', '') \
	      .replace('_cuts_0', '_cuts') for sub in pars]

  # Get pyhf nuisance params
  w = pyhf.Workspace(json.load(open(pyhf_json)))
  m = w.model()

  pars_pyhf = []
  for k,v in m.config.par_map.items():
    sl = v['slice']
    npars = sl.stop-sl.start
    if npars > 1:
      for i in range(npars):
        pars_pyhf.append('{}_{}'.format(k,i))
    else:
      pars_pyhf.append(k)

  # Compare the nuisance params
  nuisance_dict={
  'root': pars_root, 
  'pyhf': pars_pyhf
   }

  unique_dict = {
  'root': [],
  'pyhf': []  
  }

  unique_dict['pyhf'] = set(nuisance_dict['pyhf']) - set(nuisance_dict['root'])
  unique_dict['root'] = set(nuisance_dict['root']) - set(nuisance_dict['pyhf'])

  print("Nuisance params unique to pyhf:")
  for param in unique_dict['pyhf']:
    print(param)

  print("\nNuisance params unique to root:")
  for param in unique_dict['root']:
    print(param)

if __name__ == '__main__':
    compare_nuisance()
