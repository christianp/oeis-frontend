from flask import Flask, redirect, render_template, url_for, Markup, request
import oeis
import urllib
import re
from jinja2 import escape

basestr = unicode

cache = {}
def get_url(url):
	if url in cache:
		return cache[url]
	else:
		data = urllib.urlopen(url).read().decode(encoding='utf-8')
		cache[url] = data
		print('got %s' % url)
		return data

app = Flask(__name__)

@app.template_filter('multiline')
def multiline_filter(s):
	lines = basestr(s).split('\n')
	return Markup('\n'.join('<div class="line">%s</div>' % line for line in lines))

@app.template_filter('maths')
def maths_filter(s):
	s = basestr(escape(s))
	bits = re_not_maths.split(s)
	for i in range(2,len(bits),2):
		if bits[i]:
			bits[i] = '<span class="maths">%s</span>' % bits[i]
	return ''.join(bits)

@app.template_filter('addlinks')
def addlinks_filter(s):
	s = re.sub('(^|[\\W])_(.*?)_([\\W]|$)',link_to_author,s)
	s = re.sub('(A\\d{6})',link_to_sequence,s)

	return Markup(s)

def link_to_author(match):
	groups = match.groups('')
	name = groups[1]
	return groups[0]+render_template('link_to_author.html',name=name)+groups[2]

def link_to_sequence(match):
	index = match.group(0)
	return render_template('link_to_sequence.html',index=index)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/entry/<index>')
def show_entry(index):
	data = get_url('http://oeis.org/search?q=id:%s&fmt=text' % index)
	a_file = data.split('\n\n')[2]

	entry = oeis.Entry(a_file)

	return render_template('show_entry.html',entry=entry)

@app.route('/search/')
def search():
	query = request.args.get('q')
	start = int(request.args.get('start',0))
	data = get_url('http://oeis.org/search?q=%s&start=%i&fmt=text' % (query,start))
	sections = data.split('\n\n')
	total = int(re.search('Showing \d+-\d+ of (?P<total>\d+)',sections[1]).group('total'))
	a_files = data.split('\n\n')[2:-1]
	entries = [oeis.Entry(a_file) for a_file in a_files]

	return render_template('search_results.html',entries=entries,start=start,query=query,total=total)

@app.route('/user/<username>')
def show_user(username):
	sub_name = username.replace(' ','_')
	return redirect('http://oeis.org/wiki/User:%s' % sub_name)

@app.route('/keyword/<keyword>')
def show_keyword(keyword):
	return redirect('http://oeis.org/search?q=keyword:%s' % keyword)

# An attempt to split out maths notation.
# Would be good if I could think of a way of converting pseudo-TeX to real TeX
re_not_maths = re.compile(r'((?:^|\s+)(?:(?:[(\[][a-zA-Z.,:\'\"]+(?=\s)|[a-zA-Z\'\".,;:]+[)\]]*|A\d{6}|(?<=[a-zA-Z])--?(?=[a-zA-Z])|\d{2}\s\d{4}|_[a-zA-Z\s.-]+_)+(?:$|\s|[()\[\]])+)+)',re.MULTILINE)

app.debug = True

if __name__ == '__main__':
	app.debug = True
	app.run()

