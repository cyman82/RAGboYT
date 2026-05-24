import streamlit as st
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.rag.pipelines.query_pipeline import QueryPipeline
from app.rag.pipelines.ingest_pipeline import IngestPipeline
from app.rag.embeddings.embedder import EmbedderFactory
from app.llm.generator import LLMGenerator

# Page configuration
st.set_page_config(
    page_title="YouTube RAG Chatbot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("🎬 YouTube RAG Chatbot")
st.markdown("### Ask questions about any YouTube video")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    video_id = st.text_input(
        "YouTube Video ID",
        placeholder="e.g., dQw4w9WgXcQ",
        help="Found in the URL after v="
    )
    
    transcript_input = st.text_area(
        "Video Transcript",
        placeholder="Paste the transcript here or it will be auto-fetched...",
        height=200
    )
    
    model_type = st.selectbox(
        "LLM Model",
        ["Ollama (Local)", "OpenAI"],
        help="Choose your LLM provider"
    )
    
    ingest_button = st.button("📥 Ingest Video", use_container_width=True)
    
    st.divider()
    
    st.markdown("### 📚 About")
    st.info("""
    **YouTube RAG Chatbot** uses Retrieval-Augmented Generation to answer questions about YouTube videos.
    
    - 🎯 Accurate answers grounded in video content
    - ⚡ Fast inference with local or cloud LLMs
    - 📝 Full transcript analysis
    """)

# Main content
if video_id:
    # Initialize pipelines
    try:
        embedder = EmbedderFactory.create(settings.EMBEDDING_MODEL)
        llm_gen = LLMGenerator(model_type="ollama" if "Ollama" in model_type else "openai")
        query_pipeline = QueryPipeline(embedder, llm_gen)
        
        # Ingest video
        if ingest_button:
            with st.spinner("📥 Processing video..."):
                try:
                    ingest_pipeline = IngestPipeline(embedder)
                    
                    if transcript_input:
                        # Use provided transcript
                        result = ingest_pipeline.process_transcript(
                            video_id=video_id,
                            transcript_text=transcript_input
                        )
                    else:
                        # Try to fetch from YouTube
                        result = ingest_pipeline.process_video(video_id)
                    
                    st.success(f"✅ Video processed! Stored {result.get('chunks_count', 0)} chunks.")
                    st.session_state.video_ingested = True
                    
                except Exception as e:
                    st.error(f"❌ Error processing video: {str(e)}")
                    st.info("💡 Tip: Paste the transcript manually if auto-fetch fails")
        
        # Chat interface
        st.divider()
        st.subheader("💬 Ask a Question")
        
        # Initialize session state for chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "video_ingested" not in st.session_state:
            st.session_state.video_ingested = False
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        user_query = st.chat_input("Ask about the video...", disabled=not st.session_state.video_ingested)
        
        if user_query:
            if not st.session_state.video_ingested:
                st.warning("⚠️ Please ingest a video first!")
            else:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": user_query})
                
                with st.chat_message("user"):
                    st.write(user_query)
                
                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("🤔 Thinking..."):
                        try:
                            result = query_pipeline.query(
                                video_id=video_id,
                                query=user_query
                            )
                            
                            answer = result.get("answer", "Could not generate answer")
                            evidence = result.get("evidence", [])
                            
                            # Display answer
                            st.write(answer)
                            
                            # Display evidence
                            if evidence:
                                st.divider()
                                st.subheader("📌 Evidence")
                                for i, item in enumerate(evidence, 1):
                                    with st.expander(f"Source {i} - {item.get('timestamp', 'N/A')}"):
                                        st.write(item.get("text", ""))
                                        st.caption(f"Confidence: {item.get('confidence', 0):.1%}")
                            
                            # Add assistant message
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer
                            })
                        
                        except Exception as e:
                            st.error(f"❌ Error generating response: {str(e)}")
                            st.info("💡 Make sure your backend is running and video is ingested")
    
    except Exception as e:
        st.error(f"❌ Configuration Error: {str(e)}")
        st.info("💡 Check your .env file and ensure all dependencies are installed")

else:
    st.info("👈 Enter a YouTube Video ID to get started!")
    
    with st.expander("📖 How to use"):
        st.markdown("""
        1. **Get Video ID**: From YouTube URL `https://www.youtube.com/watch?v=VIDEO_ID`
        2. **Paste ID**: In the sidebar, enter the 11-character video ID
        3. **Ingest**: Click "📥 Ingest Video" (auto-fetches transcript)
        4. **Ask**: Type questions about the video content
        5. **View Evidence**: See exact timestamps and quotes that support answers
        """)
