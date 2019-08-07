## Introduction

The code in this repository is intended for use in the [Inscriptions of Israel / Palestine project](http://library.brown.edu/cds/projects/iip/search/). It uses Python and LXML to generate word lists from [epidoc](http://www.stoa.org/epidoc/gl/latest/) files and includes a simple web interface.

## Workflow

The project is designed to separate parts of the process into atomic units,
each of which saves its results into a set of data files
  (one data file per text).
The purpose of this is to ensure that the entire process can be maintained efficiently
  by making it easy to modify distinct components,
  and to make changes on isolated steps without repeatedly processing the entire dataset from scratch.
Each step adds columns to a data table (stored in csv format for each step).
The data table gradually grows to include additional information,
  before being processed holistically to produce the final word list.

The broadly-defined steps are as follows:

1. **XML Parser** – Extract words from text (in sequence) from XML inscriptions
2. **Part-of-Speech Tagger** – Tag parts of speech
3. **Lemmatizer** – Lemmatize results of previous step.
3. **Word List Compiler** – Generate word list on lemmatized word table

## Setup

0. Clone or download the repository.
1. Enter the project directory with `cd iip-word-lists`
2.


### To run the site locally

0. Enter the docs directory with `cd docs`
1. Start an http server by running: `python -m SimpleHTTPServer 8000` or in Python3: `python3 -m http.server 8000`
2. Open `localhost:8000` in your web browser

(You can view the files without running the server, but some links will
not work.)

### To build the site

0. from the root project directory, run `./build_site.sh`. Add `-nu` if
   you are updating the site and do not wish to download the xml files.

## Project structure

## Functionality

### Lemmatization

A word's *lemma* is its "basic" form as it might appear in a dictionary. For instance, the lemma of "rethinking" is "think." The process of getting a lemma from a word is called "lemmatization." Lemmatization allows this project to recognize different strings as instances of the same word, which is very useful for learning about the usage and distributions of specific words.

Lemmatization is currently done only for Latin and Greek, as provided by [CLTK](http://cltk.org).

## Libraries

This project uses several libraries and toolkits.

* [NLTK](http://www.nltk.org/) (Natural Language Toolkit) is a tool for working with natural language data. It is very approachable and well-documented, including a gratis [ebook](http://www.nltk.org/book/). This project uses NLTK for part-of-speech identification in translated English text.
* The [Classical Language Toolkit](http://cltk.org/) (CLTK) provides natural language processing (NLP) support for a number of ancient Eurasian languages. It is used in this project for lemmatization, stemming, and part-of-speech identification in Latin and Greek texts. The implementations of these functions are explained in the project's documentation for [each](http://docs.cltk.org/en/latest/latin.html#) [language](http://docs.cltk.org/en/latest/greek.html).
* [LXML](https://lxml.de/) is a library for fast XML parsing.

## Problems Encountered

* Line breaks following certain tags indicate the start of a new word.
  These are currently listed in the global variable `include_trailing_linebreak`.
  However, this is not comprehensive. A complete list based on the epidoc
  spec should be added.
* How should gaps be handled?
* Graffiti: some transcriptions, such as masa09390.xml, are of graffiti
  and do not contain complete words but just jumbles of characters.
  Currently these are added to the word list as if they were words,
  leading to some strange results. However, if we ignored all files
  marked as containing graffiti, we could potentially lose some words.
* Should `<num>` elements always indicate the start of a new word?
