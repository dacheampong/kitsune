#!/usr/bin/env python

""" Main entry of the script.
"""

import argparse
import sys
import os
import gzip
import datetime

import numpy as np
from sklearn.preprocessing import normalize

from ksiga import ksignature
from ksiga import logutil
from ksiga import fsig


USAGE = """
"""

def openner(filename, **kwargs):
    """Try to return a sensible filehandle

    Args:
        filename (string): name of a file. Absolute/Relative path should work.

    Returns: TODO

    """
    if filename.endswith(".gz"):
        return gzip.open(filename, **kwargs)
    else:
        return open(filename, **kwargs)


def main():
    commands = {"index": index,
                "relent": relative_entropy,
                "cre_kmer": cre_kmer,
                "acf": average_common_feature,
                "pair_acf": pair_average_common_feature,
                "acf_kmer": acf_kmer,
                "ofc": observe_feature_frequency,
                "ofc_kmer": ofc_kmer,
                "gen_dmatrix": generate_distance_matrix
               }

    parser = argparse.ArgumentParser(description="Signature for virus",
                                     usage="""ksiga <command> [<args>]

Commands can be:
index <filenames>                     Compute k-mer.
cre_kmer <filename.sig>               Compute optimal k-mer from CRE.
acf_kmer <filename.sig>               Compute optimal k-mer from ACF.
ofc_kmer <filename.sig>               Compute optimal k-mer from OFC.
cre <filename.sig>                    Compute cumulative relative entropy.
acf <filenames.sig>                   Compute average number of common feature between signatures.
ofc <filenames.sig>                   Compute observed feature frequencies.
relent <filename.sig>                 Compute relative entropy.
dmatrix <filenames.sig>               Compute distance matrix.
""")
    parser.add_argument('command')
    args = parser.parse_args(sys.argv[1:2])
    if args.command not in commands:
        parser.print_help()
        sys.exit(1)

    cmd = commands.get(args.command)
    cmd(sys.argv[2:])


def index(args):
    """ Create index for input sequences

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    parser = argparse.ArgumentParser(usage="usage:'%(prog)s index [options]'")
    parser.add_argument("filenames", nargs="+", help="file(s) of sequences")
    parser.add_argument("-k", "--ksize", required=True, type=int)
    parser.add_argument("-o", "--output")
    parser.add_argument("-f", "--force", action="store_true")
    parser.add_argument("-r", "--canon", action="store_true", default=False, help="Use cannonical k-mer representation")
    args = parser.parse_args(args)

    filenames = args.filenames
    ksize = args.ksize
    od = args.output
    force = args.force

    for filename in od:
        if not os.path.exists(filename):
            # TODO: Warn or exit here.
            pass

    # Change this, since using mulitple filename does not make sense.
    #for filename in filenames:
    filename = filenames[0]
    outputName = "{fn}".format(fn=od)
    fInputH = openner(filename, mode="rt")
    ksignature.build_signature(fInputH, ksize, outputName, force)


def relative_entropy(args):
    """ Calculate relative entropy of genome.

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--file", required=True, help="")
    parser.add_argument("-k", "--ksize", required=True, type=int)
    parser.add_argument("-o", "--output")
    args = parser.parse_args(args)

    if args.output is None:
        foh = sys.stdout
    else:
        foh = open(args.output, "w")

    relEntropy = fsig.calculate_relative_entropy(args.file, args.ksize)

    # Print metadata
    print("# input file: {}".format(args.file))
    print("# Run on {}".format(str(datetime.datetime.now())))
    print(relEntropy, file=foh)


