from typing import List
import os
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from crewai_tools import SerperDevTool

class Agent:
    def __init__(self, name: str, instructions: str, backstory: str):
        self.name = name
        self.instructions = instructions
        self.backstory = backstory
        self.llm = OpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
        self.serper_tool = SerperDevTool()

    def process(self, input_data: str, knowledge_base_used: bool = False, file_summary: str = "") -> str:
        prompt = PromptTemplate(
            input_variables=["instructions", "backstory", "input_data", "file_summary"],
            template="Instrucțiuni: {instructions}\nPovestea personajului: {backstory}\nSarcină: {input_data}\nRezumatul fișierului: {file_summary}\nAnalizați informațiile furnizate și oferiți perspective. Folosiți căutarea pe internet dacă este necesar. Răspundeți în limba română.\nRăspuns:"
        )
        chain = prompt | self.llm
        result = chain.invoke({
            "instructions": self.instructions,
            "backstory": self.backstory,
            "input_data": input_data,
            "file_summary": file_summary
        })
        
        internet_used = False
        if "căutați pe internet" in result.lower():
            internet_used = True
            search_query = result.split("căutați pe internet pentru ")[-1].split(".")[0]
            search_result = self.serper_tool.search(search_query)
            result += f"\n\nRezultatele căutării pe internet: {search_result}"
        
        prefix = []
        if knowledge_base_used:
            prefix.append("[S-a folosit baza de cunoștințe]")
        if internet_used:
            prefix.append("[S-a folosit căutarea pe internet]")
        if file_summary:
            prefix.append("[S-a analizat fișierul încărcat]")
        
        prefix_str = " ".join(prefix) + " " if prefix else ""
        final_result = f"{prefix_str}Sarcină completată. Răspuns: {result}"
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

def create_agents_and_crew():
    manager = Manager(
        "Manager",
        "Coordonați echipa și oferiți o analiză finală bazată pe contribuțiile tuturor agenților.",
        "Sunteți un manager experimentat în domeniul licitațiilor, cu o vastă experiență în coordonarea echipelor multidisciplinare."
    )
    agents = [
        Agent("Cercetător", "Cercetați și furnizați informații detaliate despre aspectele tehnice ale licitațiilor.", "Sunteți un expert în cercetarea și analiza informațiilor despre licitații."),
        Agent("Scriitor", "Creați conținut clar și convingător pentru documentele licitației.", "Sunteți un scriitor talentat cu experiență în redactarea documentelor pentru licitații."),
        Agent("Analist", "Analizați datele și tendințele pieței relevante pentru licitație.", "Sunteți un analist de date cu experiență în interpretarea informațiilor de piață pentru licitații."),
        Agent("Expert Financiar", "Oferiți analize și sfaturi financiare legate de licitație.", "Sunteți un expert financiar cu o vastă experiență în aspectele economice ale licitațiilor.")
    ]
    crew = Crew(manager, agents)
    return manager, crew