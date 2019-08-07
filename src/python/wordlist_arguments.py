def add_arguments(parser):
	parser.add_argument(
		'files',
		type=str,
		nargs='+',
		help='The epidoc xml files to process'
	)
	parser.add_argument(
		"--html",
		help="Output list as html file(s)",
		action="store_true"
	)
	parser.add_argument(
		"--csv",
		help="Output list as csv file",
		action="store_true"
	)
	parser.add_argument(
		"--plaintext",
		help="Create flat text document for each parsed file",
		action="store_true"
	)
	parser.add_argument(
		"--silent",
		help="Don't print the word list to the console",
		action="store_true"
	)
	#parser.add_argument("--duplicates",
	#                    help="""Include each instance of every word in
	#                            the word list""",
	#                    action="store_true")
	parser.add_argument(
		"--nodiplomatic",
		help="""Do not include words extracted from diplomatic editions
        in word list""",
		action="store_true"
	)
	parser.add_argument(
		"--fileexception",
		help="Print exceptions for files which could not be read",
		action="store_true"
	)
	parser.add_argument(
		"--langfiles",
		help="Write a seperate file for each language",
		action="store_true"
	)
	parser.add_argument("-s", "--sort", type=str,
	                    help="Sort the list by the specified fields")
	parser.add_argument(
		"-n", "--name", type=str,
		help="The name of the output file without the extension"
	)
	parser.add_argument(
		"-f", "--flat", type=str,
		help="Specify the location to store plain text files."
	)
	parser.add_argument(
		"--nolemma",
		help="""Don't lemmatize words before writing to plain text
		files""",
		action="store_true"
	)
	parser.add_argument(
		"--engstops",
		help="""Do not include translated English words  that are in
		the stop list.""",
		action="store_true"
	)
	parser.add_argument(
		"--repl",
		help="start repl after tasks",
		action = "store_true"
	)
	parser.add_argument(
		"--html_general",
		help="output general word list as html",
		action = "store_true"
	)
	parser.add_argument(
		"--google_sheets",
		help="create a wordlist in Google Sheets for manual correction",
		action="store_true"
	)
	#parser.add_argument("--new_system", action = "store_true")
	parser.add_argument("--old_system", action = "store_true")
	return parser
