import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from backend.config import CHROMA_DB_PATH, DOCUMENTS_FOLDER, OLLAMA_MODEL


def load_documents():
    if not os.path.exists(DOCUMENTS_FOLDER):
        os.makedirs(DOCUMENTS_FOLDER)
        print("Created company_docs folder - put your txt files in there!")
        return None

    all_text = []
    for filename in os.listdir(DOCUMENTS_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(DOCUMENTS_FOLDER, filename)
            with open(path, "r") as file:
                text = file.read()
                all_text.append(text)
                print("Loaded:", filename)

    if len(all_text) == 0:
        print("No txt files found!")
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.create_documents(all_text)
    print("Total chunks created:", len(chunks))

    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )

    print("Done! Documents are now in Chroma.")
    return db


def get_vector_store():
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)

    if os.path.exists(CHROMA_DB_PATH):
        db = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings
        )
        return db

    return load_documents()


if __name__ == "__main__":
    load_documents()
