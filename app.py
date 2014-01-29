from flask import Flask, redirect, render_template, url_for, Markup
import oeis
import urllib.request
import re

app = Flask(__name__)

@app.template_filter('multiline')
def multiline_filter(s):
	lines = s.split('\n')
	return '\n'.join('<div class="line">%s</div>' % line for line in lines)

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

@app.route('/entry/<index>')
def show_entry(index):
	request = urllib.request.urlopen('http://oeis.org/search?q=id:%s&fmt=text' % index).read().decode()
	a_file = request.split('\n\n')[2]

	entry = oeis.Entry(a_file)

	return render_template('entry.html',entry=entry)

@app.route('/search/<query>')
def search(query):
	request = urllib.request.urlopen('http://oeis.org/search?q=%s&fmt=text' % query).read().decode()
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

if __name__ == '__main__':
	app.debug = True
	app.run()

