import streamlit as st
from etc.document_store import NewsDocumentStore
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        self.message_placeholder = container.empty()

    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.message_placeholder.markdown(self.text)

def initialize_session_state():
    """Streamlit 세션 상태 초기화"""
    if 'doc_store' not in st.session_state:
        # 기존 collection을 사용하여 NewsDocumentStore 초기화
        st.session_state.doc_store = NewsDocumentStore.from_existing("news_documents")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        
    if 'llm' not in st.session_state:
        st.session_state.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            streaming=True  # 스트리밍 활성화
        )

def search_documents(query: str, k: int = 3):
    """문서 검색 함수"""
    try:
        return st.session_state.doc_store.similarity_search(query, k=k)
    except Exception as e:
        st.error(f"검색 중 오류 발생: {str(e)}")
        return []

def generate_answer(query: str, relevant_docs: list, stream_handler) -> str:
    """GPT를 사용하여 답변 생성"""
    # 시스템 프롬프트 구성
    system_prompt = """당신은 사용자의 질문에 대해 친절하고 전문적으로 답변하는 AI 어시스턴트입니다.
    제공된 문서 정보를 바탕으로 답변을 생성하되, 문서 내용을 벗어나지 않도록 주의하세요.
    답변은 한국어로 작성하며, 전문적이면서도 이해하기 쉽게 설명해주세요."""
    
    # 관련 문서 정보 구성
    context = "관련 문서 정보:\n"
    for i, doc in enumerate(relevant_docs, 1):
        context += f"{i}. {doc['content']}\n"
    
    # 메시지 구성
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"다음 문서 정보를 참고하여 질문에 답변해주세요.\n\n{context}\n\n질문: {query}")
    ]
    
    try:
        # GPT로 스트리밍 답변 생성 (invoke 메소드 사용)
        response = st.session_state.llm(
            messages,
            callbacks=[stream_handler]
        )
        return response.content
    except Exception as e:
        st.error(f"답변 생성 중 오류 발생: {str(e)}")
        return "죄송합니다. 답변을 생성하는 중에 문제가 발생했습니다."

def main():
    st.set_page_config(
        page_title="AI 챗봇",
        page_icon="🤖",
        layout="wide"
    )
    
    initialize_session_state()

    # 메인 채팅 영역과 사이드바 레이아웃
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.sidebar.title("Navigation")
        st.sidebar.page_link("mainPage.py", label="News")
        st.sidebar.page_link("pages/dashboard.py", label="Dashboard") 
        st.sidebar.page_link("pages/chatbotPage.py", label="ChatBot")
        
        st.title("🤖 AI 문서 기반 챗봇")
        
        # 채팅 컨테이너 생성
        chat_container = st.container()
        with chat_container:
            # 채팅 히스토리 표시
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # 사용자 입력 영역
        if question := st.chat_input("질문을 입력하세요"):
            # 사용자 메시지 표시
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(question)
                st.session_state.chat_history.append({"role": "user", "content": question})
                
                # 관련 문서 검색
                with st.spinner("관련 정보 검색 중..."):
                    results = search_documents(question)

                # 사이드바 업데이트를 위한 상태 저장
                st.session_state.latest_results = results
                
                # GPT 답변 생성 및 표시
                with st.chat_message("assistant"):
                    stream_handler = StreamHandler(st.empty())
                    answer = generate_answer(question, results, stream_handler)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
            
    
    # 사이드바: 관련 문서 정보 표시
    with col2:
        st.sidebar.title("📑 관련 문서")
        # 현재 질문 표시
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            last_user_message = next((msg for msg in reversed(st.session_state.chat_history) 
                                    if msg["role"] == "user"), None)
            if last_user_message:
                st.sidebar.markdown("**현재 질문:**")
                st.sidebar.info(last_user_message["content"])
        if 'latest_results' in st.session_state and st.session_state.latest_results:
            for i, result in enumerate(st.session_state.latest_results, 1):
                with st.sidebar.expander(f"관련 문서 {i} (유사도: {result['similarity']:.2%})"):
                    st.markdown("**내용:**")
                    st.write(result['content'][:300] + "..." if len(result['content']) > 300 else result['content'])
                    st.markdown("**메타데이터:**")
                    for key, value in result['metadata'].items():
                        st.write(f"- {key}: {value}")
                        break
        else:
            st.sidebar.info("관련 문서가 없습니다.")
        
        # 대화 초기화 버튼
        if st.sidebar.button("대화 내용 초기화", type="secondary"):
            st.session_state.chat_history = []
            if 'latest_results' in st.session_state:
                del st.session_state.latest_results
            st.rerun()

if __name__ == "__main__":
    main()