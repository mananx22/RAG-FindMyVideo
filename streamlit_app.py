__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ADD THIS: Trick LangChain into using pytubefix whenever it asks for pytube
import pytubefix
sys.modules['pytube'] = pytubefix

from dotenv import load_dotenv
load_dotenv()
import re
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import YoutubeLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pytubefix import YouTube

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="RAG-FindMyVideo",
    page_icon="🔍",
    layout="wide",
)

@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="ibm-granite/granite-embedding-small-english-r2")

embeddings = load_embeddings()

@st.cache_resource
def load_llm():
    return init_chat_model("groq:llama-3.1-8b-instant")
llm = load_llm()

@st.cache_resource
def load_vectorstore():
    return Chroma(
        collection_name="acquired_videos",
        embedding_function=embeddings,
        persist_directory="./chroma_db",

    )
vectorstore = load_vectorstore()

# 3. UI Layout
st.title("🔮 Text to Embeddings Converter")
st.write("Type or paste your text below to convert it into a numerical vector embedding.")

# Text input box (Text area allows for multi-line input)
tab1, tab2 = st.tabs(["🔍 Query","📥 Store"])

with tab1:
    st.subheader("Add Video to Vector DB")
    user_input = st.text_area(
        label="Input Text", 
        placeholder="Paste url to save as vectors...",
        height=150
    )

    if st.button("Save Video"):
        if user_input.strip():
            with st.spinner("Fetching transcript and generating embeddings..."):
                video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", user_input)
                if not video_id_match:
                    st.error("Invalid YouTube URL.")
                    st.stop()
                video_id = video_id_match.group(1)

                loader = YoutubeLoader.from_youtube_url(
                    youtube_url=user_input,
                    add_video_info=True,
                    language=["en"],
                )
                docs = loader.load()

                if not docs:
                    st.error("Could not load transcript for this video.")
                    st.stop()

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=100,
                    separators=["\n", ".", " "],
                    chunk_overlap=25,
                    length_function=len,
                )

                chunks = text_splitter.split_documents(docs)
                vectorstore.add_documents(chunks)

                video_title = docs[0].metadata.get("title", "Unknown Title")
                video_author = docs[0].metadata.get("author", "Unknown Author")
                st.success(f"Your Video: **{video_title}** from channel **{video_author}** has been saved to Vector DB successfully.")
        else:
            st.warning("Please add some text")