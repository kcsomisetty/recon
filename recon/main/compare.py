import os
import time

"""Custom enum class"""
class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
		
ReconProperty = Enum(["TransactionDate", "TransactionAmount", "WalletReference", "TransactionID", "TransactionDescription", "TransactionNarrative", "TransactionDate"]);

"""Class to represent each line in the reconciliation file"""
class ReconEntry:

	def __init__(self):
		self.values = {}
		self.matched = False
		
	def equals(self, otherObj, columnsToIgnore):
		points = 0
		
		#Combination of transaction ID and transactionDescription is used as primary condition to say if 2 rows are a match.
		#if they dont match, we will treat as no-match
		if self.values[ReconProperty.TransactionID] != otherObj.values[ReconProperty.TransactionID]:
			return points
		
		if self.values[ReconProperty.TransactionDescription] != otherObj.values[ReconProperty.TransactionDescription]:
			return points
		
		for column in self.values.keys():
			if column in columnsToIgnore:
					continue;
			if self.values[column] == otherObj.values[column]:
				points += 1;
			else:
				pass
		return points;
	
	def setKey(self, key, val):
		self.values[key] = val
	
	def getKey(self, key):
		return self.values[key]
	
	def getDate(self):
		return self.getKey(ReconProperty.TransactionDate)

	def getAmount(self):
		return self.getKey(ReconProperty.TransactionAmount)
		
	def getReference(self):
		return self.getKey(ReconProperty.WalletReference)
		
	def getTransactionID(self):
		return self.getKey(ReconProperty.TransactionID)
		
	def __str__(self):
		return self.values[ReconProperty.TransactionID] + ", " + self.values[ReconProperty.TransactionDescription] + ", " + self.values[ReconProperty.TransactionNarrative] + ", " + self.values[ReconProperty.TransactionDate]
		
"""
input: fully qualified file paths of reconciliation files
"""
class CompareUtility:
	def __init__(self):
		pass;
	
	def compare (self, file1, file2, columnsToIgnore):
		startTime = time.time()
		
		#defensive checks
		if not os.path.exists(file1):
			raise Exception("Failed to load " + os.path.basename(file1));
			
		if not os.path.exists(file2):
			raise Exception("Failed to load " + os.path.basename(file2));
		
		file1Unmatched = []
		file1Total = 0
		file1Duplicates = 0
		
		file2Unmatched = []
		file2Total = 0
		file2Duplicates = 0
		
		exactMatch = 0
		partialMatch = 0
		partialMatches1 = []
		partialMatches2 = []
		
		file1Map = {}
		file1Handle = open(file1, "r");
		file1Columns = []
		
		file2Handle = open(file2, "r");
		file2Columns = []

		#read header and remove columns which are not present in recon file
		#redundant check, can be removed
		line = file1Handle.readline();
		file1Columns = line.strip().split(",")
		
		line = file2Handle.readline();
		file2Columns = line.strip().split(",")
		
		#ideally should match the column names as well, but column count is sufficient for now.
		if len(file1Columns) != len(file2Columns):
			return "Error: File formats are different"
		
		for c in columnsToIgnore:
			if c not in file1Columns:
				columnsToIgnore.remove(c)
		
		#minimum number of columns to match to be called perfect match
		columnsThreshold = len(file1Columns) - len(columnsToIgnore)
		
		while True:
			line = file1Handle.readline().strip().lower();
			
			#eof
			if not line: 
				break;
			
			#blank lines
			if len(line) <= 0:
				continue;
				
			file1Total += 1
			valueList = line.split(",")
			valueList.pop()
			if len(valueList) != len(file1Columns):
				#row does not have sufficient values. abort
				raise Exception("Data processing error : File format may be wrong")
				
			r = ReconEntry();
			for ix in range(0, len(file1Columns)):
				r.setKey(file1Columns[ix], valueList[ix])
			
			#TODO: duplicate transaction objects are overridden with out warning
			file1Map[r.getKey(ReconProperty.TransactionID) + r.getKey(ReconProperty.TransactionDescription)] = r;
			
		file1Handle.close()
		
		while True:
			line = file2Handle.readline().strip().lower();
			
			#eof
			if not line: 
				break;
				
			if len(line) <= 0:
				continue;
			
			file2Total += 1
			
			valueList = line.split(",")
			#ignore the last comma symbol
			valueList.pop() 
			
			if len(valueList) != len(file2Columns):
				#row does not have sufficient values. abort
				raise Exception("Data processing error : File format may be wrong")
			
			file2Entry = ReconEntry();
			
			for ix in range(0, len(file2Columns)):
				file2Entry.setKey(file1Columns[ix], valueList[ix])
			
			#check for matches
			try:
				file1Entry = file1Map[file2Entry.getKey(ReconProperty.TransactionID) + file2Entry.getKey(ReconProperty.TransactionDescription)]
				if file1Entry.matched == False:
					points = file1Entry.equals(file2Entry, columnsToIgnore)
					if points != columnsThreshold:
						#Partial Match
						partialMatches1.append(file1Entry)
						partialMatches2.append(file2Entry)
					else:
						#Exact Match
						exactMatch += 1
					file1Entry.matched = True
					file1Map[file2Entry.getKey(ReconProperty.TransactionID) + file2Entry.getKey(ReconProperty.TransactionDescription)] = file1Entry
				else:
					#Already matched, ignore and move on
					pass
			except KeyError:
				#No match
				file2Unmatched.append(file2Entry)
			except Exception as e:
				#unknown error
				raise 
		
		file2Handle.close()
		
		for fileEntry in file1Map.values():
			if fileEntry.matched == False:
				file1Unmatched.append(fileEntry)
		
		op = {}
		op["partialmatches"] = len(partialMatches1)
		op["partialmatchesList1"] = partialMatches1
		op["partialmatchesList2"] = partialMatches2
		
		op["file1_name"] = os.path.basename(file1)
		op["file1_total"] = file1Total
		op["file1_exactmatches"] = exactMatch
		op["file1_unmatched"] = len(file1Unmatched)
		op["file1_unmatchedList"] = file1Unmatched
		op["file1_duplicates"] = op["file1_total"] - (op["file1_exactmatches"] + op["file1_unmatched"] + op["partialmatches"])
		
		op["file2_name"] = os.path.basename(file2)
		op["file2_total"] = file2Total
		op["file2_exactmatches"] = op["file1_exactmatches"]
		op["file2_unmatched"] = len(file2Unmatched)
		op["file2_unmatchedList"] = file2Unmatched
		op["file2_duplicates"] = op["file2_total"] - (op["file2_exactmatches"] + op["file2_unmatched"] + op["partialmatches"])
		op["totalTime"] = str(round((time.time() - startTime),2) ) + " seconds"
		
		return op;
