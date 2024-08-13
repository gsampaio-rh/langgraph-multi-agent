from custom_tools.website_crawl import website_crawl
from custom_tools.duck_search import duckSearch
from custom_tools.wiki_query import wiki
from custom_tools.arxiv_query import arxiv

# Expose all tools in a list for easier import
custom_tools = [duckSearch, wiki, arxiv, website_crawl]
