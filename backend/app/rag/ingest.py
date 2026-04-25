import logging
import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

logger.info("Loading documents from: %s", DOCS_DIR)

loader = DirectoryLoader(
    DOCS_DIR,
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
    show_progress=True,
)

documents = loader.load()

if not documents:
    raise ValueError(f"No .md files found in {DOCS_DIR}. Add your docs first.")

logger.info("Loaded %s documents", len(documents))
logger.info("Splitting documents")

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

chunks = splitter.split_documents(documents)
logger.info("Total chunks created: %s", len(chunks))

logger.info("Creating embeddings")
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

logger.info("Storing vectors in: %s", VECTOR_DB_DIR)
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=VECTOR_DB_DIR,
)

logger.info("Embeddings stored successfully in vector_db")
