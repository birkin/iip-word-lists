#!/usr/bin/env bash

cd ..

update=1;
exceptions=0;
silent=0;
google_sheets=0;
use_existing=0;
file_name="abil0001";

if [ -z "$DOCS" ]; then
	export DOCS="docs"
fi
echo "Using data in $DOCS."

# Procedure for generating the appropriate arguments and running the python script
# It is not clear to me why this is a procedure, because it is called only once below
run_script() {
	source environment/bin/activate;
	# pip install oauth2client
	cd $DOCS;
	exceptions_flag=""
	new_system_flag=""
	silent_flag=""
	google_sheets_flag=""
	if [ $exceptions == 1 ]; then
		exceptions_flag="--fileexception"
	fi
	if [ $silent == 1 ]; then
		silent_flag="--silent"
	fi
	if [ $google_sheets == 1 ]; then
		google_sheets_flag="--google_sheets"
	fi

	python3 ../src/python/wordlist.py texts/xml/$file_name.xml --nodiplomatic --html_general\
	--csv $google_sheets_flag --plaintext --flat texts/plain $exceptions_flag $new_system_flag $silent_flag;
	cd ..;

	echo $file_name;
	echo $(<docs/texts/plain/$file_name.txt)
}

for word in $*; do
	if [ "$word" == "--help" ] || [ "$word" == "-h" ]; then
		printf "Usage:\n
		-h, --help            Print this message.
		--no-update, -nu      Do not fetch epidoc files from github.
		--exceptions, -e      If an exception occurs in the python \
		code, print the error message.
		--use-existing, -ue   Do not rebuild the word lists.\n" |
		sed -e 's:\t::g';
		exit;
	elif [ "$word" == "--no-update" ] || [ "$word" == "-nu" ]; then
		update=0;
	elif [ "$word" == "--silent" ] || [ "$word" == "-s" ]; then
		silent=1;
	elif [ "$word" == "--google_sheets" ] || [ "$word" == "-gs" ]; then
		google_sheets=1;
	elif [ "$word" == "--exceptions" ] || [ "$word" == "-e" ]; then
		exceptions=1;
	elif [ "$word" == "--new-system" ] || [ "$word" == "-ns" ]; then
		new_system=1;
	else
		file_name="$word";
		file_name=$(echo $file_name | cut -d'.' -f 1);
	fi

done

run_script;