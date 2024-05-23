from pathlib import Path

SITE_ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = 'docs'

# Site internals
SITE_PAGES_DIR = SITE_ROOT_DIR / SITE_DIR / 'pages'
SITE_ARTICLES_PAGE = SITE_PAGES_DIR / 'articles.html'
SITE_PROJECTS_PAGE = SITE_PAGES_DIR / 'projects.html'
SITE_INDEX_PAGE = SITE_ROOT_DIR / SITE_DIR / 'index.html'

BLOG_DIR = 'blog'
SITE_BLOG_DIR = SITE_ROOT_DIR / SITE_DIR / BLOG_DIR
SITE_BLOG_MD_DIR = SITE_ROOT_DIR / 'blog_md'

SITE_PROJECT_DIR = SITE_ROOT_DIR / SITE_DIR / 'projects'
SITE_PROJECT_MD_DIR = SITE_ROOT_DIR / 'project_md'

# Site manager internals
TEMPLATE_DIR = 'templates'
PIECES = 'pieces'
PAGES_DIR = 'pages'

# Templates
ARTICLE_TEMPLATE = SITE_ROOT_DIR / TEMPLATE_DIR / 'article_template.html'
CONTENT_TEMPLATE = SITE_ROOT_DIR / TEMPLATE_DIR / 'content_template.html'
PROJECT_TEMPLATE = SITE_ROOT_DIR / TEMPLATE_DIR / 'project_template.html'

# Pages
ARTICLE_PAGE = SITE_ROOT_DIR / TEMPLATE_DIR / PAGES_DIR / 'articles_page.html'
INDEX_PAGE = SITE_ROOT_DIR / TEMPLATE_DIR / PAGES_DIR / 'index_page.html'
PROJECT_PAGES = SITE_ROOT_DIR / TEMPLATE_DIR / PAGES_DIR / 'projects_page.html'

# Components
NAVBAR = SITE_ROOT_DIR / TEMPLATE_DIR / PIECES / 'nav_bar.html'
MATH_SCRIPT = SITE_ROOT_DIR / TEMPLATE_DIR / PIECES / 'math_script.html'
CODE_SCRIPT = SITE_ROOT_DIR / TEMPLATE_DIR / PIECES / 'highlight_script.html'

def add_piece(text: str, key: str, script: str, should_add) -> str:
	with open(script, 'r') as f:
		return text.replace(key, f.read()) if should_add else text.replace(key + '\n', '')