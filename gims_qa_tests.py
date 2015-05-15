from qa_core import qa_test




@qa_test
def readCount(sequencingFileName, sequencingType):
	return 100
	
@qa_test
def coverage():
	return 100
	
# @qa_test
# def coverageQThirtyPlus():
# 	return 100

@qa_test	
def qcStatus(coverageThreshold=None):
	return "Pass"
	