def average_common_feature(args):
    """ Calculate an average number of common feature pairwise
        between one genome against others

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    desc = "Calculate average number of common feature"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("filenames", nargs="+", help="file(s) of signature")
    parser.add_argument("-k", "--ksize", required=True, type=int)
    parser.add_argument("-o", "--output")
    parser.add_argument("--lowmem", action="store_true")
    args = parser.parse_args(args)

    filenames = args.filenames
    outF = args.output

    if outF is None:
        outHandle = sys.stdout
    else:
        outHandle = open(outF, "w")

    # Choose to use low mem but slow, or fast but eat memoery like a whale.
    if args.lowmem:
        acf_func = fsig.lowmem_calculate_average_common_feature
    else:
        acf_func = fsig.calculate_average_common_feature
    
    acf = acf_func(args.filenames, args.ksize)
    acf = np.round(acf, 2)

    baseFilenames = (os.path.basename(filename) for filename in filenames)

    for filename, val in zip(baseFilenames, acf):
        print("{}\t{}".format(filename, val), file=outHandle)

def pair_average_common_feature(args):
    """ Calculate an average number of common feature pairwise
        between one genome against others

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    desc = "Calculate average number of common feature"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--in1", help="file(s) of signature")
    parser.add_argument("--in2", help="file(s) of signature")
    parser.add_argument("-k", "--ksize", required=True, type=int)
    parser.add_argument("-o", "--output")
    args = parser.parse_args(args)

    in1 = args.in1
    in2 = args.in2
    ksize = args.ksize
    outF = args.output

    val = fsig.pair_calculate_average_common_feature(in1, in2, ksize)

    if outF is None:
        outHandle = sys.stdout
    else:
        outHandle = open(outF, "w")

    outHandle.write(str(val))


def pair_distance(args):
    """ Calculate an average number of common feature pairwise
        between one genome against others

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    desc = "Calculate average number of common feature"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--in1", help="file(s) of signature")
    parser.add_argument("--in2", help="file(s) of signature")
    parser.add_argument("-k", "--ksize", required=True, type=int)
    parser.add_argument("-d", "--distance", required=True, type=int)
    parser.add_argument("-o", "--output")
    args = parser.parse_args(args)

    in1 = args.in1
    in2 = args.in2
    ksize = args.ksize
    distance = args.distance
    outF = args.output

    val = fsig.pair_calculate_average_common_feature(in1, in2, ksize)

    if outF is None:
        outHandle = sys.stdout
    else:
        outHandle = open(outF, "w")

    outHandle.write(str(val))


def observe_feature_frequency(args):
    """ Calculate an observe feature frequency

    Args:
        args (TODO): TODO

    Returns: TODO

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", help="file(s) of signature")
    parser.add_argument("-k", "--ksize", required=True, type=int)
    parser.add_argument("-w", "--wd", default=os.getcwd())
    parser.add_argument("-o", "--output")
    parser.add_argument("--lowmem", action="store_true")
    args = parser.parse_args(args)

    ksize = args.ksize
    output = args.output

    outputFH = open(output, "w") if output else sys.stdout

    if args.lowmem:
        ofc_func = fsig.lowmem_calculate_ofc_shannon
    else:
        ofc_func = fsig.calculate_ofc_shannon

    shannon_size = ofc_func(args.filenames, ksize)
    outputLine = "{}\t{}".format(ksize, shannon_size)
    print(outputLine, file=outputFH)


def cre_kmer(args):
    """ Calculate optimal k-mer through CRE value.

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    desc = "Calculate k-mer from cumulative relative entropy of all genomes"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("filenames", nargs="+", help="file(s) of signature")
    parser.add_argument("-ks", "--kfrom", required=True, type=int, help="Calculate from k-mer")
    parser.add_argument("-ke", "--kend", required=True, type=int, help="last k-mer")
    parser.add_argument("-o", "--output")
    parser.add_argument("-r", "--report", default="cre.txt")
    args = parser.parse_args(args)

    filenames = args.filenames
    kmerStart = args.kfrom
    kmerEnd = args.kend

    cres = []
    kmers = []
    for filename in filenames:
        logutil.debug("Working on {}".format(filename))
        cre, kmer = fsig.calculate_cre_kmer(filename, kmerStart, kmerEnd)
        cres.append(cre)
        kmers.append(kmer)

    cres = np.vstack(cres)
    # Write report.
    suggestKmer = int(round(np.mean(kmers)))
    print("Suggest k-mer based on CRE value is {}".format(suggestKmer))


def acf_kmer(args):
    """ Calculate an average number of common feature pairwise
        between one genome against others

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    desc = "Calculate optimal k-mer from average number of common feature"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("filenames", nargs="+", help="file(s) of signature")
    parser.add_argument("-ks", "--kfrom", required=True, type=int, help="Calculate from k-mer")
    parser.add_argument("-ke", "--kend", required=True, type=int, help="last k-mer")
    parser.add_argument("-r", "--report", default="acf.txt")
    parser.add_argument("-o", "--output")
    args = parser.parse_args(args)

    filenames = args.filenames
    outF = args.output
    kmerStart = args.kfrom
    kmerEnd = args.kend

    if outF is None:
        outHandle = sys.stdout.buffer
    else:
        outHandle = open(outF, "wb")  # wb for numpy write

    acf, kmers = fsig.calculate_acf_kmer(filenames, kmerStart, kmerEnd)
    acf = np.hstack(acf)
    suggestKmer = int(round(np.mean(kmers)))

    print("Suggest k-mer based on ACF value is {}".format(suggestKmer))


