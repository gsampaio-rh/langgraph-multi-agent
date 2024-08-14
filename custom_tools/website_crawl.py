from langchain.agents import tool
from langchain.schema import Document
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer

@tool
def website_crawl(url: str) -> str:
    """
    A wrapper around a website crawling tool. Useful for retrieving and displaying the title and main content of a website from a specific URL. Input should be the URL of the website.
    """

    urls = [url]
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()

    return docs

@tool
def extract_content(docs, tags_to_extract=["body"]) -> str:
    """
    A wrapper around an HTML content extraction tool. Useful for extracting specific content from documents based on HTML tags.
    Input can be a list of Document objects or dictionaries, and a list of tags to extract.
    """
    # Ensure docs are in the form of a list of Document objects
    if isinstance(docs, list) and isinstance(docs[0], dict):
        docs = [
            Document(metadata=doc["metadata"], page_content=doc["page_content"])
            for doc in docs
        ]

    # Initialize BeautifulSoup transformer with the specified tags
    bs_transformer = BeautifulSoupTransformer()

    # Transform the documents using the provided tags
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=tags_to_extract
    )

    # Extract the content from the transformed documents
    content = docs_transformed[0].page_content if docs_transformed else ""

    return content
