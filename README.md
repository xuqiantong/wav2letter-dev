# wav2letter-dev
This is a repository containing scripts to launch jobs with SLURM.


To check the status of running jobs:
```sh
$ squeue -o "%.10i %.9P %35j %.8u %.2t %.10M %.6D %R" -p rasr,priority,dev -u padentomasello,gab,avidov,qiantong
     JOBID PARTITION NAME                                    USER ST       TIME  NODES NODELIST(REASON)
  32221800       dev forward                             qiantong  R    1:09:43      1 learnfair0253
  32221801       dev forward                             qiantong  R    1:09:43      1 learnfair0281
  32221802       dev forward                             qiantong  R    1:09:43      1 learnfair0374
  32220798       dev forward                             qiantong  R    3:25:44      1 learnfair0565
  32098163      rasr 256_GPU:24                          qiantong  R 2-19:08:17     16 learnfair[1186-1187,1190,1194,1200,1204-1206,1209,1211,1964,1977-1979,1985-1986]
  32214553      rasr 256_GPU:34                          qiantong  R    9:53:49     16 learnfair[1179-1180,1184-1185,1188,1192,1203,1207-1208,1210,1213,1960,1962,1969,1982-1983]
  31815622  priority w2v_pl:ls_1h_rescore_ltr_ctc          avidov  R 1-08:26:49      4 learnfair[5101,5188,5190,5193]
  32086525  priority w2v_pl:10h_rescore                  qiantong  R   11:31:47      8 learnfair[1359,1380,1383,1409,1439,1613,1664,1678]
  32025852  priority swbd:13                             qiantong  R 1-23:53:06      4 learnfair[2194,2339,2354,2419]
```

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