def ofc_kmer(args):
    """ Calculate an observe feature frequency

    Args:
        args (TODO): TODO

    Returns: TODO

    """

    desc = "Calculate average number of common feature"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("filenames", nargs="+", help="file(s) of signature")
    parser.add_argument("-ks", "--kfrom", required=True, type=int, help="Calculate from k-mer")
    parser.add_argument("-ke", "--kend", required=True, type=int, help="last k-mer")
    parser.add_argument("-r", "--report", default="ofc.txt")
    parser.add_argument("-o", "--output")
    args = parser.parse_args(args)

    filenames = args.filenames
    outF = args.output
    kmerStart = args.kfrom
    kmerEnd = args.kend

    percentage, suggestKmer = fsig.calculate_ofc_kmer(filenames, kmerStart, kmerEnd)

    print("Suggest k-mer based on OCF value is {}".format(suggestKmer))

    outF = args.output
    if outF is None:
        outHandle = sys.stdout.buffer
    else:
        outHandle = open(outF, "wb")  # wb for numpy write

def generate_distance_matrix(args):
    """Generate distance matrix base on k-mer

    The output will 

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    import ksiga.fsig as fsig
    from ksiga import distance

    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", help="file(s) of signature")
    parser.add_argument("-k", "--ksize", required=True, type=int)
    parser.add_argument("-o", "--output")
    parser.add_argument("-t", "--n_thread", type=int, default=1)
    parser.add_argument("-d", "--distance", default="euclid")
    args = parser.parse_args(args)

    fn = distance.get_distance_function(args.distance)

    # Delegate to function in distance.
    filenames = args.filenames
    ksize = args.ksize
    outF = args.output

    if outF is None:
        outHandle = sys.stdout.buffer
    else:
        outHandle = open(outF, "wb")  # wb for numpy write


    # Check for existence of file.
    for filename in args.filenames:
        if not os.path.exists(filename):
            # TODO: Do something about this
            pass

    csr_matrix = fsig.rebuild_sparse_matrix(filenames, ksize)
    rowNum = csr_matrix.shape[0]

    # Normalize data before calculate distance
    csr_matrix_norm = normalize(csr_matrix, norm='l1', axis=1)

    result = fn(csr_matrix_norm)
    np.savetxt(outHandle, result)

    # Output for file
    flistH = open("{}.inputlist".format(outF), 'w')
    for f in filenames:
        flistH.write(f)
        flistH.write("\n")

    # Logging
    logutil.notify("Result is written to {}".format(outF))
    logutil.notify("Filelist is written to {}".format(outF))
    sys.exit(0)


def lowmem_generate_distance_matrix(args):
    """Generate distance matrix base on k-mer. Unlike the normal version counterpart, it relied heavily on looping.

    Args:
        args (TODO): TODO

    Returns: TODO

    """
    import ksiga.fsig as fsig
    from ksiga import distance

    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", help="file(s) of signature")
    parser.add_argument("-k", "--ksize", required=True, type=int)
    parser.add_argument("-o", "--output")
    parser.add_argument("-t", "--n_thread", type=int, default=1)
    parser.add_argument("-d", "--distance", default="euclid")
    args = parser.parse_args(args)

    fn = distance.get_distance_function(args.distance)
    # Temporary array.
