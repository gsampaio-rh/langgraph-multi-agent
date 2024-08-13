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

    Example:
        website_content = website_crawl(url="https://example.com/")
        print(website_content)

    Description:
        This function performs an HTTP GET request to the specified `url`. If the request
        is successful (status code 200), it parses the HTML content using BeautifulSoup to extract
        the title and main content of the article. The title is expected to be within an <h2> tag
        with the id "title_area," and the main content is expected within a <div> tag with the id "contents".
        The function prints the title and content, and returns the content as a string.
        If the request fails, it prints the status code.
    """
    urls = [url]
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    # print(docs)

    # bs_transformer = BeautifulSoupTransformer()
    # docs_transformed = bs_transformer.transform_documents(
    #     docs, tags_to_extract=["body"]
    # )

    # content = docs_transformed[0].page_content

    return docs
