import argparse
import random

def perturb_parameters(args):
    random_01 = random.uniform(0, 1)
    args.lmweight = 0.0 + random_01 * 1.0

    random_01 = random.uniform(0, 1)
    args.wordscore = -8.0 + random_01 * 15.0

    random_01 = random.uniform(0, 1)
    args.eosscore = -8.0 + random_01 * 6.0
    
    return args
