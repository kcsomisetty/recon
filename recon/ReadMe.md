## How to run this program?
	Requirements.
		Python 2.7+
		Django 1.9+
		Tested on windows 10 + chrome
		
	This Django app can be run as a self hosted app, 
		download the code place it in a folder
		open command prompt and nagive to folder <clone path>\recon
		run the command "python manage.py runserver --nothreading"
		you should see a message "Starting development server at http://127.0.0.1:8000/"
		
	Launch browser and type the url "http://127.0.0.1:8000/"
	
## Solution Approach
	The problem statement to design a transaction reconciliation system, even though provides sufficient details, is still very much open ended question.
	But as suggested in the problem statement, I tried to keep things simple, assumed few things and ruled out few other. I will describe my assumptions and approach to the solution and in a separate section will describe on scaling challenges.
	
	Assumptions:
		1. Recon files rarely have changes in their formats. 
			code to detect basic inconsistencies is written, but assumed that file formats dont change dialy.
		2. A real world recon system usually has unique key pre-defined between 2 parties (tutuka and processor?) to match transactions. (ex: retrieval reference number of 8583)
			I started out assuming TransactionID would be unique, but after going through sample files, I realized that its combination of TransactionID + TransactionDescription which will be our unique key.
		3. It is possible to have duplicates in recon files for various reasons.
		4. It is possible that the 2 parties doing reconciliation, record different time stamps for the same transaction (owing to network delays)
		5. To call a transaction a perfect match, TransactionAmount should match not as is.
			I understand this assumption is counter intutive, but since the probability of calling a transaction row partial is very low, i wanted to take this chance and put a less strict validation for amount field.
		6. Transactions from Day T will appear in Day T+1 file. 
			To address scenario where Day T transactions appear in Day T+2 or later, a database backend is required. Since the problem statement ruled it out, I am ignore this usecase.
		7. recon files are roughly of same size. (5% deviation)
			In real world, recon files from both parties, very rarely differ in size. (number of transactions per file)
	
	Design
		I will skip discussing things which are trivial. like,
			1. error validation, sanity checks about formats and data.
			2. file uploading logic
			3. building django template to present results to user of the app.
		The solution at the core is very simple.
		The program is passed 2 files (file1, file2) and list of columns which can be ignored while comparing transactions
			1. iterate through file1, line by line
			2. prepare a custom object which holds these values each line holds
			3. Store this line in a hashmap with the unique key, represented by "TransactionID + TransactionDescription"
			4. iterate through file2, line by line
			5. prepare a custom object which holds these values each line from file2
			6. check if this object is present in the file1's map (from step:3) by using the unique key calculated from file2's obj
			7. if key is present, 
				a. check how many columns are equal between these two lines.
				b. if the number matched columns, is equal to a defined threshold value, we treat as exact match.
				c. if the number matched columns, is not equal to a defined threshold value, we treat as partial match.
				d. mark this row as matched in file1 object.
			8. if key is not present, mark this row from file 2 as unmatched.
	
	Possible Performance issues:
		1. Since file1's data is kept in memory and file2 is iterated line by line, A possible memory bottleneck can happen if file1 is abnormally huge. 
			Such cases, can be addressed by keep smaller file (of the two) in memory and iterate larger file to keep run time memory requirement in check.
			But, give the nature of reconciliation, this will not hit.
		2. File Uploads (minor):
			Since, this is a sample project, the file upload logic implemented here is very trivial and completely done in memory. 
			This approach is not recommended for production system. Recommended ways are ftp/Dropbox/Cloud storage.
	
	How to determine if a row is a partial match:
		This is describe above in 7.b and 7.c
		Apart from this, i have provided an UI option for the engineer to select which columns to ignore while comparing transactions. The list is hardcoded for simplicity, but can be made dynamic as well.	
	
## What about Scaling ?
	Though reconciliation system is an offline EOD task and not a real time, 
	Large enough recon files, can overwhelm the processing system interms of memory requirements or processing time.
	The above algorithm though works, is not suitable for really large files.
	Here is a possible list of changes that would help scaling
		1. store file1's contents in persistent backend, which index on unique key
		2. Use SSD storage for storing file2. (SSD have decent random read speed over HDD)
		3. Partition transactions from file2 into multiple buckets (N rows per bucket) 
		4. Process each bucket using an independent thread and aggregate results (Map-Reduce style)
			Since, file1Map is presisted, and used only to compare, it can be shared between threads.
		5. Reconciliation can be further sped up if file1's transactions are stored in cassandra (only if replication factor is tuned), This facilitates, parallelization on read side.
			But this comes at a cost, from increased storage requirements.
