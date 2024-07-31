from Bio import SeqIO

ALIGN_FORMAT: dict[str, str] = {
    "uniprot.sto": "stockholm",
    "bfd_uniref_hits.a3m": "fasta",
    "mgnify_hits.sto": "stockholm",
    "pdb_hits.sto": "stockholm",
    "uniref90_hits.sto": "stockholm",
}

def num_unique_msa(msa_file_path: str) -> int:
    """
    Return the number of unique alignments from the MSA's used to generate features for the protein

    Parameters:
        msa_file_path: The path to the MSA files (str)

    Returns:
        Number of unique sequences from the MSA's used to generate features for the protein (int)
    """
    msa_sequences = []


    # For all the MSA files, parse the sequences and add them to the set
    for align_file, format in ALIGN_FORMAT.items():
        align = SeqIO.parse(f"{msa_file_path}/{align_file}", format)

        for record in align:
            msa_sequences.append(record.seq)


    return len(set(msa_sequences))
