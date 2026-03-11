# config.py - all the settings for our project (moved into backend/)

# postgres database url
DATABASE_URL = "postgresql://sidxcodes@localhost:5432/support_db"

# which ollama model to use (make sure its downloaded)
OLLAMA_MODEL = "llama3.2"

# where chroma stores the vector embeddings
CHROMA_DB_PATH = "./chroma_storage"

# folder where we keep company txt files
DOCUMENTS_FOLDER = "./company_docs"
