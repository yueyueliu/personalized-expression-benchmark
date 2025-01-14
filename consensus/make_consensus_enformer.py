import argparse
from optparse import OptionParser
import subprocess
import re
import os
import sys
import multiprocessing as mp
import pyfaidx
from itertools import product
import json

REF_DIR = "ref"
INDS = "inds"
vcf_dir = "data/variants"
OUT_DIR = "/storage/zhangkaiLab/liuyue87/Projects/personalized-expression-benchmark/consensus/seq"
SEQUENCE_LENGTH = 393216
INTERVAL = 114688


def get_vcf(chr):
    return f"{vcf_dir}/GEUVADIS.chr{chr}.cleaned.vcf.gz"


def get_items(file):
    with open(file, "r") as f:
        return f.read().splitlines()


def get_sample_files(sample, gene_id):
    return f"{OUT_DIR}/{INDS}/{sample}/{gene_id}.1pIu.fa", f"{args.out_dir}/{INDS}/{sample}/{gene_id}.2pIu.fa"

def get_index_files(sample, gene_id):
    return f"{OUT_DIR}/{INDS}/{sample}/{gene_id}.1pIu.fai", f"{args.out_dir}/{INDS}/{sample}/{gene_id}.2pIu.fai"

def generate_ref(ref_fasta_dir, gene):
    # gene format: 'ENSG00000263280,16,2917619,AC003965.1,-'
    gene_id, chr, tss, _, strand = gene.split(",")
    print(f"#### Starting reference fasta for {gene_id} ####")
    out_file = f"{args.out_dir}/{REF_DIR}/{gene_id}.fa"
    # command = "module load samtools"
    # subprocess.run(command, shell=True, executable='/bin/bash')
    with open(out_file, "w") as f:
        start, end = int(tss) - SEQUENCE_LENGTH // 2, int(tss) + SEQUENCE_LENGTH // 2 - 1
#        start, end = int(tss) - INTERVAL // 2, int(tss) + INTERVAL // 2
        ref_command = f"module load samtools; samtools faidx {ref_fasta_dir} chr{chr}:{start}-{end} -o {out_file}"
        subprocess.run(ref_command, shell=True)


def generate_consensus(pair):
    gene, sample = pair
    gene_id, chr, tss, _, strand = gene.split(",")
    out1, out2 = get_sample_files(sample, gene_id)
    ind1, ind2 = get_index_files(sample, gene_id)

    print(f"#### Starting consensus fasta for {gene_id}, Sample {sample} ####")
    hap1 = f"module load bcftools; bcftools consensus -s {sample} -f {OUT_DIR}/{REF_DIR}/{gene_id}.fa -I -H 1pIu {get_vcf(chr)} > {out1}"
    hap2 = f"module load bcftools; bcftools consensus -s {sample} -f {OUT_DIR}/{REF_DIR}/{gene_id}.fa -I -H 2pIu {get_vcf(chr)} > {out2}"
    subprocess.run(hap1, shell=True)
    subprocess.run(hap2, shell=True)
    pyfaidx.Faidx(out1)
    pyfaidx.Faidx(out2)

def make_dirs(args,samples):
    for sample in samples:
        if not os.path.exists(f"{args.out_dir}/{INDS}/{sample}"):
            os.makedirs(f"{args.out_dir}/{INDS}/{sample}")

if __name__ == "__main__":
    """
    Create individual fasta sequences

    Arguments:
    - ref_fasta_dir: reference fasta directory
    - vcf_dir: directory containing VCF files 
    - genes_csv: file containing Ensembl gene IDs, chromosome, TSS position, gene symbol, and strand
    - sample_file: file containing individuals names
    """
    with open("/storage/zhangkaiLab/liuyue87/Projects/personalized-expression-benchmark/parm/make_consensus_enformer.json","r") as f:
        param = json.load(f)

    parser = argparse.ArgumentParser()
    # Required parameters
    parser.add_argument(
        "--ref_fasta_dir",default=param['ref_fasta_dir'], type = str,
    )
    parser.add_argument(
        "--vcf_dir",default=param['vcf_dir'], type = str,
    )
    parser.add_argument(
        "--genes_file",default=param['genes_file'], type = str,
    )
    parser.add_argument(
        "--sample_file",default=param['sample_file'], type = str,
    )
    parser.add_argument(
        "--out_dir",default=param['out_dir'], type = str,
    )
    f.close()

    args = parser.parse_args()

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    if not os.path.exists(args.out_dir + "/" + REF_DIR):
        os.makedirs(args.out_dir + "/" + REF_DIR)
    if not os.path.exists(args.out_dir + "/" + INDS):
        os.makedirs(args.out_dir + "/" + INDS)

    genes = get_items(args.genes_file)
    # for gene in genes:
    #     generate_ref(args.ref_fasta_dir, gene)

    samples = get_items(args.sample_file)

    #make sample directories
    make_dirs(args,samples)

    pool = mp.Pool(processes=mp.cpu_count())
    with pool:
        pairs = product(genes, samples)
        pool.map(generate_consensus, pairs)



