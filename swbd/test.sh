#!/bin/bash

# $1 = rundir
# $2 = runname
# $3 = checkpoint

log_dir=$2_$3
samplerate=16
ch_list=hub05-callhome.${samplerate}khz.lst
sw_list=hub05-switchboard.${samplerate}khz.lst
rt03_list=rt03s_eval.${samplerate}KHz.lst
binary=/checkpoint/antares/experiments/fl_new_master/exec/bin_master_81c4d8d_Jan12_af373_cuda11/asr/fl_asr_test
config=$4
sclite=/checkpoint/wav2letter/transfer_learning/aws/icassp_paper/ams/sclite/$log_dir
mkdir $sclite

path=/checkpoint/wav2letter/data/
declare -a test=("../../antares/datasets/wsj/lists/nov93dev.lst.fixed" "../../antares/datasets/wsj/lists/nov92.lst.fixed" "librispeech/lists/dev-clean.lst" "librispeech/lists/test-clean.lst" "librispeech/lists/dev-other.lst" "librispeech/lists/test-other.lst" "tedlium/lists/dev.lst.fixed" "tedlium/lists/test.lst.fixed" "commonvoice/lists/dev.lst" "commonvoice/lists/test.lst")

for index in 0 1 2 3 4 5 6 7 8 9
do
  $binary --am=$1/$2/$3 --datadir=$path --test=${test[index]} --sclite=$sclite --flagsfile=$config
done

#swb
$binary --am=$1/$2/$3 --datadir=/checkpoint/wav2letter/data/swbd_lists/noNL --test=$ch_list --sclite=$sclite --flagsfile=$config
$binary --am=$1/$2/$3 --datadir=/checkpoint/wav2letter/data/swbd_lists/noNL --test=$sw_list --sclite=$sclite --flagsfile=$config
$binary --am=$1/$2/$3 --datadir=/checkpoint/vineelkpratap/rt03s_eval/original/lists --test=$rt03_list --sclite=$sclite --flagsfile=$config

cd $sclite
awk '{print $NF,$0}' ../hub05-callhome.ref | sort | cut -f2- -d' ' > ${ch_list}.viterbi.ref
awk '{print $NF,$0}' ../hub05-switchboard.ref | sort | cut -f2- -d' ' > ${sw_list}.viterbi.ref
awk '{print $NF,$0}' ../rt03_list.ref | sort | cut -f2- -d' ' > ${rt03_list}.viterbi.ref

awk '{print $NF,$0}' ${ch_list}.hyp | sort | cut -f2- -d' ' > tmp
mv tmp ${ch_list}.hyp
awk '{print $NF,$0}' ${sw_list}.hyp | sort | cut -f2- -d' ' > tmp
mv tmp ${sw_list}.hyp
awk '{print $NF,$0}' ${rt03_list}.hyp | sort | cut -f2- -d' ' > tmp
mv tmp ${rt03_list}.hyp
rm tmp

python /private/home/qiantong/sclite/viterbi_hyp_ref_transformer.py --datadir=$sclite --test=$ch_list
python /private/home/qiantong/sclite/viterbi_hyp_ref_transformer.py --datadir=$sclite --test=$sw_list
python /private/home/qiantong/sclite/viterbi_hyp_ref_transformer.py --datadir=$sclite --test=$rt03_list

/private/home/qiantong/sclite/sctk-2.4.10/bin/hubscr.pl \
	-p /private/home/qiantong/sclite/sctk-2.4.10/bin \
	-V -l english -h hub5 \
	-g /private/home/qiantong/sclite/en20000405_hub5.glm \
	-r $sclite/${ch_list}.stm.ref \
	$sclite/${ch_list}.ctm.hyp

/private/home/qiantong/sclite/sctk-2.4.10/bin/hubscr.pl \
	-p /private/home/qiantong/sclite/sctk-2.4.10/bin \
	-V -l english -h hub5 \
	-g /private/home/qiantong/sclite/en20000405_hub5.glm \
	-r $sclite/${sw_list}.stm.ref \
	$sclite/${sw_list}.ctm.hyp

/private/home/qiantong/sclite/sctk-2.4.10/bin/hubscr.pl \
	-p /private/home/qiantong/sclite/sctk-2.4.10/bin \
	-V -l english -h hub5 \
	-g /checkpoint/vineelkpratap/rt03s_eval/en20030506.glm \
	-r $sclite/${rt03_list}.stm.ref \
	$sclite/${rt03_list}.ctm.hyp

cat $sclite/*.dtl | grep "Percent Total Error"
