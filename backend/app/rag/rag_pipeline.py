from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_classic.retrievers import EnsembleRetriever


from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from dotenv import load_dotenv
import os

load_dotenv()



embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# one level up from vector_db/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")  # one level up from vector_db/

vectordb = Chroma(
    persist_directory=VECTOR_DB_DIR,
    embedding_function=embedding
)




vector_retriever = vectordb.as_retriever(
    search_kwargs={"k":6}
)

# -----------------------
data = vectordb.get()

if not data["documents"]:
    raise ValueError("Vector DB is empty. Run your ingestion pipeline first.")

docs = [
    Document(page_content=text, metadata={"source": "db"})
    for text in data["documents"]
]

bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 6

retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4]
)


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


prompt = ChatPromptTemplate.from_template("""
Use the provided context to answer the question.

If the answer is partially available, explain based on the context.

Context:
{context}

Question:
{question}
""")


def format_docs(docs):
    return "\n\n".join(
        f"Source: {doc.metadata.get('source')}\n{doc.page_content}"
        for doc in docs
    )



qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def ask_question(question: str):
    return qa_chain.invoke(question)