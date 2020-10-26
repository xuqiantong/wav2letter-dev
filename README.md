# wav2letter-dev
This is a repository containing scripts to launch jobs with SLURM.


## Training
0. Requeue the job itself automatically after time-out.
1. Mirroring the structure of config files with checkpoints
    1. Config file: `<path/to>/your_project/experiment_name.cfg`
    2. Checkpoint folder: `<path/to/checkpoints>/your_project/experiment_name/`
2. Storing everything inside the checkpoint folder:
    1. Scripts to launch the job
    2. Stderr and stout logs
    3. Checkpoints
3. Detailed information in squeue:
    1. `your_project:experiment_name`
4. Adding new flags in `--extra` will create a new job with corresponding suffix.
5. Error checking:
    1. Prevent restarting a training job that’ll overwrite existing checkpoints
    2. Prevent continue training from nowhere
    3. Allow testing locally (adding flag `--local`) before launching — to spot obvious errors
6. **ALL** in one piece:
    1. Minimal changes to launch new jobs
7. Collaboration training
    1. Allowing other users to continue training your job

### Train

- Input config: `<path/to>/your_project/experiment_name.cfg`
- Output: `<path/to/checkpoints>/your_project/experiment_name`

```
python3 train.py \
--binary=<path/to>/wav2letter/build/Train \
--mode=train --config=<path/to>/your_project/experiment_name.cfg \
--ngpu=64 --partition=learnfair
```

### Train with extra flags
- Additional flags: `--lr=0.1`
- Output: `<path/to/checkpoints>/your_project/experiment_name_lr0.1`

```
python3 train.py \
--binary=<path/to>/wav2letter/build/Train \
--mode=train --config=<path/to>/your_project/experiment_name.cfg \
--extra="--lr=0.1" \
--ngpu=64 --partition=learnfair
```

### Continue
- Output: `<path/to/checkpoints>/your_project/experiment_name`
- Adding extra flags will not create a new job

```
python3 train.py \
--binary=<path/to>/wav2letter/build/Train \
--mode=continue --model_path=<path/to/checkpoints>/your_project/experiment_name \
--extra="--lr=0.1" \
--ngpu=64 --partition=learnfair
```

### Fork
- Input config: `<path/to>/your_project/experiment_name.cfg`
- Input model: `<path/to/another/experiment>/checkpoint.bin`
- Output: `<path/to/checkpoints>/your_project/experiment_name`

```
python3 train.py \
--binary=<path/to>/wav2letter/build/Train \
--mode=fork --config=<path/to>/your_project/experiment_name.cfg \
--model_path=<path/to/another/experiment>/checkpoint.bin \
--ngpu=64 --partition=learnfair
```


## Decoding

### Sweep
Use `--local` to test locally, if training is able to start.
```
python3 decoder_sweep/sweep.py \
--binary=<...>/wav2letter/build/Decoder \
--am=<...>/checkpoint.bin \
--lm=<...>/lm.bin \
--uselexicon=true \
--lexicon=<...>/lexicon.txt \
--decodertype=wrd \
--datadir=<...> \
--test=dev-clean.lst \
--logdir=<...>/decoder_sweep \
--prefix=my_experiment \
--n=120 \
--partition=learnfair \
--beamsize=50 --beamthreshold=10 --beamsizetoken=10
```

### Collect
```
python3 decoder_sweep/collect.py \
--logdir=<...>/decoder_sweep \
--prefix=my_experiment 
```


## Rescoring

### Beam dump
```
<...>/wav2letter/build/Decoder \
--isbeamdump=true \
--test=dev-clean.lst \
--sclite=<...>/my_experiment_dump \
...
```

### LM forwarding
```
sbatch decoder_sweep/transformer_forward.sh <...>/my_experiment_dump dev-clean
```

### Rescoring 

#### Grid search
```
python3 decoder_sweep/rescore.py \
--hyp=<...>/my_experiment_dump/dev-clean.lst.hyp \
--tr=<...>/my_experiment_dump/dev-clean-tr.ppl \
--list=<ground_truth_of>/dev-clean.lst \
--search --gridsearch --new
```

#### Evaluation
```
python3 decoder_sweep/rescore.py \
--hyp=<...>/my_experiment_dump/dev-clean.lst.hyp \
--tr=<...>/my_experiment_dump/dev-clean-tr.ppl \
--list=<ground_truth_of>/dev-clean.lst \
--in_wts=0,0,0 --new
```


