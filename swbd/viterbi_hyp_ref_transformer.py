import os
import re
import argparse

# hyp -> ctm
# ref -> stm
# http://www1.icsi.berkeley.edu/Speech/docs/sctk-1.2/infmts.htm#trn_fmt_name_0


parser = argparse.ArgumentParser(description="Librispeech dictionary creation.")
parser.add_argument("--datadir", help="datadir")
parser.add_argument("--test", help="test file")
args = parser.parse_args()

base_dir = args.datadir
test_path = args.test
prefix = os.path.join(base_dir, test_path)

hyp_path = prefix + '.hyp'
ref_path = prefix + '.viterbi.ref'
new_hyp = prefix + '.ctm.hyp'
new_ref = prefix + '.stm.ref'

def unpack_hesitation(line):
    for pattern in ["um hum","um huh","um hm","uh hum","uh huh","uh hm","mm hum","mm huh","mm hm"]:
        out_pattern = "uh-huh"
        line = re.sub(r" {} ".format(pattern), " {} ".format(out_pattern), line)
        line = re.sub(r"^{} ".format(pattern), "{} ".format(out_pattern), line)
        line = re.sub(r" {}$".format(pattern), " {}".format(out_pattern), line)
        line = re.sub(r"^{}$".format(pattern), "{}".format(out_pattern), line)
    return line

with open(hyp_path) as f:
    with open(new_hyp, 'w') as outf:
        for i, line in enumerate(f):
            sentence = line.split('(')[0].strip()
            sentence = re.sub("N", "", sentence)
            sentence = re.sub("L", "", sentence)
            sentence = unpack_hesitation(sentence)
            words = sentence.split()
            for j, word in enumerate(words):
                outf.write(str(i) + ' A ' + str(j) + ' 1 ' + word + ' -6.3\n')


with open(ref_path) as f:
    with open(new_ref, 'w') as outf:
        for i, line in enumerate(f):
            sentence = ' ('.join(line.split(' (')[:-1])
            #sentence = re.sub("\[noise\]", "(hm)", sentence)
            #sentence = re.sub("\[laughter\]", "(hm)", sentence)
            #sentence = sentence.replace("<unk>", "UNKNOWNWORD")
            outf.write(str(i) + ' A ' + str(i) + '-a 0 100 ' + sentence + '\n')
