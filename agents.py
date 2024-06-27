from typing import List
import os
import json
import requests
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage

class Agent:
    def __init__(self, name: str, instructions: str, backstory: str):
        self.name = name
        self.instructions = instructions
        self.backstory = backstory
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))

    def search_internet(self, query: str) -> str:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': os.getenv("SERPER_API_KEY"),
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text

    def process(self, input_data: str, knowledge_base_used: bool = False, file_summary: str = "") -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Instrucțiuni: {instructions}\nPovestea personajului: {backstory}"),
            ("human", "Sarcină: {input_data}\nRezumatul fișierului: {file_summary}\nAnalizați informațiile furnizate și oferiți perspective. Folosiți căutarea pe internet dacă este necesar. Răspundeți în limba română.")
        ])
        messages = prompt.format_messages(
            instructions=self.instructions,
            backstory=self.backstory,
            input_data=input_data,
            file_summary=file_summary
        )
        result = self.llm(messages)
        
        if isinstance(result, AIMessage):
            result_text = result.content
        else:
            result_text = str(result)

        internet_used = False
        if "căutați pe internet" in result_text.lower():
            internet_used = True
            search_query = result_text.split("căutați pe internet pentru ")[-1].split(".")[0]
            search_result = self.search_internet(search_query)
            result_text += f"\n\nRezultatele căutării pe internet: {search_result}"
        
        prefix = []
        if knowledge_base_used:
            prefix.append("[S-a folosit baza de cunoștințe]")
        if internet_used:
            prefix.append("[S-a folosit căutarea pe internet]")
        if file_summary:
            prefix.append("[S-a analizat fișierul încărcat]")
        
        prefix_str = " ".join(prefix) + " " if prefix else ""
        final_result = f"{prefix_str}Sarcină completată. Răspuns: {result_text}"
        return final_result

class Manager(Agent):
    def delegate(self, crew: List[Agent], input_data: str, knowledge_base_used: bool, file_summary: str) -> str:
        crew_output = []
        for agent in crew:
            agent_output = agent.process(input_data, knowledge_base_used, file_summary)
            crew_output.append(f"{agent.name}: {agent_output}")

        final_prompt = f"""
        Ca Manager, revizuiți următoarele rezultate ale echipei și oferiți o analiză finală și recomandări:

        {' '.join(crew_output)}

        Sarcina originală: {input_data}
        Rezumatul fișierului: {file_summary}

        Oferiți un rezumat cuprinzător și recomandări finale bazate pe rezultatele echipei și sarcina originală.
        Folosiți căutarea pe internet dacă sunt necesare informații suplimentare. Răspundeți în limba română.
        """
        return self.process(final_prompt, knowledge_base_used, file_summary)

class Crew:
    def __init__(self, manager: Manager, agents: List[Agent]):
        self.manager = manager
        self.agents = agents

    def process(self, input_data: str, knowledge_base_used: bool, file_summary: str) -> str:
        return self.manager.delegate(self.agents, input_data, knowledge_base_used, file_summary)

def create_agents_and_crew(agent_configs):
    manager = Manager(
        "Manager",
        agent_configs["Manager"]["instructions"],
        agent_configs["Manager"]["backstory"]
    )
    agents = [
        Agent("Cercetător", agent_configs["Cercetător"]["instructions"], agent_configs["Cercetător"]["backstory"]),
        Agent("Scriitor", agent_configs["Scriitor"]["instructions"], agent_configs["Scriitor"]["backstory"]),
        Agent("Analist", agent_configs["Analist"]["instructions"], agent_configs["Analist"]["backstory"]),
        Agent("Expert Financiar", agent_configs["Expert Financiar"]["instructions"], agent_configs["Expert Financiar"]["backstory"])
    ]
    crew = Crew(manager, agents)
    return manager, crew