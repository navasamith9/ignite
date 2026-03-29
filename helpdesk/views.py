import os
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import bs4

from langchain_community.document_loaders import RecursiveUrlLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)

class LocalHelpdeskBot:
    def __init__(self):
        self.base_url = "https://www.iiitdmj.ac.in"
        self.pdf_path = os.path.join(os.path.dirname(__file__), "..", "2944 Annexure II _ Academic Guidelines_UG modified Dec 2025_.pdf")
        self.persist_directory = "./chroma_db_local"
        
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = ChatOllama(model="llama3", temperature=0.1)
        
        self.vector_store = None
        self.chat_history = []
        
    def _extractor(self, html_content: str) -> str:
        soup = bs4.BeautifulSoup(html_content, "html.parser")
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()
        return " ".join(soup.stripped_strings)

    def load_or_ingest_data(self):
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            self.vector_store = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
            print("Loaded existing local vector database.")
        else:
            print("Building local database from Web and PDF. This will take a moment depending on your hardware...")
            all_documents = []
            
            try:
                web_loader = RecursiveUrlLoader(url=self.base_url, max_depth=1, extractor=self._extractor, prevent_outside=True)
                all_documents.extend(web_loader.load())
            except Exception as e:
                print(f"Web load error: {e}")

            try:
                pdf_loader = PyPDFLoader(self.pdf_path)
                all_documents.extend(pdf_loader.load())
            except Exception as e:
                print(f"PDF load error: {e}")

            if all_documents:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
                chunks = text_splitter.split_documents(all_documents)
                self.vector_store = Chroma.from_documents(documents=chunks, embedding=self.embeddings, persist_directory=self.persist_directory)

    def setup_chain(self):
        if not self.vector_store:
            return
            
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given a chat history and the latest user question, formulate a standalone question. Do NOT answer it, just reformulate it."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        history_aware_retriever = create_history_aware_retriever(self.llm, retriever, contextualize_q_prompt)

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the official Ignite Helpdesk AI assistant for IIITDM Jabalpur. Answer accurately based on the website and Academic Guidelines PDF. Do not invent information.\n\nContext: {context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        self.rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    def get_answer(self, user_input):
        if not hasattr(self, 'rag_chain'):
            return "I am currently initializing my database. Please try again in a moment."
            
        response = self.rag_chain.invoke({"input": user_input, "chat_history": self.chat_history})
        answer = response["answer"]
        self.chat_history.append(HumanMessage(content=user_input))
        self.chat_history.append(AIMessage(content=answer))
        return answer

bot = None

def get_bot():
    global bot
    if bot is None:
        bot = LocalHelpdeskBot()
        bot.load_or_ingest_data()
        bot.setup_chain()
    return bot

def chat_page(request):
    return render(request, 'helpdesk.html')

@csrf_exempt  
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            if not user_message:
                return JsonResponse({"error": "Empty message"}, status=400)
            
            bot_instance = get_bot()
            bot_response = bot_instance.get_answer(user_message)
            return JsonResponse({"response": bot_response})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)