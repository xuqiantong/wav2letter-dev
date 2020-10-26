#!/bin/bash
#SBATCH --output=/checkpoint/qiantong/tmp/tr-forward-%j.out
#SBATCH --error=/checkpoint/qiantong/tmp/tr-forward-%j.err
#SBATCH --comment="wav2letter lm forward"
#SBATCH --job-name=forward
#SBATCH --partition=dev
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=10G
#SBATCH --open-mode=append
#SBATCH --time=40:00:00

module purge
module load anaconda3/5.0.1 cuda/10.0 cudnn/v7.6-cuda.10.0
source deactivate
source activate /private/home/antares/.conda/envs/fairseq-20190809

export TR=/checkpoint/antares/2019-11-02/v4_reduced_lr_trlmgb.invsqrt.wrm16000.int1e-07.nag.lr0.05.clp0.1.lyr20.hd16.drp0.1.adp\=60000_160000.ad_inp.ad_f4.ad_sf4.inp\=60000_160000.tie.ffn6144.at_d0.1.rl_d0.1.i1280.m1280.o1280.mxtk2048.tps256.seed1.bm\=eos.ngpu128/checkpoint_best.pt

cd /checkpoint/antares/experiments/librispeech_lms/fairseq-py
python forward_lm.py --model $TR --dict /checkpoint/wav2letter/released_models/sota/2019/lms/word_tr/dict.txt --text "$1/$2.lst.hyp" --out "$1/$2-tr.ppl" --model-type transformer --max-tokens 1024 --skip 1

