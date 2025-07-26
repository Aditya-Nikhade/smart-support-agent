import os
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

FAQ = {
    "refund": "You can request a refund within 14 days of purchase by contacting our support team with your order number.",
    "shipping": "Standard shipping typically takes 3-5 business days. Expedited shipping is 1-2 business days.",
    "support": "You can contact our human support agents by emailing support@example.com or calling 1-800-123-4567.",
    "account": "To reset your password, please go to the login page and click 'Forgot Password'."
}

def get_faq_retriever():
    """
    This function creates a Chroma vector store from the FAQ data using Azure embeddings
    and returns a retriever.
    """
    embedding_function = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
    )

    vectorstore = Chroma(
        collection_name="faq_retriever",
        embedding_function=embedding_function,
        persist_directory="./chroma_db"
    )

    if vectorstore._collection.count() == 0:
        print("Populating ChromaDB with FAQs using Azure Embeddings...")
        docs = [f"Question: {q}\nAnswer: {a}" for q, a in FAQ.items()]
        vectorstore.add_texts(docs)
        print("Population complete.")

    return vectorstore.as_retriever(search_kwargs={"k": 1})

if __name__ == '__main__':
    get_faq_retriever()
    print("Azure-powered FAQ Vector Store is ready.")