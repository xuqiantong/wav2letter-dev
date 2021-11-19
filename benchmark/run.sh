#!/bin/bash

# sbatch --job-name=benchmark:1 \
# --output=$2/GPU_1.log \
# --error=$2/GPU_1.err \
# --constraint volta32gb \
# --cpus-per-task=10 \
# --partition=prioritylab --comment=deadline \
# --time=00:20:00 \
# --mem-per-gpu=50GB \
# --nodes=1 --ntasks-per-node=1 \
# --gpus-per-node=8 \
# --wrap="export NCCL_SOCKET_IFNAME=^docker0,lo; srun bash /private/home/qiantong/wav2letter_experiments/wav2letter-dev/benchmark/trigger.sh $1 $2 1"

# sbatch --job-name=benchmark:8 \
# --output=$2/GPU_8.log \
# --error=$2/GPU_8.err \
# --constraint volta32gb \
# --cpus-per-task=10 \
# --partition=devlab --comment=deadline \
# --time=00:20:00 \
# --mem-per-gpu=50GB \
# --nodes=1 --ntasks-per-node=8 \
# --gpus-per-node=8 \
# --wrap="export NCCL_SOCKET_IFNAME=^docker0,lo; srun bash /private/home/qiantong/wav2letter_experiments/wav2letter-dev/benchmark/trigger.sh $1 $2 8"

# sbatch --job-name=benchmark:16 \
# --output=$2/GPU_16.log \
# --error=$2/GPU_16.err \
# --constraint volta32gb \
# --cpus-per-task=10 \
# --partition=devlab --comment=deadline \
# --time=00:20:00 \
# --mem-per-gpu=50GB \
# --nodes=2 --ntasks-per-node=8 \
# --gpus-per-node=8 \
# --wrap="export NCCL_SOCKET_IFNAME=^docker0,lo; srun bash /private/home/qiantong/wav2letter_experiments/wav2letter-dev/benchmark/trigger.sh $1 $2 16"

sbatch --job-name=benchmark:32 \
--output=$2/GPU_32.log \
--error=$2/GPU_32.err \
--constraint volta32gb \
--cpus-per-task=10 \
--partition=prioritylab --comment=deadline \
--time=00:30:00 \
--mem-per-gpu=60GB \
--nodes=4 --ntasks-per-node=8 \
--gpus-per-node=8 \
--wrap="export NCCL_SOCKET_IFNAME=^docker0,lo; srun bash /private/home/qiantong/wav2letter_experiments/wav2letter-dev/benchmark/trigger.sh $1 $2 32"