import os
import re
import pathlib

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', type=str)
parser.add_argument('--logdir', type=pathlib.Path)
parser.add_argument('--keywords', type=str, default='lmweight,wordscore,eosscore')


if __name__ == '__main__':
    args = parser.parse_args()

    log_dir = os.path.join(args.logdir, args.prefix)
    log_files = [f for f in os.listdir(log_dir)
            if os.path.isfile(os.path.join(log_dir, f)) and ".err" == f[-4:]]

    results = {}
    for log_file in log_files:
        err_path = os.path.join(log_dir, log_file)
        with open(err_path) as f:
            lines = f.readlines()
            try:
                m = re.search('.* WER: (.+?), .*', lines[-1])
                wer = float(m.group(1))
                m = re.search('.* LER: (.+?)]', lines[-1])
                ler = float(m.group(1))

                for line in lines:
                    if not line.startswith('--flagfile=;'):
                        continue

                    keywords = {}
                    for k in args.keywords.split(','):
                        m = re.search('.* --{}=(.+?); .*'.format(k), line)
                        v = m.group(1)
                        keywords[k] = v

                    break

                results[log_file] = (wer, ler, keywords)
            except:
                pass

    sorted_res = sorted(results.items(), key=lambda x: x[1][0])
    print(len(sorted_res), '/', len(log_files))
    for k, v in sorted_res[:10]:
        print(k, "WER:", v[0], "LER:", v[1], "params:", v[2])
