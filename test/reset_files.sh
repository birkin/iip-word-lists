#!/usr/bin/env bash

cd ..;

update=1;		# should be update=1 and then set to zero with -nu tag, but I've hacked it temporarily to save trouble for testing
exceptions=0;
silent=0;
google_sheets=0;
use_existing=0;
#new_system=0;

if [ -z "$DOCS" ]; then
	export DOCS="docs"
fi
echo "Using data in $DOCS."

# Procedure for generating the appropriate arguments and running the python script
# -- worldlist.py -- which parses the xml, generates plain text, and lemmatizes
# It is not clear to me why this is a procedure, because it is called only once below
run_script() {
	source environment/bin/activate;
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
	#if [ $new_system == 1 ]; then
	#	new_system_flag="--new_system"
	#fi
	# python3 -i ../src/python/wordlist.py texts/xml/* --nodiplomatic --html_general\
	#  --plaintext --flat texts/plain $google_sheets_flag $exceptions_flag $new_system_flag $silent_flag;
	../src/python/wordlist.py texts/xml/* --nodiplomatic --html_general\
	 --plaintext --flat texts/plain $google_sheets_flag $exceptions_flag $new_system_flag $silent_flag;
	cd ..;
}

# Parse command-line arguments
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
	fi

done

# Delete all of the old files,
# including those generated programmatically and downloaded from the repo

if [ $update == 1 ]; then
	echo "Removing old site...";
	if [ -d $DOCS ]; then
		cd $DOCS;
		if [ $update == 0 ]; then
			mv texts ..;
		fi
		cd ..;
		rm -rf $DOCS
	fi
	mkdir $DOCS
fi

say "updating texts" # Robot voice output so I can do other things while this runs

echo "Updating texts...";
mkdir temp;
cd temp;
wget "https://github.com/Brown-University-Library/iip-texts/archive/master.zip";
# wget $(echo "https://github.com/Brown-University-Library/iip-texts/\
# archive/master.zip" | sed -e 's:\t::g');
unzip master.zip;
mkdir ../$DOCS/texts;
cp -r iip-texts-master/epidoc-files/ ../$DOCS/texts/xml;
# read -p "Press [Enter] key to continue..."
cd ..;
rm -rf temp;
cd $DOCS/texts/xml;
if [ -f interpretations.xml ]; then
	rm interpretations.xml;
fi
if [ -f include_publicationStmt.xml ]; then
	rm include_publicationStmt.xml;
fi
cd ../../..;

# Delete a bunch of the files to speed up testing
for i in {1..7}
do
	rm $DOCS/texts/xml/*$i*.xml
done