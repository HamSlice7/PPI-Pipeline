from Bio import SeqIO
import os


def num_unique_msa(msa_file_path):

    """
    Input: MSA file path (string)
    Output: Number of unique sequences from the MSA's used to generate features for the protein (int)
    """

    #Initializing a list to hold all the sequences from the MSA's of a seq object type
    msa_sequences = []

    #Appending the homologous sequences found in the uniprot database
    align_uniprot = SeqIO.parse(f"{msa_file_path}/uniprot.sto", "stockholm")

    for record in align_uniprot:
        msa_sequences.append(record.seq)

    #Appending the homologous sequences from BDF database

    align_bfd = SeqIO.parse(f"{msa_file_path}/bfd_uniref_hits.a3m", "fasta")

    for record in align_bfd:
        msa_sequences.append(record.seq)

    #Appending the homologous sequences from the MGnify database

    align_mgnify = SeqIO.parse(f"{msa_file_path}/mgnify_hits.sto", "stockholm")

    for record in align_mgnify:
        msa_sequences.append(record.seq)

    #Appending the homologous sequences from the PDB database
    align_pdb = SeqIO.parse(f"{msa_file_path}/pdb_hits.sto", "stockholm")

    for record in align_pdb:
        msa_sequences.append(record.seq)


    #Appending the homologous sequences from the Uniref90 database
    align_uniref90 = SeqIO.parse(f"{msa_file_path}/uniref90_hits.sto", "stockholm")

    for record in align_uniref90:
        msa_sequences.append(record.seq)


    return len(set(msa_sequences))
