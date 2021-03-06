import pathlib
import subprocess
import os
import stat
import shutil
import importlib

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--am', type=pathlib.Path)
parser.add_argument('--lm', type=str)
parser.add_argument('--logdir', type=pathlib.Path)
parser.add_argument('--prefix', type=str)
parser.add_argument('--binary', type=pathlib.Path)

parser.add_argument('--perturb', type=str, default="")
parser.add_argument('--local', action='store_true')
parser.add_argument('--partition', type=str, default='learnfair')
parser.add_argument('--n', type=int, default=8)
parser.add_argument('--gpu', type=int, default=1)
parser.add_argument('--cpu', type=int, default=10)
parser.add_argument('--hour', type=int, default=10)

parser.add_argument('--test', type=str, default="dev-other.lst")
parser.add_argument('--beamsize', type=int, default=10)
parser.add_argument('--beamthreshold', type=int, default=10)
parser.add_argument('--beamsizetoken', type=int, default=10)
parser.add_argument('--datadir', type=str, default=None)
parser.add_argument('--nthread_decoder', type=int, default=1)
parser.add_argument('--lmtype', type=str, default="kenlm")
parser.add_argument('--uselexicon', type=str, default="true")
parser.add_argument('--decodertype', type=str, default="wrd")
parser.add_argument('--smearing', type=str, default="max")
parser.add_argument('--emission_dir', type=str, default="")
parser.add_argument('--lm_vocab', type=str, default="")
parser.add_argument('--lm_memory', type=int, default=5000)
parser.add_argument('--silscore', type=float, default=0.)
parser.add_argument('--eosscore', type=float, default=0.)
parser.add_argument('--wordscore', type=float, default=0.)
parser.add_argument('--lmweight', type=float, default=0.)
parser.add_argument('--attentionthreshold', type=int, default=10000)
parser.add_argument('--maxdecoderoutputlen', type=int, default=None)
parser.add_argument('--lexicon', type=str, default=None)
parser.add_argument('--tokens', type=str, default=None)
parser.add_argument('--tokensdir', type=str, default=None)
parser.add_argument('--logadd', type=str, default="false")

# Templates
sbatch_cmd = """#!/bin/bash

#SBATCH --output={}/%A_%a.out
#SBATCH --error={}/%A_%a.err
#SBATCH --comment=decoder_sweep
#SBATCH --job-name=sweep_{}
#SBATCH --partition={}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:{}
#SBATCH --cpus-per-task={}
#SBATCH --mem-per-cpu=6G
#SBATCH --open-mode=append
#SBATCH --time={}:00:00
#SBATCH --array=0-{}%{}
#SBATCH -C volta32gb

module purge
module load cuda/10.0
module load cudnn/v7.6-cuda.10.0
module load NCCL/2.4.7-1-cuda.10.0
module load mkl/2018.0.128
module unload kenlm # kenlm loads boost and causes pb to AF
module load gcc/6.3.0 

srun sh {}/sub_${{SLURM_ARRAY_TASK_ID}}.sh
"""


if __name__ == '__main__':
    args = parser.parse_args()

    if len(args.perturb) == 0:
        args.perturb = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'perturb_parameters.py')
    spec = importlib.util.spec_from_file_location("module.name", args.perturb)
    perturb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(perturb)

    log_dir = os.path.join(args.logdir, args.prefix)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if args.local:
        log_dir = '/tmp'
        args.n = 1
        print(args)

    run_sh_path = os.path.join(log_dir, 'run.sh')
    sub_sh_path = os.path.join(log_dir, 'sub_{}.sh')
    with open(run_sh_path, 'w') as f:
        f.write(sbatch_cmd.format(log_dir, log_dir, args.prefix,
                                  args.partition, args.gpu, args.cpu, 
                                  args.hour, args.n-1, args.n, log_dir))

    ignore_args = set(['n', 'local', 'prefix', 'gpu', 'cpu', 'hour',
                   'partition', 'binary', 'logdir', 'perturb'])
    override_args = set(['datadir', 'lexicon', 'tokens', 'tokensdir', 'maxdecoderoutputlen'])
    
    for i in range(args.n):
        args = perturb.perturb_parameters(args)

        with open(sub_sh_path.format(i), 'w') as f:
            f.write('#!/bin/bash\n\n')

            if args.lmtype == 'kenlm' and not args.local:
                f.write(
                    "cp {} /scratch/slurm_tmpdir/$SLURM_JOB_ID/lm.bin\n\n".format(args.lm))

            f.write(str(args.binary) + ' ')
            for arg in vars(args):
                if arg in ignore_args:
                    continue
                k, v = arg, getattr(args, arg)
                if k in override_args and not v:
                    continue
                
                if k == 'lm' and args.lmtype == 'kenlm' and not args.local:
                    v = "/scratch/slurm_tmpdir/$SLURM_JOB_ID/lm.bin"
                f.write('--{}={} '.format(k, v))

            f.write('--logtostderr --show')

            if args.lmtype == 'kenlm' and not args.local:
                f.write(
                    "\n\nrm /scratch/slurm_tmpdir/$SLURM_JOB_ID/lm.bin\n".format(args.lm))

    if args.local:
        os.system("sh /tmp/sub_0.sh")
    else:
        os.system("sbatch " + run_sh_path)
