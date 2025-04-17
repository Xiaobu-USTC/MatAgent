PREFIX = """You act like a material scientist answering a question. Answer the following questions as best you can. You have access to the following tools:"""

FORMAT_INSTRUCTIONS = """
Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Evaluate: the result of the action
... (this Thought/Action/Action Input/Evaluate can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

SUFFIX = """Begin!



Question: What is the energy and force of CH4?
Thought: I need to find the energy of CH4.
Action: Dateset_Search
Action Input: "Search name CH4 and provide information on its energy"
Observation: The energy of material "CH4" is 0.0202 eV. Check to see if this answer can be you final answer, and if so, you should submit your final answer.
Thought: The Dateset_Search tool provided the energy of CH4, but not the force. I need to find the force.
Action: Dateset_Search
Action Input: "Search name force and provide information on its force"
Observation: The Dateset_Search tool did not provide any information on the force of CH4. I need to find another way to obtain this information.
Thought: The Dateset_Search tool provided the energy of CH4, but not the force. I need to find the force.
Action: predictor
Action Input: "Predict the force of CH4"
Observation: The force of material CH4 is 0.0101 eV/Å. Check to see if this answer can be you final answer, and if so, you should submit your final answer.
Thought: I now know the final answer
Final Answer: The energy and force of CH4 is 0.0202 eV and 0.0101 eV/Å.


Question: {input}
Thought:{agent_scratchpad}""" 
