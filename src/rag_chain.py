"""
rag_chain.py - بيستخدم Google Gemini للـ LLM والـ embeddings
مجاني 100% - بيستخدم google-genai الجديدة
"""

import os
from pathlib import Path
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.embeddings.base import Embeddings
from google import genai


VECTORSTORE_PATH = "data/vectorstore"


class GeminiEmbeddings(Embeddings):
    """Custom embeddings class بتستخدم google-genai الجديدة"""

    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )
        return [e.values for e in result.embeddings]

    def embed_query(self, text: str) -> List[float]:
        result = self.client.models.embed_content(
            model=self.model,
            contents=[text],
        )
        return result.embeddings[0].values


def build_vectorstore(documents: List[Document], force_rebuild: bool = False) -> FAISS:
    print("   Setting up Gemini embeddings...")
    embeddings = GeminiEmbeddings(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-embedding-001",
    )

    store_path = Path(VECTORSTORE_PATH)

    if store_path.exists() and not force_rebuild:
        print("Loading vector store from cache...")
        vectorstore = FAISS.load_local(
            str(store_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print("Vector store loaded from cache")
        return vectorstore

    if not documents:
        raise ValueError("No documents found! Make sure CV / GitHub / LinkedIn loaded correctly.")

    print(f"Building vector store from {len(documents)} document(s)...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"   {len(chunks)} chunks created")

    vectorstore = FAISS.from_documents(chunks, embeddings)
    store_path.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(store_path))
    print(f"Vector store built and saved!")

    return vectorstore


def build_qa_chain(vectorstore: FAISS, your_name: str) -> ConversationalRetrievalChain:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
        k=10,
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 20},
    )

    system_prompt = f"""You are a smart assistant that answers questions about {your_name}.

You have information from:
- CV/Resume
- GitHub account
- LinkedIn profile

Important rules:
1. Answer ONLY based on the available context
2. If you cannot find the information, say so honestly
3. Answer in the same language as the question (Arabic or English)
4. Be specific and clear
5. If asked about a skill or technology, mention project examples if available

Available context:
{{context}}

Previous conversation:
{{chat_history}}

Question: {{question}}

Answer:"""

    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=system_prompt,
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        verbose=False,
    )

    return chain