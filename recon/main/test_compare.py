import unittest
from django.http import *
from compare import *

class AddressBookTest(unittest.TestCase):
	def setUp(self):
		pass
		
	def test_ReconEntry_getset(self):
		re = ReconEntry()
		re.setKey("key", "someVal");
		val = re.getKey("key")
		self.assertEquals(val, "someVal");
		
	def test_ReconEntry_getset(self):
		re = ReconEntry()
		re.setKey(ReconProperty.TransactionID, "123");
		re.setKey(ReconProperty.TransactionDescription, "Debit");
		re.setKey(ReconProperty.WalletReference, "xyz");
		re.setKey(ReconProperty.TransactionNarrative, "TUTUKA * Charge");
		
		re2 = ReconEntry()
		re2.setKey(ReconProperty.TransactionID, "123");
		re2.setKey(ReconProperty.TransactionDescription, "Debit");
		re2.setKey(ReconProperty.WalletReference, "abc");
		re2.setKey(ReconProperty.TransactionNarrative, "TUTUKA * reverse");
		
		points = re.equals(re2, [])
		
		self.assertEquals(points, 2);
		
	def test_ReconEntry_getset_ignorecolumns(self):
		re = ReconEntry()
		re.setKey(ReconProperty.TransactionID, "123");
		re.setKey(ReconProperty.TransactionDescription, "Debit");
		re.setKey(ReconProperty.WalletReference, "xyz");
		re.setKey(ReconProperty.TransactionNarrative, "TUTUKA * Charge");
		
		re2 = ReconEntry()
		re2.setKey(ReconProperty.TransactionID, "123");
		re2.setKey(ReconProperty.TransactionDescription, "Debit");
		re2.setKey(ReconProperty.WalletReference, "abc");
		re2.setKey(ReconProperty.TransactionNarrative, "TUTUKA * Charge");
		
		points = re.equals(re2, [ReconProperty.WalletReference])
		
		self.assertEquals(points, 3);
		
	def test_compare_missingfiles(self):
		file1 = "compare.py"
		file2 = "none2.csv"
		exceptionHappened = False
		
		try:
			compare(file1, file2, [])
		except:
			exceptionHappened = True
		
		self.assertEquals(exceptionHappened, True);

		
	def test_compare_missingfiles(self):
		file1 = "none.csv"
		file2 = "compare.py"
		exceptionHappened = False
		
		try:
			compare(file1, file2, [])
		except:
			exceptionHappened = True
		
		self.assertEquals(exceptionHappened, True);
		
if __name__ == '__main__':
	unittest.main()