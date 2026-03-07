import sys
from newspaper import Article

url = 'https://www.ludunwayoo.com/news-mm/2026/03/150084/'
article = Article(url)
article.download()
article.parse()
print(f"Title: {article.title}")
print(f"Text content: \n{article.text}")
