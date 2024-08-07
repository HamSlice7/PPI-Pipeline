# PPI-Pipeline

Instructions for use:
- Clone repository in a HPC environment
- Create a fasta file called 'bait.fasta' containing the amino acid sequence for the target peptidase. The name of the peptidase should start with a ">" followed by the amino acid sequence on a new line. See the example bait.fasta file.
- Create a fasta file called 'candidates.fasta' containing the amino acid sequences for the candidate compeitive inhibitors for the target peptidase. The name of each inhibitor should start with a ">" character followed by the amino acid sequence on a new line. See the example candidates.fasta file.
- To start the pipeline, type the command 'bash activate.sh' with the following flags:
  -a: amino acid number of an active site residue
  -b: location of the "bait.fasta" file
  -c: location of the "candidates.fasta" file.
- Example command: 'bash activate.sh -a 32 -b bait.fasta -c candidates.fasta'

Citations:

Cock, P. J. A., Antao, T., Chang, J. T., Chapman, B. A., Cox, C. J., Dalke, A., Friedberg, I., Hamelryck, T., Kauff, F., Wilczynski, B., & de Hoon, M. J. L. (2009). Biopython: Freely available Python tools for computational molecular biology and bioinformatics. Bioinformatics, 25(11), 1422–1423. https://doi.org/10.1093/bioinformatics/btp163

Evans, R., O’Neill, M., Pritzel, A., Antropova, N., Senior, A., Green, T., Žídek, A., Bates, R., Blackwell, S., Yim, J., Ronneberger, O., Bodenstein, S., Zielinski, M., Bridgland, A., Potapenko, A., Cowie, A., Tunyasuvunakool, K., Jain, R., Clancy, E., … Hassabis, D. (2022). Protein complex prediction with AlphaFold-Multimer (p. 2021.10.04.463034). bioRxiv. https://doi.org/10.1101/2021.10.04.463034

Jumper, J., Evans, R., Pritzel, A., Green, T., Figurnov, M., Ronneberger, O., Tunyasuvunakool, K., Bates, R., Žídek, A., Potapenko, A., Bridgland, A., Meyer, C., Kohl, S. A. A., Ballard, A. J., Cowie, A., Romera-Paredes, B., Nikolov, S., Jain, R., Adler, J., … Hassabis, D. (2021). Highly accurate protein structure prediction with AlphaFold. Nature, 596(7873), 583–589. https://doi.org/10.1038/s41586-021-03819-2

Kim, A.-R., Hu, Y., Comjean, A., Rodiger, J., Mohr, S. E., & Perrimon, N. (2024). Enhanced Protein-Protein Interaction Discovery via AlphaFold-Multimer. https://doi.org/10.1101/2024.02.19.580970

Mitternacht, S. (2016). FreeSASA: An open source C library for solvent accessible surface area calculations. F1000Research, 5, 189. https://doi.org/10.12688/f1000research.7931.1

Yu, D., Chojnowski, G., Rosenthal, M., & Kosinski, J. (2023). AlphaPulldown—A python package for protein–protein interaction screens using AlphaFold-Multimer. Bioinformatics, 39(1), btac749. https://doi.org/10.1093/bioinformatics/btac749


