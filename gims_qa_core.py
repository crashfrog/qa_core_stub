import xml.etree.ElementTree as xml
import sys
import os, os.path
from functools import partial
from inspect import getargspec
from os.path import join as j
import subprocess

qa_tests = dict()

def qa_test(qa_func):
	"Decorator to simplify XML interaction"
	def bind_metadata_to_arguments(qa_func, metadata):
		"Find elements in XML with same name as function argument and bind their content"
		for args, varargs, keywords, defaults in getargspec(qa_func):
			for argument in args:
				elements = metadata.findall(".//{0}".format(argument))
				if len(elements) == 1:
					qa_func = partial(qa_func, **{argument:elements[0].text})
				else:
					qa_func = partial(qa_func, **{argument:[e.text for e in elements]})
		return qa_func()
		
		
	decorated_qa_func = partial(bind_metadata_to_arguments, qa_func=qa_func)
	qa_tests[qa_func.__name__] = decorated_qa_func
	return decorated_qa_func
	

def main(sandbox_path=os.getcwd()):
	with open(j(sandbox_path, 'Input', 'input.xml'), 'rU') as inputfile:
		metadata = xml.parse(inputfile).root()
	
	qaoutput = xml.Element("qaQcCoverageOutput")
	outputxml = xml.ElementTree(element=qaoutput)
	
	for name, test in qa_tests.items():
		xml.SubElement(qaoutput, name).text = test(metadata)
		
	with open(j(sandbox_path, 'Output', 'output.xml'), 'w') as outputfile:
		outputxml.write(outputfile, encoding="UTF-8", xml_declaration=True)

@qa_test
def version():
	


if __name__ == "__main__":
	name, sandbox_path = sys.argv
	main(sandbox_path)