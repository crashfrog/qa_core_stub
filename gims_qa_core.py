#!/usr/bin/env python

import xml.dom.minidom as dom
import xml.etree.ElementTree as xml
import sys
import os, os.path
from functools import partial
from inspect import getargspec, getfile, currentframe
from os.path import join as j
import subprocess
import textwrap
import imp
from collections import OrderedDict


usage = """ CFSAN Genomics QA Core 0.1
May 15, 2015
Justin Payne
justin.payne@fda.hhs.gov

	usage:
	{0} /path/to/sandbox (production mode)
	{0} [{1}] (single-test mode, for utility and debugging)

"""



qa_tests = OrderedDict()
qa_undecorated_tests = OrderedDict()

def qa_test(qa_func):
	"Decorator to simplify XML interaction"
	qa_undecorated_tests[qa_func.__name__] = qa_func
	def bind_metadata_to_arguments(metadata, qa_func):
		"Find elements in XML with same name as function argument and bind their content"
		for argument in getargspec(qa_func).args:
			elements = metadata.findall(".//{0}".format(argument))
			if len(elements) == 1:
				qa_func = partial(qa_func, **{argument:elements[0].text})
			else:
				qa_func = partial(qa_func, **{argument:[e.text for e in elements]})
		return qa_func()
		
		
	decorated_qa_func = partial(bind_metadata_to_arguments, qa_func=qa_func)
	qa_tests[qa_func.__name__] = decorated_qa_func
	return decorated_qa_func

qa_core = imp.new_module("qa_core")
qa_core.qa_test = qa_test
sys.modules['qa_core'] = qa_core
	

def main(sandbox_path=os.getcwd()):
	with open(j(sandbox_path, 'Input', 'input.xml'), 'rU') as inputfile:
		metadata = xml.parse(inputfile).getroot()
	
	qaoutput = xml.Element("qaQcCoverageOutput")
	outputxml = xml.ElementTree(element=qaoutput)
	
	for name, test in qa_tests.items():
		xml.SubElement(qaoutput, name).text = str(test(metadata))
		
	with open(j(sandbox_path, 'Output', 'output.xml'), 'w') as outputfile:
		d = dom.parseString(xml.tostring(qaoutput))
		d.writexml(outputfile, addindent='    ', newl='\n')
# 		outputxml.write(outputfile, encoding="UTF-8", xml_declaration=True)

@qa_test
def version():
	"Collect repository commit id from git"
	p = os.path.dirname(__file__)
#	 with open(j(p, '.git/refs/heads/master'), 'rU') as head_ref:
# 		ref = head_ref.read().replace('\n', '')
	ref = subprocess.check_output("git -C {0} describe".format(p), shell=True).replace("\n", '')
	return ref




if __name__ == "__main__":
	import gims_qa_tests
	try:
		name, sandbox_path = sys.argv
		
		if not os.path.exists(sandbox_path):
			args = sys.argv[2:]
			try:
				print(sandbox_path + ":", qa_undecorated_tests[sandbox_path](*args))
				quit()
			except KeyError:
				print("Invalid QA test name: {0}".format(sandbox_path))
				quit()
		main(sandbox_path)
	except ValueError:
		print("Missing argument: path to sandbox or name of QA test.")
		commands = " | ".join([':'.join((n, ",".join(["<{0}>".format(a) for a in getargspec(f)[0]]) or 'DELETEME')).replace(':DELETEME', '') for n, f in qa_undecorated_tests.items()])
		print(usage.format(os.path.basename(__file__), textwrap.fill(commands, 79, subsequent_indent='\t\t')))
		quit()