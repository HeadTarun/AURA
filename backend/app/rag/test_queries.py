
from rag_pipeline import *
results = vectordb.similarity_search("refund policy", k=3)

for r in results:
    print(r.page_content)