"""
Conversational RAG chain builder per domain.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from rag.vectorstore import get_retriever
from rag.prompts import PROMPTS, CONTEXTUALIZE_SYSTEM_PROMPT

# Cache built chains
_chain_cache: dict = {}


def _build_chain(domain: str):
    """Build a conversational retrieval chain for the given domain."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.4,
        max_output_tokens=1024,
    )

    retriever = get_retriever(domain)

    # --- History-aware retriever ---
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", CONTEXTUALIZE_SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_prompt
    )

    # --- QA chain with domain prompt ---
    system_prompt = PROMPTS[domain] + (
        "\n\nUse the following retrieved context to answer the user's question. "
        "If the context does not contain the answer, say you don't have that "
        "information and suggest contacting the business directly.\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # --- Full retrieval chain ---
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain


def get_chain(domain: str):
    """Get or create the RAG chain for a domain."""
    if domain not in _chain_cache:
        _chain_cache[domain] = _build_chain(domain)
    return _chain_cache[domain]


def chat(domain: str, message: str, history: list[dict] | None = None) -> str:
    """
    Send a message to the domain-specific RAG chain and return the reply.
    history: list of {"role": "user"|"assistant", "content": "..."}
    """
    chain = get_chain(domain)

    # Convert history dicts to LangChain message objects
    chat_history = []
    if history:
        for msg in history:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))

    result = chain.invoke({
        "input": message,
        "chat_history": chat_history,
    })
    return result["answer"]
