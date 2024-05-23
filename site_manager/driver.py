#!/usr/bin/env python3
import argparse
from pathlib import Path
from article_parser import convert_markdown
from site_manager import update_blog
from templates import SITE_PROJECT_DIR, SITE_PROJECT_MD_DIR, SITE_BLOG_DIR, SITE_BLOG_MD_DIR, SITE_ARTICLES_PAGE, SITE_INDEX_PAGE

def convert_md(md_dir: Path, html_dir: Path, refresh: bool):
    md_list = [blog_md for blog_md in md_dir.iterdir()]    
    converted_html_list = [blog.name[:-5] for blog in html_dir.iterdir()]

    for md in md_list:
        if md.name[:-3] not in converted_html_list or refresh:
            convert_markdown(md, (html_dir / md.name.replace('md', 'html')))

def main():
    parser = argparse.ArgumentParser(description='Manages site updates')
    parser.add_argument('-u', '--update', action='store_true', help='Update site')
    parser.add_argument('-c', '--convert', action='store_true', help='Convert markdown to html')
    parser.add_argument('-b', '--blog', action='store_true', help='Convert blog markdown to html')
    parser.add_argument('-p', '--project', action='store_true', help='Convert project markdown to html')
    parser.add_argument('-r', '--refresh', action='store_true', help='Refresh all pages')

    args = parser.parse_args()

    if (args.convert and args.blog) or args.refresh:
        convert_md(SITE_BLOG_MD_DIR, SITE_BLOG_DIR, args.refresh)
    if (args.convert and args.project) or args.refresh:
        convert_md(SITE_PROJECT_MD_DIR, SITE_PROJECT_DIR, args.refresh)
    if args.update:
        blogs = [blog for blog in SITE_BLOG_MD_DIR.iterdir()]
        update_blog(blogs, SITE_ARTICLES_PAGE, SITE_INDEX_PAGE)

if __name__ == '__main__':
    main()