#!/usr/bin/env bash

update=1;
exceptions=0;
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
	if [ $exceptions == 1 ]; then
		exceptions_flag="--fileexception"
	fi
	#if [ $new_system == 1 ]; then
	#	new_system_flag="--new_system"
	#fi
	../src/python/wordlist.py texts/xml/* --nodiplomatic --html_general\
	--plaintext --flat texts/plain $exceptions_flag $new_system_flag;
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
	elif [ "$word" == "--exceptions" ] || [ "$word" == "-e" ]; then
		exceptions=1;
	elif [ "$word" == "--new-system" ] || [ "$word" == "-ns" ]; then
		new_system=1;
	fi

done

# Delete all of the old files,
# including those generated programmatically and downloaded from the repo
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

say "updating texts" # Robot voice output so I can do other things while this runs

if [ $update == 1 ]; then
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
else
	mv texts $DOCS;
fi

say "running lemmatizer" # Robot voice output so I can do other things while this runs
run_script;
say "lemmatizer complete"

cp src/web/wordlist.css $DOCS/;
cp src/web/style.css $DOCS/;
# cp src/web/index_search.js $DOCS/;
cp index_search.js $DOCS/;
cp src/web/doubletree.html $DOCS/;
cp -r src/web/doubletreejs $DOCS/;
cp src/web/levenshtein.min.js $DOCS/;
cp src/web/wordinfo.css $DOCS/;
cp src/web/wordInfo.js $DOCS/;
cp res/doubletree.svg $DOCS/;

# cat $DOCS/texts/plain/* > $DOCS/combined.txt # Rewritten below to avoid "arg list too long" error
# All this does is combine all of the texts into one text file so that the doubletree can be generated from them
# It is complicated because it has to be
find $DOCS/texts/plain -name "*.txt" -exec cat '{}' ';' > $DOCS/combined.txt
./src/python/per_line.py $DOCS/combined.txt $DOCS/doubletree-data.txt