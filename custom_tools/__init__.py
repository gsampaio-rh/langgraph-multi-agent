from langchain.tools.render import render_text_description_and_args
from custom_tools.website_crawl import website_crawl, extract_content
from custom_tools.duck_search import duckSearch
from custom_tools.wiki_query import wiki
from custom_tools.arxiv_query import arxiv

# Expose all tools in a list for easier import
custom_tools = [duckSearch, wiki, arxiv, website_crawl]

# Generate the tools description (already in your code)
tools_description = (
    render_text_description_and_args(custom_tools).replace("{", "{{").replace("}", "}}")
)

# Create a list of tool names
tools_names = [tool.name for tool in custom_tools]
