import subprocess
import sys
import os
from ChatProp.tools.predictor.get_ids import get_ids
from ChatProp.tools.predictor.POSCAR_Generate import POSCAR_Generate
from ChatProp.config import config
class FP_Predictor():
    def __init__(self, mat):
        self.mat = mat
        

    def run_command(self, command, cwd=None):
        """
        Execute a command line command and handle possible errors.

        Parameters:
            command (str): The command to be executed.
            cwd (str, optional): The working directory where the command is executed.

        Returns:
            str: The standard output of the command.
        """
        # print(f"\nExecuting command: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,  # Return bytes instead of a string
                cwd=cwd
            )
            # Decode with utf-8, replace errors
            stdout_decoded = result.stdout.decode('utf-8', errors='replace')
            stderr_decoded = result.stderr.decode('utf-8', errors='replace')
            # print(stdout_decoded)
            if stderr_decoded:
                # print(stderr_decoded, file=sys.stderr)
                return stdout_decoded
        except subprocess.CalledProcessError as e:
            stderr_decoded = e.stderr.decode('utf-8', errors='replace')
            # print(f"Command execution failed: {command}\nError message:\n{stderr_decoded}", file=sys.stderr)
            sys.exit(1)
        except UnicodeDecodeError as e:
            # print(f"Decoding error: {e}\nCommand: {command}", file=sys.stderr)
            sys.exit(1)

    def cal_fp_predictor(self):
        prepath = config['predictor']
        material_id = get_ids(self.mat)
        
        # Step 1: Generate POSCAR_old
        # print("Step 1: Run POSCAR_Generate.py to generate POSCAR")
        POSCAR_Generate(material_id[0])

        # Step 2: Convert POSCAR_old to POSCAR and orthogonalize
        # print("\nStep 2: Run POSCAR_Trans.py to convert POSCAR_old to POSCAR and orthogonalize")
        self.run_command(f"python {prepath}/POSCAR_Trans.py {prepath}/POSCAR {prepath}/POSCAR --orthogonalize")

        # Step 3: Run pwdft_input.py to generate config.yaml
        # print("\nStep 3: Run pwdft_input.py to generate config.yaml")
        # from ChemAgent.tools.predictor.pwdft_input import Pwdft_input
        # Pwdft_input(prepath)
        self.run_command(f"python {prepath}/pwdft_input.py {prepath}/POSCAR")
        
        # Step 4: Upload files and execute run.sh on the remote server
        # print("\nStep 4: Upload files and execute run.sh on the remote server")
        
        # SSH key file path needs to be provided
        key_filepath = " "  # Replace with your private key path

        # Check if the private key file exists
        if not os.path.isfile(key_filepath):
            print(f"Private key file not found: {key_filepath}", file=sys.stderr)
            sys.exit(1)
        
        upload_command = (
            f'python {prepath}/upload_pseudopotentials.py {prepath}/POSCAR /home/gpu2/work/LvS/target '
            f'--config {prepath}/config.yaml --run {prepath}/run.sh --default_folder {prepath}/default '
            f'--hostname 114.214.197.165 --username gpu2 --password "ustc@2021/.," '
            f'--exec_command "cd /home/gpu2/work/LvS/target && ./run.sh"'
        )
        self.run_command(upload_command)

        # Step 5: Download the generated file statflie.0 from the remote server
        # print("\n Step 5: Download the generated file statflie.0 from the remote server")
        self.run_command(f"python {prepath}/t0_output.py")
