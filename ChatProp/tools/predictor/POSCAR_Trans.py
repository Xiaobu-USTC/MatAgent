# -*- coding: utf-8 -*-
"""
convert_poscar.py

This script reads a VASP POSCAR file, converts it into the specified format, 
and outputs it to a new file `POSCAR_new`.

Usage:
    python convert_poscar.py input_POSCAR_file output_POSCAR_new_file [--orthogonalize]
"""

import sys
import numpy as np
import argparse

def read_poscar(filename):
    """
    Read the POSCAR file and parse its contents.

    Parameters:
        filename (str): Path to the POSCAR file

    Returns:
        dict: A dictionary containing the POSCAR data
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    poscar_data = {}
    idx = 0

    # Line 1: Comment (stored)
    poscar_data['comment'] = lines[idx].strip()
    idx += 1

    # Line 2: Scale factor
    try:
        poscar_data['scale'] = float(lines[idx].strip())
    except ValueError:
        raise ValueError("Line 2 must be the scale factor (a float).")
    idx += 1

    # Lines 3-5: Lattice vectors
    lattice = []
    for i in range(3):
        parts = lines[idx].strip().split()
        if len(parts) < 3:
            raise ValueError(f"Line {idx+1} has insufficient lattice vector data.")
        lattice.append([float(x) for x in parts[:3]])
        idx += 1
    poscar_data['lattice'] = np.array(lattice)

    # Line 6: Element symbols (optional)
    elements_line = lines[idx].strip().split()
    if all(item.isalpha() for item in elements_line):
        poscar_data['elements'] = elements_line
        idx += 1
    else:
        # If no element symbols line, infer from atomic coordinates
        poscar_data['elements'] = []

    # Line 7 or Line 6: Number of atoms of each element
    counts_line = lines[idx].strip().split()
    if not all(item.isdigit() for item in counts_line):
        raise ValueError(f"Line {idx+1} must contain the number of atoms for each element (integers).")
    poscar_data['counts'] = [int(x) for x in counts_line]
    idx += 1

    # Line 8: Coordinate type (Direct or Cartesian)
    coord_type = lines[idx].strip().capitalize()
    if coord_type not in ['Direct', 'Cartesian']:
        raise ValueError(f"Line {idx+1} must specify coordinate type as 'Direct' or 'Cartesian'.")
    poscar_data['coord_type'] = coord_type
    idx += 1

    # Following lines: Atomic coordinates
    total_atoms = sum(poscar_data['counts'])
    coordinates = []
    for _ in range(total_atoms):
        if idx >= len(lines):
            raise ValueError("Insufficient atomic coordinate lines.")
        parts = lines[idx].strip().split()
        if len(parts) < 3:
            raise ValueError(f"Line {idx+1} has insufficient atomic coordinate data.")
        x, y, z = map(float, parts[:3])
        elem = parts[3] if len(parts) >= 4 else None
        coordinates.append({
            'x': x,
            'y': y,
            'z': z,
            'element': elem
        })
        idx += 1
    poscar_data['coordinates'] = coordinates

    return poscar_data

def orthogonalize_lattice(lattice):
    """
    Orthogonalize the lattice vectors.

    Parameters:
        lattice (np.ndarray): Original lattice vectors (3x3)

    Returns:
        np.ndarray: Orthogonalized lattice vectors (3x3)
    """
    # Use the Gram-Schmidt process for orthogonalization
    a = lattice[0]
    b = lattice[1]
    c = lattice[2]

    # Orthogonalization steps
    a_ortho = a
    b_ortho = b - np.dot(b, a_ortho) / np.dot(a_ortho, a_ortho) * a_ortho
    c_ortho = c - np.dot(c, a_ortho) / np.dot(a_ortho, a_ortho) * a_ortho - np.dot(c, b_ortho) / np.dot(b_ortho, b_ortho) * b_ortho

    orthogonal_lattice = np.array([a_ortho, b_ortho, c_ortho])
    return orthogonal_lattice

def set_tolerance(lattice, tol=1e-6):
    """
    Set values smaller than tolerance to zero in lattice vectors.

    Parameters:
        lattice (np.ndarray): Lattice vectors (3x3)
        tol (float): Tolerance value, default is 1e-6

    Returns:
        np.ndarray: Processed lattice vectors
    """
    lattice[np.abs(lattice) < tol] = 0.0
    return lattice

def write_new_format(poscar_data, output_filename, orthogonalize=False, tol=1e-6):
    """
    Write the parsed POSCAR data to a new formatted file.

    Parameters:
        poscar_data (dict): Parsed POSCAR data
        output_filename (str): Output file path
        orthogonalize (bool): Whether to orthogonalize the lattice
        tol (float): Tolerance value to set near-zero values to zero
    """
    lattice = poscar_data['lattice'].copy()

    if orthogonalize:
        lattice = orthogonalize_lattice(lattice)
        lattice = set_tolerance(lattice, tol=tol)
        print("Lattice has been orthogonalized and tolerance applied.")
    else:
        # Check orthogonality
        non_orthogonal = not np.allclose(lattice, np.diag(np.diagonal(lattice)), atol=tol)
        if non_orthogonal:
            print("Warning: Non-orthogonal lattice detected.")
            # Apply tolerance to set near-zero values to zero
            lattice = set_tolerance(lattice, tol=tol)

    with open(output_filename, 'w') as f:
        # Write header
        f.write("sea\n")

        # Write scale factor
        f.write(f"{poscar_data['scale']}\n")

        # Write lattice vectors, formatted to 10 decimal places
        for vec in lattice:
            formatted_vec = "  " + " ".join([f"{num:.10f}" for num in vec])
            f.write(f"{formatted_vec}\n")

        # Write element symbols
        if poscar_data['elements']:
            elements_str = "  " + "  ".join(poscar_data['elements'])
        else:
            # If no element symbols, infer from atomic coordinates
            unique_elements = sorted(
                list(set([atom['element'] for atom in poscar_data['coordinates'] if atom['element']])))
            elements_str = "  " + "  ".join(unique_elements)
            poscar_data['elements'] = unique_elements  # Update elements list
        f.write(f"{elements_str}\n")

        # Write the number of atoms of each element
        counts_str = "  " + "  ".join([str(count) for count in poscar_data['counts']])
        f.write(f"{counts_str}\n")

        # Write coordinate type
        f.write(f"{poscar_data['coord_type']}\n")

        # Write atomic coordinates, formatted to 9 decimal places
        for atom in poscar_data['coordinates']:
            x = f"{atom['x']:.9f}"
            y = f"{atom['y']:.9f}"
            z = f"{atom['z']:.9f}"
            f.write(f"     {x}    {y}    {z}\n")

    print(f"Conversion complete. Output file is {output_filename}")

def main():
    parser = argparse.ArgumentParser(description="Convert a VASP POSCAR file to the specified format.")
    parser.add_argument('input_file', help="Input POSCAR file path")
    parser.add_argument('output_file', help="Output file path")
    parser.add_argument('--orthogonalize', action='store_true', help="Whether to orthogonalize the lattice")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    orthogonalize = args.orthogonalize

    try:
        # Read POSCAR file
        poscar_data = read_poscar(input_file)

        # Write to the new formatted file
        write_new_format(poscar_data, output_file, orthogonalize=orthogonalize)

    except Exception as e:
        print(f"Error occurred during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
