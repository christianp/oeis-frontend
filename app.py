from flask import Flask, redirect, render_template, url_for, Markup
import oeis
import urllib.request
import re
from jinja2 import escape

cache = {}
def get_url(url):
	if url in cache:
		return cache[url]
	else:
		request = urllib.request.urlopen(url).read().decode()
		cache[url] = request
		print('got %s' % url)
		return request

app = Flask(__name__)

@app.template_filter('multiline')
def multiline_filter(s):
	lines = str(s).split('\n')
	return Markup('\n'.join('<div class="line">%s</div>' % line for line in lines))

@app.template_filter('addlinks')
def addlinks_filter(s):
	s = str(escape(s))
	bits = re_not_maths.split(s)
	for i in range(2,len(bits),2):
		if bits[i]:
			bits[i] = '<span class="maths">%s</span>' % bits[i]
	s = ''.join(bits)
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

@app.route('/entry/<index>')
def show_entry(index):
	request = get_url('http://oeis.org/search?q=id:%s&fmt=text' % index)
	a_file = request.split('\n\n')[2]

	entry = oeis.Entry(a_file)

	return render_template('entry.html',entry=entry)

@app.route('/search/<query>')
def search(query):
	request = get_url('http://oeis.org/search?q=%s&fmt=text' % query)
	a_files = request.split('\n\n')[2:-1]
	entries = [oeis.Entry(a_file) for a_file in a_files]

	return render_template('search_results.html',entries=entries)

@app.route('/user/<username>')
def show_user(username):
	sub_name = username.replace(' ','_')
	return redirect('http://oeis.org/wiki/User:%s' % sub_name)

@app.route('/keyword/<keyword>')
def show_keyword(keyword):
	return redirect('http://oeis.org/search?q=keyword:%s' % keyword)

# An attempt to split out maths notation.
# Would be good if I could think of a way of converting pseudo-TeX to real TeX
re_not_maths = re.compile('((?:^|\s+)(?:(?:[()\[\]][a-zA-Z.,:\'\"]+|[a-zA-Z\'\".,;:]+[)\]]*|A\d{6}|(?<=[a-zA-Z])--?(?=[a-zA-Z])|\d{2}\s\d{4}|_[a-zA-Z\s.-]+_)+(?:$|\s+|[()\[\]])+)+)',re.MULTILINE)

if __name__ == '__main__':
	app.debug = True
	app.run()

