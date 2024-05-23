import markdown
import re

from templates import CONTENT_TEMPLATE, MATH_SCRIPT, CODE_SCRIPT, NAVBAR, add_piece

SPECIAL_CHARS = '_*'

def convert_markdown(input_file, output_file):
	with open(input_file, 'r') as f:
		md = f.read()

	# Extract title and date
	eod = md.find('\n', md.find('\n')+1)
	title, date = md[1:eod].split('\n')
	md = md[eod+1:]

	# Format code blocks for highlight.js and make markdown converter ignore them
	code_blocks: list[tuple[str,str]] = re.findall(r'```(\w+)\n(.*?)```', md, flags=re.DOTALL)
	for lang, code in code_blocks:
		code_rep = code.replace('<', '&lt').replace('>', '&gt').strip()
		code_html = f"<div class='code-block'><pre><code class='language-{lang}'>{code_rep}</code></pre></div>"
		md = md.replace(f'```{lang}\n{code}```', code_html)

	content = markdown.markdown(md)

	# Replace special characters with two back slashes to maintain latex format
	math_blocks: list[str] = list(set(re.findall(r'(\$[^$]+\$)', content)))
	for math in math_blocks:
		if not set(SPECIAL_CHARS) & set(math): continue

		math_rep = math
		for c in SPECIAL_CHARS:
			math_rep = math_rep.replace(c, '\\' + c)
		content = content.replace(math, math_rep)

	with open(CONTENT_TEMPLATE, 'r') as fr, open(output_file, 'w') as fw:
		html = fr.read().replace('{title}', title).replace('{date}', date).replace('{content}', content)
		html = add_piece(html, '{nav}', NAVBAR, True)
		html = add_piece(html, '{math}', MATH_SCRIPT, math_blocks)
		html = add_piece(html, '{code}', CODE_SCRIPT, code_blocks)
		fw.write(html)

	print(f'Markdown file {input_file} converted to HTML and saved as {output_file}')