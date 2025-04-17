import re
import pandas as pd
from typing import Dict, Any, List, Optional
from MatAgent.tools.predictor.type_map import generate_input_json
import dpdata
import numpy as np
import json
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from MatAgent.config import config as default_config
from MatAgent import __root_dir__
from MatAgent.config import config
from MatAgent.tools.Dataset_Search.base import TableSearcher
from MatAgent.tools.predictor.FP_base import FP_Predictor
from MatAgent.tools.predictor.ML_base import PT_Predictor
from MatAgent.tools.predictor.get_ids import get_ids
from MatAgent.tools.predictor.POSCAR_Generate import POSCAR_Generate
from MatAgent.tools.predictor.prompt import (
    PROMPT, FINAL_MARKDOWN_PROPMT, READ_PROPMT
)
from .data_relaticity import data_relaticity
from pathlib import Path
import json
import dpdata
import numpy as np
import os

data_csv_path = default_config['data_dir']

_predictable_properties = [
    path.stem for path in Path(default_config['model_dir']).iterdir() if not path.stem.startswith('__')
]
load_model_path = default_config['model_dir']
predictor_path = config['predictor']
model_names = ",".join(_predictable_properties)
print(f"model_name: {model_names}", _predictable_properties)


def create_folder(folder_name, path):
    full_path = os.path.join(path, folder_name)

    try:
        os.makedirs(full_path, exist_ok=False)
        print(f"Folder '{folder_name}' has been successfully created at '{path}'.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists at '{path}'.")
    except Exception as e:
        print(f"Error creating folder: {e}")
    return full_path

def pwdft2dpmd(pwdft_output,path):
    d_outcar = dpdata.LabeledSystem(pwdft_output, fmt = 'pwdft/hydrid')
    d_outcar.to_deepmd_raw(path+'/raw_data/')
    d_outcar.to_deepmd_npy(path+'/npy_data/')

