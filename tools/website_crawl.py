from langchain.agents import tool
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer


@tool
def website_crawl(url: str) -> str:
    """
    A wrapper around a website crawling tool. Useful for retrieving and displaying the title and main content of a website from a specific URL. Input should be the URL of the website.

    Args:
        url (str): The URL of the website to crawl.

    Returns:
        str: The main content of the website.
    """
    urls = [url]
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()

    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["article"]
    )

    content = docs_transformed[0].page_content

    return content
