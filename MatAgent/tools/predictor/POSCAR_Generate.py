from mp_api.client import MPRester
from pymatgen.io.vasp import Poscar
from MatAgent.config import config
prepath = config['predictor']


def POSCAR_Generate(material_id):
    # Your Material Project API key
    api_key = " "
    # Connect to Material Project using mp-api
    mpr = MPRester(api_key)

    structure = mpr.get_structure_by_material_id(material_id, conventional_unit_cell=True)
    # Create POSCAR file
    poscar = Poscar(structure)

    # Save as POSCAR file
    poscar.write_file(f"{prepath}/POSCAR")
