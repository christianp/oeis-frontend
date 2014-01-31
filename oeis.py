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

def get_entry(index):
	request = urllib.urlopen('http://oeis.org/search?q=id:%s&fmt=text' % index).read().decode(encoding='utf-8')
	a_file = request.split('\n\n')[2]
	return Entry(a_file)

