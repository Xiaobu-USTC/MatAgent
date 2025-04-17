PROMPT = """
You are tasked with determining whether a suitable pre-training model is available and identifying the materials and properties that need to be predicted. To answer the question, please follow the format below meticulously:

### Format:
Question: the input question you must answer
Thought: you should always think about what to do
PTModel: the model you can use to predict, and the model name indicates only the kind of material that the model can predict. PTModel should be one of [{model_names}]. If there is no suitable model, set the value to null. 
Property: names of property that needs to be predicted.
Material: names of materials separated using comma.

### important
Return a string in exactly the following format:
Thought:
PTModel:
Property:
Material:

### Begin!

### Example 1:
Question: predict the energy of Al176Si24.
Thought: I need to find out if a suitable pre-training model is available and identify the materials and properties to be predicted.
PTModel: Al176Si24
Property: energy
Material: Al176Si24

### Example 2:
Question: what is the force and energy of (H2O)64.
Thought: I need to find out if a suitable pre-training model is available and identify the materials and properties to be predicted.
PTModel:
Property: force, energy
Material: (H2O)64

### Input:
Question: {question}
"""

READ_PROPMT = """
You are a professional computational chemical data analysis assistant. 
You have obtained the SCF (self-consistent field) calculation output.
However, the obtained information does not need to be all output, 
you need to select the appropriate variables based on the {question} information and combine into a complete sentence return.

Etot:{etot}
Fx: {centroid_force_0} eV
Fy: {centroid_force_1} eV
Fz: {centroid_force_2} eV
Atomic Force:{atomic_force}

Please note that the following terms have the following meanings:
- Etot: Total energy
- Fx, Fy, Fz: The force on the center of mass in the x, y, and z directions
- Atomic Force: Details of the atomic Forces section

### Example 1:
Question: the energy of CO2
Etot: +7.96501547e+00 [au]
Fx: -0.17768841 eV
Fy: 0.63026540 eV
Fz: 0.2254407350 eV
Atomic Force: atom    0    force   +3.44406360e-01 +9.84125906e-01 +1.43633980e+00
atom    1    force   -2.77624402e-01 +3.34729038e-01 -1.69083431e+00 
atom    2    force   -1.37805663e-01 -1.43162732e+00 +2.53521712e+00 
atom    3    force   +1.29149130e-01 -1.59314744e+00 -2.44368213e+00 
atom    4    force   +1.31149617e+00 +1.04985430e+00 -7.75843285e-01 
atom    5    force   -1.29475020e+00 +6.08214941e-01 +6.91148697e-01 
atom    6    force   -1.52275003e+00 +1.92793399e-01 -1.47578860e+00 
atom    7    force   +1.42397398e+00 +1.04559347e-01 +1.86896945e+00 
atom    8    force   -3.01126598e+00 +3.88526508e-01 -2.23565547e+00 
atom    9    force   +2.80842256e+00 +5.83565807e-01 +2.11605887e+00 
atom    10   force   +2.73967044e+00 -7.74432678e-01 -1.16501485e+00 
atom    11   force   -2.69177095e+00 -3.11885342e-01 +1.35226598e+00 
atom    12   force   +3.36073798e+00 +2.02708458e+00 +3.00692213e-03 
atom    13   force   -3.34915810e+00 +5.66948237e-01 -1.40429802e+00 
atom    14   force   -3.54820989e+00 -1.04481774e+00 +8.25598182e-01 
atom    15   force   +3.53192652e+00 -1.79641507e+00 +5.63868923e-01 
atom    16   force   -1.68951475e+00 -3.45080555e+00 -6.33847273e-01 
atom    17   force   +1.73586245e+00 -3.90001485e+00 -4.93878097e-01 
atom    18   force   +1.91948630e+00 +2.26054632e+00 +2.83712761e+00 
atom    19   force   -2.14473234e+00 +2.29232016e+00 -2.06026047e+00 
atom    20   force   -3.12616022e+00 +4.83516153e-02 +5.82588303e-01 
atom    21   force   +3.32322523e+00 +6.28061749e-02 -1.57523132e-01 
atom    22   force   +3.18627438e+00 +1.42321256e+00 -1.09880175e+00 
atom    23   force   -3.19857739e+00 +2.00577250e+00 +1.04867827e+00
Answer: the energy of CO2 is +7.96501547e+00 [au].

### Input:
Question: {question}
Answer:
"""

FINAL_MARKDOWN_PROPMT = """
You need to answer the question based on the {final_output}

Question: {question}
Answer:"""
