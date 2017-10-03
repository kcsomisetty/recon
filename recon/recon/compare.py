import os

#how to return results
#generate diffs based on fields
	#this logic should not break when fields are added or removed.
#facility to match unmatched entries from old files
#multi threading
#flexibility to load really rally big files ?
#what about sorting order ?
#can records in file1 repeat ?

maxRowsInMemory = 100000
mismatchThreshold = 20

columnsToIgnore = ["TransactionDate", "TransactionAmount"]
mandatoryMatchColumns = []

#ProfileName,TransactionDate,TransactionAmount,TransactionNarrative,TransactionDescription,TransactionID,TransactionType,WalletReference

class ReconEntry:
	def __init__(self):
		self.columns = {}
		self.TransactionID = ""
		self.matched = False
		
	def equals(self, otherObj):
		points = 0
		
		if self.TransactionID != otherObj.TransactionID:
			return points
			
		for column in self.columns:	
			if self.columns[column] == otherObj.columns[column]:
				#print column, 1
				points += 1;
			else:
				pass#print column, 2
		return points;
		
	def __str__(self):
		return '-'.join(self.columns.values())
		
"""
input: fully qualified file paths of reconciliation files
"""
def compare (file1, file2):
	result = []
	exactMatch = 0
	partialMatch = 0
	file1Unmatched = set()
	file2Unmatched = set()
	partialMatches = set()
	#check if files exists
	if not os.path.exists(file1):
		return "Failed to load " + file1
		
	if not os.path.exists(file2):
		return "Failed to load " + file2
	
	file1Map = {}
	file1Handle = open(file1, "r");
	file1Columns = 0
	
	file2Map = {}
	file2Handle = open(file2, "r");
	file2Columns = 0

	#read header and decide number of columns
	line = file1Handle.readline();
	file1Columns = line.strip().split(",")
	columnsThreshold = len(file1Columns) - len(columnsToIgnore)
	#print columnsThreshold;
	
	line = file2Handle.readline();
	file2Columns = line.strip().split(",")
	
	if len(file1Columns) != len(file2Columns):
		return "Error: File formats are different"
	
	file1Map = {}
	#print "hi"
	while True:
		line = file1Handle.readline().strip().lower();
		#print line;
		
		if not line: #eof
			break;
			
		if len(line) <= 0:
			continue;
		#print "hi"
		valueList = line.split(",")
		#print len(valueList)
		#print file1Columns
		#print valueList
		valueList.pop() #ignore the last comma symbol
		if len(valueList) != len(file1Columns):
			#row does not have sufficient values. abort
			exit(1)
			
		ix = -1
		r = ReconEntry();
		for column in file1Columns:
			#print column
			ix+= 1
			if column in columnsToIgnore:
				continue;
			else:
				#print column, valueList[ix]
				r.columns[column] = valueList[ix]
		r.TransactionID = r.columns["TransactionID"]
		#TODO: duplicate transaction objects are overridden with out warning
		file1Map[r.TransactionID] = r;
		
	#for f in file1Map:
	#	print f;
	
	file1Handle.close()
	#print len(file1Map.keys());
	while True:
		line = file2Handle.readline().strip().lower();
		#print line
		if not line: #eof
			break;
			
		if len(line) <= 0:
			continue;
		
		valueList = line.split(",")
		valueList.pop() #ignore the last comma symbol
		if len(valueList) != len(file2Columns):
			#row does not have sufficient values. abort
			exit(1)
				
		ix = -1
		file2Entry = ReconEntry();
		for column in file2Columns:
			ix += 1	
			if column in columnsToIgnore:
				continue;
			else:
				file2Entry.columns[column] = valueList[ix]			
		
		file2Entry.TransactionID = file2Entry.columns["TransactionID"]
		#print file2Entry.columns.keys()
			
		try:
			#print "Hi"
			file1Entry = file1Map[file2Entry.TransactionID]
			#print "entry Found for  " + file1Entry.TransactionID
			points = file1Entry.equals(file2Entry)
			#print points
			if points != columnsThreshold:
				#print "Partial Match"
				#print file1Entry.TransactionID
				#print file2Entry.TransactionID
				#partialMatch += 1
				partialMatches.add(file1Entry.TransactionID)
			else:
				exactMatch += 1
			file1Entry.matched = True
			file1Map[file2Entry.TransactionID] = file1Entry
		except KeyError:
			#print "entry not Found for  " + file2Entry.TransactionID
			file2Unmatched.add(file2Entry)
		except:
			#print "unknown error"
			pass;
			
	file2Handle.close()
	
	op = "Exact Matches : " + str(exactMatch)
	op += "Partial Matches : " + str(len(list(partialMatches)))
	for p in partialMatches:
		op += p
	op += "File 1 Unmatched : " 
	for file1Entry in file1Map.values():
		if file1Entry.matched == False:
			op += file1Entry.TransactionID
		
	op += "File 2 Unmatched " + str(len(file2Unmatched))
	for file2Line in file2Unmatched:
		op += file2Line.TransactionID

#print compare("1.csv", "2.csv")