# rag_chain.py
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

def get_rag_chain():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_template(
        """
You are an AI sales call coach.
Use the context below to answer the question.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""
    )

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

    rag_chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm)
    return rag_chain