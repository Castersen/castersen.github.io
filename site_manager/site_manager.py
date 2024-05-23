from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from bs4 import BeautifulSoup

from templates import ARTICLE_TEMPLATE, NAVBAR, ARTICLE_PAGE, INDEX_PAGE, BLOG_DIR, add_piece

@dataclass
class Article:
	title: str
	date_str: str
	date: datetime
	article_file: str
	index_file: str

	def __lt__(self, other: 'Article') -> bool:
		return self.date < other.date

def create_page(template_page, output_file, key, data):
	with open(template_page, 'r') as fr, open(output_file, 'w') as fw:
		t = fr.read().replace(key, data)
		t = add_piece(t, '{nav}', NAVBAR, True)
		fw.write(BeautifulSoup(t, 'html.parser').prettify())
	print(f'Generated page {template_page} as {output_file}')

def update_blog(article_paths: list[Path], output_file, index_page):
	articles: list[Article] = []
	for article_path in article_paths:
		with open(article_path, 'r') as f:
			title = f.readline()[1:].strip()
			date = f.readline().strip()
			f_date = date.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
			f_date = datetime.strptime(f_date, '%B %d, %Y')
			article_name = article_path.name.replace('md', 'html')
			article_file = '../' + BLOG_DIR + '/' + article_name
			articles.append(Article(title, date, f_date, article_file, article_file[3:]))

	articles.sort(reverse=True)
	with open(ARTICLE_TEMPLATE, 'r') as f:
		article_template = f.read()

	article_html = []
	for article in articles:
		article_html.append(article_template.replace('{date}', article.date_str)
					  		.replace('{title}', article.title)
							.replace('{article}', article.article_file))

	# Only grab the most recent 4 articles for the home page
	index_articles = ''.join(article_html[:4])

	for article in articles:
		index_articles = index_articles.replace(article.article_file, article.index_file)

	page_articles = ''.join(article_html)

	create_page(ARTICLE_PAGE, output_file, '{articles}', page_articles)
	create_page(INDEX_PAGE, index_page, '{articles}', index_articles)