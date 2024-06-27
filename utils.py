import os
import PyPDF2
import chardet
from langchain_openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def process_file(file):
    content = ""
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
    else:
        raw_content = file.getvalue()
        detected_encoding = chardet.detect(raw_content)['encoding'] or 'utf-8'
        try:
            content = raw_content.decode(detected_encoding)
        except UnicodeDecodeError:
            content = raw_content.decode('utf-8', errors='replace')
    
    # Create a simple summary using LLM
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(content)
    
    llm = OpenAI(temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Rezumați următorul text într-o manieră concisă:\n\n{text}\n\nRezumat:"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    
    summary = chain.run(text=texts[0])  # Summarize the first chunk for brevity
    
    return content, summary

def save_to_knowledge_base(uploaded_file, knowledge_base_dir):
    file_path = os.path.join(knowledge_base_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

def get_knowledge_base_files(knowledge_base_dir):
    return [f for f in os.listdir(knowledge_base_dir) if os.path.isfile(os.path.join(knowledge_base_dir, f))]

def delete_from_knowledge_base(filename, knowledge_base_dir):
    file_path = os.path.join(knowledge_base_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

def read_file_content(file_path):
    with open(file_path, 'rb') as f:
        raw_content = f.read()
    detected_encoding = chardet.detect(raw_content)['encoding'] or 'utf-8'
    try:
        return raw_content.decode(detected_encoding)
    except UnicodeDecodeError:
        return raw_content.decode('utf-8', errors='replace')