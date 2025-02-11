import re
import json
from pathlib import Path

# Complete periodic table mapping: element symbol -> atomic number
periodic_table = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8,
    'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
    'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22,
    'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29,
    'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36,
    'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43,
    'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
    'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57,
    'Ce': 58, 'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64,
    'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71,
    'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78,
    'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
    'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92,
    'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99,
    'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105,
    'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109, 'Ds': 110, 'Rg': 111,
    'Cn': 112, 'Fl': 114, 'Lv': 116, 'Ts': 117, 'Og': 118
}

def parse_elements(formula):
    """
    Parses a chemical formula to extract unique elements sorted by atomic number descending.

    Args:
        formula (str): Chemical formula (e.g., "H2O", "AlO2").

    Returns:
        list: Sorted list of unique element symbols.
    """
    # Regular expression to match element symbols
    pattern = r'([A-Z][a-z]?)'
    elements = re.findall(pattern, formula)

    # Remove duplicates while preserving order
    unique_elements = []
    for e in elements:
        if e not in unique_elements:
            unique_elements.append(e)

    # Validate elements
    for e in unique_elements:
        if e not in periodic_table:
            raise ValueError(f"Unrecognized element symbol: {e}")

    # Sort elements by atomic number descending
    sorted_elements = sorted(unique_elements, key=lambda x: periodic_table[x], reverse=True)

    return sorted_elements

def generate_input_json(formula, output_path="input.json"):
    """
    Generates an input.json file with the same structure as provided,
    updating the 'model.type_map' based on the given chemical formula.

    Args:
        formula (str): Chemical formula (e.g., "H2O", "AlO2").
        output_path (str or Path): Path to save the generated input.json.

    Returns:
        None
    """
    elements = parse_elements(formula)

    # Define the JSON structure
    input_json = {
        "_comment": "that's all",
        "model": {
            "type_map": elements,
            "descriptor": {
                "type": "se_e2_a",
                "sel": [
                    46,
                    92
                ],
                "rcut_smth": 0.5,
                "rcut": 6.0,
                "neuron": [
                    25,
                    50,
                    100
                ],
                "resnet_dt": False,
                "axis_neuron": 16,
                "seed": 1,
                "_comment": " that's all"
            },
            "fitting_net": {
                "neuron": [
                    240,
                    240,
                    240
                ],
                "resnet_dt": True,
                "seed": 1,
                "_comment": " that's all"
            },
            "_comment": " that's all"
        },
        "learning_rate": {
            "type": "exp",
            "decay_steps": 20000,
            "start_lr": 0.001,
            "stop_lr": 1e-08,
            "_comment": "that's all"
        },
        "loss": {
            "type": "ener",
            "start_pref_e": 0.02,
            "limit_pref_e": 1,
            "start_pref_f": 1000,
            "limit_pref_f": 1,
            "start_pref_v": 0,
            "limit_pref_v": 0,
            "_comment": " that's all"
        },
        "training": {
            "training_data": {
                "systems": [
                    "./npy_data"
                ],
                "batch_size": "auto",
                "_comment": "that's all"
            },
            "validation_data": {
                "systems": [
                    "./npy_data"
                ],
                "batch_size": "auto",
                "_comment": "that's all"
            },
            "numb_steps": 10000,
            "seed": 1,
            "disp_file": "lcurve.out",
            "disp_freq": 2000,
            "numb_test": 4,
            "save_freq": 1000,
            "save_ckpt": "model.ckpt",
            "disp_training": True,
            "time_training": True,
            "profiling": False,
            "_comment": "that's all"
        }
    }

    # Save the JSON to the specified path
    output_path = Path(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(input_json, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Example chemical formulas
    formulas = ["H2O", "AlO2", "C6H12O6", "Fe2O3"]

    for formula in formulas:
        try:
            generate_input_json(formula, output_path=f"input.json")
        except Exception as e:
            print(f"Error processing formula '{formula}': {e}")