class Predictor(Chain):
    """Tools that predict properties."""
    llm: BaseLanguageModel
    llm_chain: LLMChain
    read_chain: LLMChain
    final_single_chain: LLMChain
    model_dir: str = config['model_dir']
    data_dir: str = config['data_dir']
    tool_names: str = model_names
    input_key: str = 'question'
    output_key: str = 'answer'

    etot: Optional[float] = None
    centroid_force: Optional[List[float]] = None  # 定义为包含三个浮点数的列表
    atomic_force: Optional[float] = None

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _parse_output(self, text) -> Dict[str, Any]:
        thought = re.search(r"Thought:\s*(.+?)(?:\s*\n|$)", text, re.DOTALL)
        PTModels = re.findall(r"PTModel:\s*(.+?)(?:\s*\n|$)", text, re.DOTALL)
        properties = re.findall(r"Property:\s*(.+?)(?:\s*\n|$)", text, re.DOTALL)
        materials = re.findall(r"Material:\s*(.+?)(?:\s*\n|$)", text, re.DOTALL)
        if not thought:
            raise ValueError(f'unknown format from LLM, no thought: {text}')
        if not properties:
            raise ValueError(f'unknown format from LLM, no properties: {text}')
        if not materials:
            raise ValueError(f'unknown format from LLM, materials: {text}')
        return {
            'Thought': thought.group(1).strip(),
            'PTModels': [pt.strip() for pt in PTModels],
            'Property': [prop.strip() for prop in properties],
            'Materials': [mat.strip() for mat in materials],
        }            

    def FP_predictor(self, mat):
        print("Use FP Tool")
        FP_Predictor(mat).cal_fp_predictor()
    
    def PT_predictor(self, pro, model_path, cor, box, atype):
        print("Use ML Tool")
        PT_Predictor_Res = PT_Predictor(model_path, cor, box, atype).cal_fp_predictor(pro)
        return PT_Predictor_Res

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None
    ):
        run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = run_manager.get_child()

        llm_output = self.llm_chain.predict(
            question=inputs[self.input_key],
            callbacks=callbacks
        )

        if config["handle_errors"]:
            try:
                output = self._parse_output(llm_output)
            except ValueError as e:
                return {self.output_key: f'ValueError : {str(e)}'}
        else:
            output = self._parse_output(llm_output)

        if output['PTModels'] == ['null']:
            # use FP tool
            self.FP_predictor(output['Materials'][0])
            file_path = f'{predictor_path}/statfile.0'
            if not os.path.isfile(file_path):
                return f"File does not exist: {file_path}"

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return "statfile.0 is null."
        
            from ChemAgent.tools.predictor.read_agent_output import extract_atomic_force
            from ChemAgent.tools.predictor.read_agent_output import extract_last_centroid_force
            from ChemAgent.tools.predictor.read_agent_output import extract_last_iteration_energy
            self.etot = extract_last_iteration_energy(file_path)
            self.centroid_force = extract_last_centroid_force(file_path)
            self.atomic_force = extract_atomic_force(file_path)

            if not isinstance(self.centroid_force, (list, tuple)) or len(self.centroid_force) < 3:
                return "centroid_force, the data format is incorrect or insufficient."
            final_output = self.read_chain.predict(
                question=inputs[self.input_key],
                etot=self.etot,  
                centroid_force_0=self.centroid_force[0],
                centroid_force_1=self.centroid_force[1],
                centroid_force_2=self.centroid_force[2],
                atomic_force=self.atomic_force
            )
            new_data = {
                'name': output['Materials'][0],
                'etot(au)': self.etot,
                'Fx(eV)': self.centroid_force[0],
                'Fy(eV)': self.centroid_force[1],
                'Fz(eV)': self.centroid_force[2],
                'atomic_force(eV/Å)': self.atomic_force,
            }
            try:
                if not data_csv_path.exists():
                    df = pd.DataFrame([new_data])
                    df.to_csv(data_csv_path, index=False)
                else:
                    df = pd.DataFrame([new_data])
                    df.to_csv(data_csv_path, mode='a', header=False, index=False)
            except Exception as e:
                print(f"Error writing CSV file: {e}")

                path = create_folder(output['Materials'][0], load_model_path)
                pwdft2dpmd('statfile.0', path)
                input_json_path = f"{path}/input.json"
                generate_input_json(output['Materials'][0], input_json_path)
                import os
                os.system('dp --pt train f"{input_json_path}"')

                data = np.genfromtxt(path+"lcurve.out", names=True)
                print(data)
                print(data['rmse_f_trn'][-1])
                trn_result = {
                    'rmse_val': data['rmse_val'][-1],
                    'rmse_trn': data['rmse_trn'][-1],
                    'rmse_e_val': data['rmse_e_val'][-1],
                    'rmse_e_trn': data['rmse_e_trn'][-1],
                    'rmse_f_val': data['rmse_f_val'][-1],
                    'rmse_f_trn': data['rmse_f_trn'][-1],
                    'lr': data['lr'][-1],
                }
                with open(path+'result.json', 'w') as json_file:
                    json.dump(trn_result, json_file, indent=4)
        else:
            # print("Further judgment")
            model_dir = f"{load_model_path}{output['PTModels'][0]}"
            model_result_path = f"{model_dir}/result.json"
            with open(model_result_path, 'r') as file:
                pm_res = json.load(file)
                l2fa_train = pm_res['rmse_f_trn']
            ei_l = (1 + 0.1) * l2fa_train 
            ei_h = ei_l + 0.30
            cor = np.load(f'{model_dir}/npy_data/set.000/coord.npy')
            box = np.load(f'{model_dir}/npy_data/set.000/box.npy')
            with open(f'{model_dir}/npy_data/type.raw') as file:
                d = [line.strip() for line in file.readlines()]
                atype = [int(x) for x in d]
            model_path = f"{model_dir}/model.ckpt.pt"
            model_path_1 = f"{model_dir}/model.ckpt-10000.pt"
            model_devi = data_relaticity(cor, box, atype, [model_path, model_path_1])

            if model_devi[0][4] < ei_l:
                final_output = self.PT_predictor(output['Property'], model_path, cor, box, atype)
            # elif model_devi[0][4] < ei_h:
            else:
                # use FP tool
                self.FP_predictor(output['Materials'][0])
                file_path = f'{predictor_path}/statfile.0'
                if not os.path.isfile(file_path):
                    return f"File does not exist: {file_path}"

                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    return "statfile.0 is null."
            
                from ChemAgent.tools.predictor.read_agent_output import extract_atomic_force
                from ChemAgent.tools.predictor.read_agent_output import extract_last_centroid_force
                from ChemAgent.tools.predictor.read_agent_output import extract_last_iteration_energy
                self.etot = extract_last_iteration_energy(file_path)
                self.centroid_force = extract_last_centroid_force(file_path)
                self.atomic_force = extract_atomic_force(file_path)

                if not isinstance(self.centroid_force, (list, tuple)) or len(self.centroid_force) < 3:
                    return "centroid_force, the data format is incorrect or insufficient."
                final_output = self.read_chain.predict(
                    question=inputs[self.input_key],
                    etot=self.etot,  
                    centroid_force_0=self.centroid_force[0],
                    centroid_force_1=self.centroid_force[1],
                    centroid_force_2=self.centroid_force[2],
                    atomic_force=self.atomic_force
                )
                new_data = {
                    'name': output['Materials'][0],
                    'etot(au)': self.etot,
                    'Fx(eV)': self.centroid_force[0],
                    'Fy(eV)': self.centroid_force[1],
                    'Fz(eV)': self.centroid_force[2],
                    'atomic_force(eV/Å)': self.atomic_force,
                }
                try:
                    if not data_csv_path.exists():
                        df = pd.DataFrame([new_data])
                        df.to_csv(data_csv_path, index=False)
                    else:
                        df = pd.DataFrame([new_data])
                        df.to_csv(data_csv_path, mode='a', header=False, index=False)
                except Exception as e:
                    print(f"Error writing CSV file: {e}")

                    path = create_folder(output['Materials'][0], load_model_path)
                    pwdft2dpmd('statfile.0', path)
                    input_json_path = f"{path}/input.json"
                    generate_input_json(output['Materials'][0], input_json_path)
                    import os
                    os.system('dp --pt train f"{input_json_path}"')

                    data = np.genfromtxt(path+"lcurve.out", names=True)
                    print(data)
                    print(data['rmse_f_trn'][-1])
                    trn_result = {
                        'rmse_val': data['rmse_val'][-1],
                        'rmse_trn': data['rmse_trn'][-1],
                        'rmse_e_val': data['rmse_e_val'][-1],
                        'rmse_e_trn': data['rmse_e_trn'][-1],
                        'rmse_f_val': data['rmse_f_val'][-1],
                        'rmse_f_trn': data['rmse_f_trn'][-1],
                        'lr': data['lr'][-1],
                    }
                    with open(path+'result.json', 'w') as json_file:
                        json.dump(trn_result, json_file, indent=4)

        formatted_output = self.final_single_chain.predict(
            question=inputs[self.input_key],
            final_output=final_output
        )
        print(formatted_output)
        return {self.output_key: formatted_output}

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        prompt: str = PROMPT,
        read_prompt: str = READ_PROPMT,
        final_single_prompt: str = FINAL_MARKDOWN_PROPMT,
        **kwargs: Any,
        ) -> Chain:
        template = PromptTemplate(
            template=prompt,
            input_variables=['question'],
            partial_variables={'model_names': model_names}
        )
        rd_template = PromptTemplate(
            template=read_prompt,
            input_variables=['question'],
            partial_variables={
                'etot': '',
                'centroid_force_0': '',
                'centroid_force_1': '',
                'centroid_force_2': '',
                'atomic_force': '',
            }
        )

        fs_template = PromptTemplate(
            template=final_single_prompt,
            input_variables=['question', 'final_output']
        )

        llm_chain = LLMChain(llm=llm, prompt=template)
        read_chain = LLMChain(llm=llm, prompt=rd_template)
        final_single_chain = LLMChain(llm=llm, prompt=fs_template)

        return cls(
            llm=llm,
            llm_chain=llm_chain, 
            read_chain=read_chain,
            final_single_chain=final_single_chain,
            **kwargs
        )
