# app/services/chatbot.py
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Qdrant
from langchain_core.embeddings import Embeddings
from langchain.retrievers import EnsembleRetriever 
from groq import Groq
from typing import List
from core.config import settings
from langchain_groq import ChatGroq 
import requests
import json

class SegmindEmbeddings(Embeddings):
    def __init__(self):
        self.api_key = settings.SEGMIND_API_KEY
        self.endpoint = "https://api.segmind.com/v1/text-embedding-3-large"  # Verify correct endpoint
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)
    
    def _embed(self, text: str) -> List[float]:
        try:
            response = requests.post(
                self.endpoint,
                headers={'x-api-key': self.api_key},
                json={
                    "text": text,
                    "model": "text-embedding-3-large"  # Verify correct model name
                }
            )
            response.raise_for_status()
            return response.json()['embedding']
        except Exception as e:
            raise ValueError(f"Embedding failed: {str(e)}")

class BusinessChatbot:
    def __init__(self):
        # Initialize Qdrant client
        self.qdrant = QdrantClient(
            url=settings.QDRANT_CLUSTER_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=60.0 
        )
        
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.3-70b-versatile"
        )
        # Initialize embeddings
        self.embeddings = SegmindEmbeddings()
        
        # Create collections if not exists
        self._init_collections()
        
        # Short-term memory (last 5 messages)
        self.memory = ConversationBufferWindowMemory(k=5)
        
        # Initialize vector stores
        self.analysis_store = Qdrant(
            client=self.qdrant,
            collection_name="analysis_reports",
            embeddings=self.embeddings
        )
        
        self.chat_history_store = Qdrant(
            client=self.qdrant,
            collection_name="chat_history",
            embeddings=self.embeddings
        )

    def _init_collections(self):
    # Check if collections exist first
        collections = self.qdrant.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if "analysis_reports" not in collection_names:
            # Create collection if it doesn't exist
            self.qdrant.create_collection(
                collection_name="analysis_reports",
                vectors_config=VectorParams(
                    size=3072,  # Segmind embedding size
                    distance=Distance.COSINE
                )
            )
        
        if "chat_history" not in collection_names:
            # Create collection if it doesn't exist
            self.qdrant.create_collection(
                collection_name="chat_history",
                vectors_config=VectorParams(
                    size=3072,  # Segmind embedding size
                    distance=Distance.COSINE
                )
            )

    async def index_report(self, report: dict):
        """Store analysis context in vector DB"""
        try:
            report_text = json.dumps(report)
            
            # Use a try-except block to handle both async and sync approaches
            try:
                # Try the async approach first
                await self.analysis_store.aadd_texts(
                    texts=[report_text],
                    metadatas=[{"type": "analysis_report"}]
                )
            except NotImplementedError:
                # Fall back to sync approach if async fails
                self.analysis_store.add_texts(
                    texts=[report_text],
                    metadatas=[{"type": "analysis_report"}]
                )
            
            return True
        except Exception as e:
            print(f"Error indexing report: {str(e)}")
            raise e

    async def _upsert_chat_history(self):
        """Store chat history after 5 exchanges"""
        history = self.memory.load_memory_variables({})["history"]
        # Use add_texts instead of aadd_texts
        self.chat_history_store.add_texts(
            texts=[history],
            metadatas=[{"type": "chat_history"}]
        )
        self.memory.clear()

    async def chat(self, query: str) -> str:
        """Handle contextual business queries"""
        # Check if we need to archive history
        if len(self.memory.chat_memory.messages) >= 5:
            await self._upsert_chat_history()
        
        # Build combined retriever
        retriever = self._create_retriever()
        
        # Create QA chain with explicit input/output keys
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            input_key="question",
            output_key="answer",
            chain_type_kwargs={
                "prompt": self._create_prompt(),
                "document_prompt": PromptTemplate(
                    input_variables=["page_content"],
                    template="{page_content}"
                )
            }
        )
        
        # Get history from memory
        memory_vars = self.memory.load_memory_variables({})
        
        try:
            # Include required keys in the chain input
            result = await qa_chain.ainvoke({
                "question": query
            })
            
            # Update memory with the new interaction
            self.memory.save_context({"input": query}, {"output": result["answer"]})
            
            return result["answer"]
        except Exception as e:
            # Handle errors gracefully
            print(f"Error in chat processing: {str(e)}")
            return f"I'm sorry, I encountered an issue while processing your request. Please try again later."

    def _create_retriever(self):
        """Combine analysis and chat history retrievers"""
        analysis_retriever = self.analysis_store.as_retriever(
            search_type="similarity",  # Specify search type
            search_kwargs={"filter": {"type": "analysis_report"}, "k": 3}
        )
        
        history_retriever = self.chat_history_store.as_retriever(
            search_type="similarity",  # Specify search type
            search_kwargs={"filter": {"type": "chat_history"}, "k": 2}
        )

        return EnsembleRetriever(
            retrievers=[analysis_retriever, history_retriever],
            weights=[0.7, 0.3]
        )

    def _create_prompt(self):
        template = """
        You are a business analyst assistant. Use this context to answer the question:
        
        {context}
        
        Question: {question}
        
        Provide precise data-backed responses using formal text formatting.
        Highlight key numbers from reports when possible.
        """
        
        return PromptTemplate(
            input_variables=["context", "question"],  # Simplified input variables
            template=template
        )