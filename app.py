from flask import Flask, redirect, render_template, url_for, Markup, request
import oeis
import urllib
import re
from jinja2 import escape
import werkzeug.routing

basestr = unicode

app = Flask(__name__)

cache = {}
def get_url(url):
	if url in cache:
		return cache[url]
	else:
		data = urllib.urlopen(url).read().decode(encoding='utf-8')
		cache[url] = data
		print('got %s' % url)
		return data

class SequenceConverter(werkzeug.routing.BaseConverter):
	def __init__(self,url_map):
		super(SequenceConverter,self).__init__(url_map)
		self.regex = 'A\\d{6}'

	def to_python(self,value):
		return value

	def to_url(self,value):
		return value

app.url_map.converters['sequence'] = SequenceConverter

@app.template_filter('multiline')
def multiline_filter(s):
	lines = basestr(s).split('\n')
	return Markup('<div class="multiline">'+'\n'.join('<div class="line">%s</div>' % line for line in lines)+'</div>')

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
	return render_template('index.html',focus_search=True)

@app.route('/<sequence:index>')
def show_entry(index):
	data = get_url('http://oeis.org/search?q=id:%s&fmt=text' % index)
	a_file = data.split('\n\n')[2]

	entry = oeis.Entry(a_file)

	return render_template('show_entry.html',entry=entry,query='id:%s' % entry.index)

@app.route('/<sequence:index>/<anything>')
def entry_extra(index,anything):
	return redirect('http://oeis.org/%s/%s?%s' % (index,anything,request.query_string))

@app.route('/search/')
def search(**kwargs):
	query = request.args.get('q')
	start = int(request.args.get('start',0))

	if not query:
		return redirect(url_for('index'))

	extra_params = {param:request.args.get(param) for param in request.args if param in oeis.search_params}

	total, entries = oeis.search(query=query,start=start,**extra_params)

	end = start + len(entries)

	return render_template('search_results.html',entries=entries,start=start,query=query,total=total,end=end)

@app.route('/user/<username>')
def show_user(username):
	sub_name = username.replace(' ','_')
	wiki_url = 'http://oeis.org/wiki/User:%s' % sub_name
	total_entries, entries = oeis.search(author=username,sort='created')

	return render_template('show_user.html', name=username, wiki_url=wiki_url, entries=entries, total_entries=total_entries)

@app.route('/keyword/<keyword>')
def show_keyword(keyword):
	return redirect('http://oeis.org/search?q=keyword:%s' % keyword)

# An attempt to split out maths notation.
# Would be good if I could think of a way of converting pseudo-TeX to real TeX
re_not_maths = re.compile(r'((?:^|\s+)(?:(?:[(\[][a-zA-Z.,:\\\'\\"]+(?=\s)|[a-zA-Z\'\".,;:]+[)\]]*|A\d{6}|(?<=[a-zA-Z])--?(?=[a-zA-Z])|\d{2}\s\d{4}|_[a-zA-Z\s.-]+_)+(?:$|\s|[()\[\]])+)+)',re.MULTILINE)

app.debug = True

if __name__ == '__main__':
	app.debug = True
	app.run()

