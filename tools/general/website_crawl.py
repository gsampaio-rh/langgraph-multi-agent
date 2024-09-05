from langchain.agents import tool
from langchain.schema import Document
from typing import List
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer


@tool(parse_docstring=True)
def website_crawl(url: str) -> str:
    """
    A wrapper around a website crawling tool. Useful for retrieving and displaying the title and main content of a website from a specific URL. Input should be the URL of the website.

    Args:
        url: The URL of the website to crawl.

    Returns:
        List[Document]: A list of `Document` objects containing the crawled website content.

    Raises:
        Exception: If there is an issue with crawling the website.
    """

    urls = [url]
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()

    return docs


@tool(parse_docstring=True)
def extract_content(
    docs: List[Document], 
    tags_to_extract: List[str] = ["body", "p", "li", "div", "a"]
) -> str:
    """
    A wrapper around an HTML content extraction tool. Useful for extracting specific content from documents based on HTML tags. Input can be a list of Document objects or dictionaries, and a list of tags to extract.
    
    Args:
        docs: A list of `Document` objects to extract content from.
        tags_to_extract: A list of HTML tags specifying which parts of the content to extract.

    Returns:
        str: Extracted content from the documents based on the specified tags.

    Raises:
        Exception: If there is an issue with extracting content from the documents.

    """

    # Ensure docs are in the form of a list of Document objects
    if isinstance(docs, list) and isinstance(docs[0], dict):
        # Handle cases where metadata might be missing
        docs = [
            Document(
                metadata=doc.get(
                    "metadata", {}
                ),  # Use an empty dict if metadata is missing
                page_content=doc["page_content"],
            )
            for doc in docs
            if "page_content" in doc  # Ensure page_content exists
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
