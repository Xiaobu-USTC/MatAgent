from mp_api.client import MPRester
import os

def get_ids(chem_formula):
    # It is recommended to store the API key in an environment variable
    api_key = " "
    if not api_key:
        raise ValueError("Please set the MATERIALS_PROJECT_API_KEY environment variable")
    
    with MPRester(api_key) as mpr:
        try:
            # Use the materials.summary.search method for the query
            results = mpr.materials.summary.search(
                formula=chem_formula,
                crystal_system="Orthorhombic"
            )
            
            # Extract the material_id list
            material_ids = [result.material_id for result in results]
        
        except Exception as e:
            print(f"Query failed: {e}")
            return []
    
    return material_ids
