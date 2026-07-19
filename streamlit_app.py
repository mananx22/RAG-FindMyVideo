__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# Trick LangChain into using pytubefix whenever it asks for pytube
import pytubefix
sys.modules['pytube'] = pytubefix

from dotenv import load_dotenv
load_dotenv()
import os
import re
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# ── Build proxy config from environment variables ──────────────────────────
_proxy_user = os.getenv("PROXY_USERNAME", "")
_proxy_pass = os.getenv("PROXY_PASSWORD", "")
_proxy_host = os.getenv("PROXY_HOST", "")
_proxy_port = os.getenv("PROXY_PORT", "80")

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
st.title("Find your video through Semantic Search 🔮")
# st.write("Go ahead! Give YT video url and let's find video without giving video name!")

# Text input box (Text area allows for multi-line input)
tab1, tab2 = st.tabs(["📥 Store","🔍 Query"])

with tab1:
    st.subheader("Go ahead! Give YT video url and let's find video without giving video name!")
    user_input = st.text_area(
        label="Input Text", 
        placeholder="Paste YT video url to save as vectors...",
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

                # ── Fetch transcript via proxy ──────────────────────────
                
                ytt_api = YouTubeTranscriptApi(proxy_config=_proxy_config)
                transcript_list = ytt_api.fetch(video_id)
                    

                # ── Fetch video metadata via pytubefix ─────────────────
                
                yt = YouTube(user_input)
                video_title  = yt.title or "Unknown Title"
                video_author = yt.author or "Unknown Author"                

                # ── Build LangChain Document ────────────────────────────
                doc = Document(
                    page_content=transcript_text,
                    metadata={
                        "source": video_id,
                        "title": video_title,
                        "author": video_author,
                        "url": user_input,
                    },
                )

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=100,
                    separators=["\n", ".", " "],
                    chunk_overlap=25,
                    length_function=len,
                )

                chunks = text_splitter.split_documents([doc])
                vectorstore.add_documents(chunks)

                st.success(f"Your Video: **{video_title}** from channel **{video_author}** has been saved to Vector DB successfully. Proceed to query section. ask questions about video to search it!")
        else:
            st.warning("Give one YT video url only within text area.")