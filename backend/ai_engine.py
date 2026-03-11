"""ai_engine.py - this is the main brain of our chatbot (backend package)
it uses RAG (retrieval augmented generation) to answer questions
now with conversation memory so the AI remembers past messages!
"""

from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from backend.document_loader import get_vector_store
from backend.config import OLLAMA_MODEL


# the prompt uses {context} (from docs) and {question} (which we stuff with history)
PROMPT_TEXT = """You are a friendly customer support assistant.
Use the context below to answer the customer's question.
If you cannot find the answer in the context, say exactly: "TICKET_NEEDED"
Do not make up answers. Be short and helpful.

Context from company documents:
{context}

{question}

Your Answer:"""


def get_ai_answer(question, chat_history=None):
    """takes a question + past chat history, searches docs, and returns an answer.
    chat_history is a list of dicts like [{"question": "...", "answer": "..."}, ...]
    """

    # get the vector store where our documents are saved
    vector_store = get_vector_store()

    # if no documents loaded yet
    if vector_store is None:
        return {
            "answer": "Sorry, no company documents loaded yet. Please contact support.",
            "needs_ticket": True
        }

    # build a readable chat history string from past messages
    # we stuff it right into the question so the AI sees everything
    # only keep last 5 exchanges so the prompt doesnt get too long
    history_text = ""
    if chat_history and len(chat_history) > 0:
        history_text = "Previous conversation:\n"
        for msg in chat_history[-5:]:
            history_text += f"Customer: {msg['question']}\n"
            history_text += f"Assistant: {msg['answer']}\n\n"

    # combine history + new question into one string
    # this trick works because RetrievalQA only passes {context} and {question}
    full_question = ""
    if history_text:
        full_question = history_text + "Customer's new message: " + question
    else:
        full_question = "Customer's message: " + question

    # set up the LLM (large language model) - runs locally via ollama
    llm = Ollama(model=OLLAMA_MODEL)

    # create prompt (only 2 variables: context and question)
    prompt = PromptTemplate(
        template=PROMPT_TEXT,
        input_variables=["context", "question"]
    )

    # build the RAG chain
    # basically: search docs -> feed to AI -> get answer
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt}
    )

    # run the chain - full_question has history baked in
    result = chain.invoke({"query": full_question})
    answer = result["result"]

    # check if AI said it couldnt find the answer
    needs_ticket = "TICKET_NEEDED" in answer

    if needs_ticket:
        answer = "I'm sorry, I couldn't find an answer to your question. A support ticket has been created and our team will get back to you soon!"

    return {
        "answer": answer,
        "needs_ticket": needs_ticket
    }
