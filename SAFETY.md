# Safety and Dual-Use Policy — parafold (TCR-pMHC Structural Predictor)

## What this project is

parafold is a research scaffold for **TCR-pMHC structural prediction** using Boltz-2 as the
base model with a planned HLA-allele-conditioned head and repertoire ensemble sampler. Its
outputs are **structural coordinates and confidence scores** — not functional or mechanistic
claims about immunological outcomes.

## Nature of predictions: structural, not functional

parafold predicts **3-D structure** of T-cell receptor / peptide-MHC complexes. This is
fundamentally different from:

- Predicting whether a peptide *activates* a specific T-cell clone.
- Predicting *in vivo* immunogenicity, tolerance, or autoimmunity outcomes.
- Designing peptides to *evade* immune surveillance.
- Engineering pathogens to avoid MHC presentation.

The tool provides geometric models. Downstream biological interpretation — including any
functional inference — is the responsibility of the scientist performing the analysis.

## Biosafety notice

pMHC-presentation modelling is dual-use by nature: the same structural understanding that
informs vaccine design can, in principle, inform immune-evasion strategies. This project
does **not** include:

- Pathogen sequence databases or functionality for pathogen design assistance.
- Enumeration of high-affinity peptides from select agents or potential pandemic pathogens
  as catalogued by the CDC/USDA Select Agent Program.
- Tools to identify MHC-presentation blind spots for use in immune-evasion.

Any wet-lab work that follows from parafold structural predictions — including synthesis of
novel peptides or modification of pathogen antigens — may fall under institutional biosafety
oversight requirements. Researchers are strongly encouraged to:

1. Submit proposed experiments to their institutional **Institutional Biosafety Committee
   (IBC)** before conducting wet-lab work informed by these predictions.
2. Comply with the [NIH Guidelines for Research Involving Recombinant or Synthetic Nucleic
   Acid Molecules](https://osp.od.nih.gov/biotechnology/nih-guidelines/) where applicable.
3. Follow CDC Select Agent Program requirements if working with select agents or toxins:
   <https://www.selectagents.gov/>

## Contribution policy

Pull requests that add any of the following will be closed:

- Databases or loaders for select-agent or potential-pandemic-pathogen sequences not
  otherwise publicly available through regulated channels (e.g., NCBI with standard access).
- Enumeration pipelines designed to exhaustively mine MHC-evasion epitopes.
- Integration with design tools explicitly intended for pathogen engineering.

## Upstream model license

parafold wraps [Boltz-2](https://github.com/jwohlwend/boltz) via a subprocess interface.
Users are responsible for complying with the Boltz-2 license and any usage restrictions of
the model checkpoints they download separately. parafold does not redistribute Boltz-2 weights.

## Responsible disclosure

If you identify a safety-relevant misuse of this software, please open a GitHub Security
Advisory (private) rather than a public issue.

## References

- Boltz-2: Wohlwend et al., "Boltz-2: Towards Accurate and Efficient Binding Affinity
  Prediction." <https://github.com/jwohlwend/boltz>
- CDC Select Agent Program: <https://www.selectagents.gov/>
- NIH Biosafety Guidelines: <https://osp.od.nih.gov/biotechnology/nih-guidelines/>
