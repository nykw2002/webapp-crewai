import streamlit as st
from dotenv import load_dotenv
from agents import create_agents_and_crew
from ui_components import setup_ui, display_result, load_custom_css
from utils import process_file, get_knowledge_base_files
from config import KNOWLEDGE_BASE_DIR

load_dotenv()

def main():
    st.set_page_config(page_title="Procesor de Documente pentru Licitații", layout="wide")

    st.write("Debug: About to call setup_ui()")
    setup_ui_result = setup_ui()
    st.write(f"Debug: setup_ui() returned: {setup_ui_result}")
    
    initial_prompt, uploaded_file, agent_configs, save_config = setup_ui_result
    st.write(f"Debug: Unpacked values - initial_prompt: {initial_prompt}, uploaded_file: {uploaded_file}, agent_configs: {agent_configs}, save_config: {save_config}")
    
    initial_prompt, uploaded_file, agent_configs, save_config = setup_ui()

    if st.sidebar.button("Procesează", key="process"):
        if not initial_prompt:
            st.error("Vă rugăm să introduceți un prompt inițial.")
        else:
            with st.spinner("Se procesează..."):
                try:
                    manager, crew = create_agents_and_crew(agent_configs)
                    input_data = initial_prompt
                    file_summary = ""
                    if uploaded_file:
                        _, file_summary = process_file(uploaded_file)
                        input_data += f"\n\nUn fișier a fost încărcat. Iată un rezumat al conținutului său: {file_summary}"

                    knowledge_base_used = len(get_knowledge_base_files(KNOWLEDGE_BASE_DIR)) > 0
                    if knowledge_base_used:
                        input_data += "\n\nInformațiile din baza de cunoștințe sunt disponibile pentru această sarcină."

                    result = crew.process(input_data, knowledge_base_used, file_summary)
                    display_result(result)

                except Exception as e:
                    st.error(f"A apărut o eroare: {str(e)}")
                    st.exception(e)

if __name__ == "__main__":
    main()