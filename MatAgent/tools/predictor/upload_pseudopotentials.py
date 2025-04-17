# -*- coding: utf-8 -*-
"""
upload_pseudopotentials.py

This script reads a VASP POSCAR file, extracts the elements,
finds the corresponding pseudopotential files (.upf), and uploads these pseudopotential files along with
`config.yaml` and `run.sh` files to the target directory on a remote server.
It also allows passing a command to execute on the remote server via the command line.

Usage:
    python upload_pseudopotentials.py POSCAR target_directory --config config.yaml --run run.sh --hostname <hostname> --username <username> --password <password> --exec_command "<command>"
"""

import sys
import os
import numpy as np
import paramiko
import argparse
import posixpath  # For constructing remote paths

def read_poscar(filename):
    """
    Read the POSCAR file and parse its contents.

    Parameters:
        filename (str): Path to the POSCAR file

    Returns:
        dict: A dictionary containing the element symbols from the POSCAR
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
        lattice.append([float(x) for x in parts[:3]])
        idx += 1
    poscar_data['lattice'] = np.array(lattice)

    # Line 6: Element information
    poscar_data['elements'] = lines[idx].strip().split()
    idx += 1

    # Line 7: Number of atoms of each element
    poscar_data['num_atoms'] = list(map(int, lines[idx].strip().split()))
    idx += 1

    return poscar_data

def execute_remote_command(ssh, command):
    """
    Execute a command in the connected SSH session.

    Parameters:
        ssh (paramiko.SSHClient): The connected SSH client
        command (str): The command to execute

    Returns:
        str: The output of the command
    """
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            print("Error:", error)
        return output
    except Exception as e:
        print(f"Error while executing remote command: {e}")
        return ""

def upload_file(sftp, local_path, remote_path):
    """Upload a single file"""
    try:
        sftp.put(local_path, remote_path)
        print(f"File uploaded successfully: {local_path} -> {remote_path}")
    except Exception as e:
        print(f"File upload failed: {local_path} -> {remote_path}, Error: {e}")

def upload_pseudopotentials(hostname, username, password, target_directory, default_folder, config_file, run_file, ssh):
    """Upload pseudopotential files and configuration files"""
    try:
        sftp = ssh.open_sftp()

        # Ensure the target directory exists
        try:
            sftp.chdir(target_directory)
        except IOError:
            # Directory doesn't exist, create it recursively
            dirs = target_directory.strip('/').split('/')
            current_path = ''
            for dir_part in dirs:
                current_path += f'/{dir_part}'
                try:
                    sftp.chdir(current_path)
                except IOError:
                    sftp.mkdir(current_path)
                    sftp.chdir(current_path)

        # Use posixpath to construct remote paths
        remote_config_path = posixpath.join(target_directory, "config.yaml")
        remote_run_path = posixpath.join(target_directory, "run.sh")

        # Upload config.yaml and run.sh
        upload_file(sftp, config_file, remote_config_path)
        upload_file(sftp, run_file, remote_run_path)

        # Extract elements from POSCAR file
        poscar_data = read_poscar('POSCAR')
        elements = poscar_data['elements']

        # Upload the corresponding pseudopotential files
        for element in elements:
            upf_file = os.path.join(default_folder, f"{element}_ONCV_PBE-1.0.upf")
            if os.path.exists(upf_file):
                remote_upf_path = posixpath.join(target_directory, f"{element}_ONCV_PBE-1.0.upf")
                upload_file(sftp, upf_file, remote_upf_path)
            else:
                print(f"Pseudopotential file not found: {upf_file}")

        sftp.close()

    except Exception as e:
        print(f"Upload failed: {e}")

def main():
    print("begin!!!!!!!!!!!!!!!!!!!!!!")
    parser = argparse.ArgumentParser(description="Upload pseudopotential files and related configuration files")
    parser.add_argument("poscar", help="Path to POSCAR file")
    parser.add_argument("target_directory", help="Target remote directory")
    parser.add_argument("--config", required=True, help="Path to config.yaml file")
    parser.add_argument("--run", required=True, help="Path to run.sh file")
    parser.add_argument("--default_folder", required=True, help="Default path for pseudopotential files")
    parser.add_argument("--hostname", required=True, help="Remote server hostname or IP address")
    parser.add_argument("--username", required=True, help="Remote server username")
    parser.add_argument("--password", required=True, help="Remote server password")
    parser.add_argument("--exec_command", help="Command to execute on the remote server")

    args = parser.parse_args()

    # Create an SSH client instance
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote host
        ssh.connect(args.hostname, username=args.username, password=args.password)
        print(f"Successfully connected to {args.hostname}")

        # Upload pseudopotential files
        upload_pseudopotentials(args.hostname, args.username, args.password,
                                args.target_directory, args.default_folder,
                                args.config, args.run, ssh)

        # Execute remote command
        if args.exec_command:
            print(f"Executing remote command: {args.exec_command}")
            output = execute_remote_command(ssh, args.exec_command)
            print(f"Command output:\n{output}")

    except Exception as e:
        print(f"Error during connection or upload: {e}")
    finally:
        ssh.close()
        print("SSH connection closed.")

if __name__ == "__main__":
    main()
