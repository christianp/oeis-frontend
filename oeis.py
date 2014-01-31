import re
import operator
import itertools
import urllib

re_entry_line = re.compile('%(?P<linetype>\w) (?P<index>A\d{6}) (?P<content>.*)$')
class Entry:
	index = ''
	other_indices = []
	name = ''
	author = ''
	offset = 0
	first_non_one_term = 0
	references = []
	links = []
	cross_references = ''
	formula = ''
	extensions = ''
	examples = ''
	comments = ''
	keywords = []

	programs = []

	terms_lines = ['','','']
	
	@property
	def terms(self):
		all_terms = ''.join(self.terms_lines)
		return [int(x) for x in all_terms.split(',')]
	
	def __init__(self,str):
		lines = str.split('\n')
		def get_matches():
			for line in lines:
				try:
					yield re_entry_line.match(line).groupdict()
				except AttributeError:
					pass
		matches = list(get_matches())

		get_linetype = operator.itemgetter('linetype')
		fields = {key:'\n'.join(match['content'] for match in value) for key,value in itertools.groupby(matches,get_linetype)}

		get = lambda key: fields.get(key,'')

		self.index = matches[0]['index']
		other_indices = get('I')
		if other_indices:
			self.other_indices = other_indices.split(' ')

		self.name = get('N')
		self.author = get('A')

		offset = re.match('(\d+),(\d+)',get('O'))
		self.offset = int(offset.group(1))
		self.first_non_one_term = int(offset.group(2))

		self.terms_lines = [fields.get('V',get('S')),fields.get('W',get('T')),fields.get('X',get('U'))]

		if 'D' in fields:
			self.references = fields.get('D').split('\n')
		if 'H' in fields:
			self.links = get('H').split('\n')

		self.formula = get('F')
		self.cross_references = get('Y')
		self.extensions = get('E')
		self.examples = get('e')
		self.comments = get('C')

		if 'K' in fields:
			self.keywords = get('K').split(',')

		self.programs = []
		if 'p' in fields:
			self.programs.append(('Maple',fields.get('p')))
		if 't' in fields:
			self.programs.append(('Mathematica',fields.get('t')))
		if 'o' in fields:
			others = get('o')
			programs = re.split('^\((\w+)\)\s*',others,0,re.MULTILINE)[1:]
			pairs = [programs[i:i+2] for i in range(0,len(programs),2)]
			self.programs += pairs
		self.programs.sort(key=operator.itemgetter(0))

	def __repr__(self):
		return '%s %s' % (self.index, self.name)

search_prefixes = ['id','seq','signed','name','offset','comment','ref','link','formula','example','maple','mathematica','program','xref','keyword','author','extension','subseq','signedsubseq']
search_params = ['query','sequence','contains','sort','start']+search_prefixes

def make_search_query(**kwargs):
	query = []

	if 'query' in kwargs:	#general query
		query.append(kwargs['query'])

	if 'sequence' in kwargs:	#subsequence in order
		query.append(','.join(str(x) for x in kwargs['sequence']))

	if 'contains' in kwargs:	#terms which must be included, in any order
		query.append(' '.join(str(x) for x in kwargs['contains']))

	def safe_quote(s):
		return '"%s"' % s if ' ' in s else s

	for prefix in search_prefixes:
		if prefix in kwargs:
			query.append('%s:%s' % (prefix,safe_quote(kwargs[prefix])))

	return ' '.join(query)

def search(**kwargs):
	args = {'fmt': 'text'}
	
	if 'sort' in kwargs:
		args['sort'] = kwargs['sort']

	if 'start' in kwargs:
		args['start'] = kwargs['start']

	args['q'] = make_search_query(**kwargs)
	args_string = '&'.join('%s=%s' %(key,value) for key,value in args.items())
	url = 'http://oeis.org/search?%s' % args_string

	data = urllib.urlopen(url).read().decode(encoding='utf-8')
	sections = data.split('\n\n')

	total = int(re.search('Showing \d+-\d+ of (?P<total>\d+)',sections[1]).group('total'))
	a_files = data.split('\n\n')[2:-1]
	entries = [Entry(a_file) for a_file in a_files]

	return (total,entries)

def get_entry(index):
	request = urllib.urlopen('http://oeis.org/search?q=id:%s&fmt=text' % index).read().decode(encoding='utf-8')
	a_file = request.split('\n\n')[2]
	return Entry(a_file)

