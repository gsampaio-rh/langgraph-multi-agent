from tools.website_crawl import website_crawl
from tools.duck_search import duckSearch
from tools.wiki_query import wiki
from tools.arxiv_query import arxiv

# Expose all tools in a list for easier import
tools = [duckSearch, wiki, arxiv, website_crawl]
