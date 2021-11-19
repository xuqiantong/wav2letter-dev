#!/bin/bash

binary=$1
log_dir=$2
world_size=$3

if [ $world_size == 1 ]; then
  $binary --log_verbose > $log_dir/GPU_$world_size.log
else
  mkdir -p $log_dir/rndv_$world_size
  $binary --distributed_enable=true --distributed_world_rank=${SLURM_PROCID} --distributed_world_size=$world_size --distributed_rndv_filepath=$log_dir/rndv_$world_size --log_verbose
  rm -rf $log_dir/rndv_$world_size
fi