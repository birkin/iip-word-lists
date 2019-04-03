DEFAULT_OUTPUT_NAME = "wordlist"
DEBUG = True
TEI_NS = "{http://www.tei-c.org/ns/1.0}"
XML_NS = "{http://www.w3.org/XML/1998/namespace}"
IGNORE = ['⎜', '{', '}', '|', '(', '?', ')', ',', ';', '.', ':',
           '"', "'", "<", ">", "+", "[", "]", "_", "#", "*", '~',
           '´', '=', '·', '‧', '⋅', '•', '∙', '/']
WORD_TERMINATING = ["\\", "/"]
INCLUDE_TRAILING_LINEBREAK = [TEI_NS + "persName", TEI_NS + "abbr",
                              TEI_NS + "choice", TEI_NS + "supplied",
							  TEI_NS + "num", TEI_NS + "div",
							  TEI_NS + "unclear", TEI_NS + "placeName"]

NO_SPAN_WORDS = [TEI_NS + "expan", TEI_NS + "num"]

LATIN_CODES = ["la", "lat"]
GREEK_CODES = ["grc"]
codes = [
	["latin",["la", "lat"]],
	["hebrew",["heb", "he"]],
	["greek",["grc", "grk"]],
	["aramaic",["arc"]],
	["unknown", ["unk"]],
	["english", ["transl"]]
]

NUM_CONTEXT = 5

INFO_PAGE_HTML = """
<html>
	<head>
		<title></title>
		<meta charset='UTF-8' />
		<script src="https://cdn.rawgit.com/google/code-prettify/master/loader/run_prettify.js"> </script>
		<link rel="stylesheet" type="text/css" href="../wordinfo.css"/>
	</head>
	<body>
		<div id="all-wrapper">
		<div class="info-box">
		<h1></h1>
		<div id="doubletree-container">
			<a id="doubletree-link">
			Doubletree Visualization
			</a>
		</div>
		<table>
			<tr>
				<td>Stem</td><td id='stem'></td>
			</tr>
			<tr>
				<td>Occurences: </td><td id='num-occurrences'></td>
			</tr>
			<tr>
				<td>Total Frequency</td><td id='total-frequency'></td>
			</tr>
			<tr>
				<td>Language Frequency</td><td id='language-frequency'></td>
			</tr>
		</table>
		</div>
		<h2>Variations</h2>
		<ul id='variations'>
		</ul>
		<!-- <h2>Files</h2>
		<ul id='files'>
		</ul> -->
		<h2>Regions</h2>
		<ul id='regions'>
		</ul>
		<!-- <iframe id='doubletree-frame' style='width: 100%; height: 400px;'>Your browser does not support frames.</iframe> -->
		<!-- <h2>Keyword in Context</h2>
		<ul id='kwic'></ul> -->
		<div class="grey-box">
		<h2>Occurences</h2>
		<table id="occurrences">
			<tr>
				<th>Variation</th>
				<th>File</th>
				<th colspan="3">Word in Context</th>
				<!--<th>XML</th>-->
				<th>Region</th>
				<th>Part of Speech</th>
			</tr>
		</table>
		</div>
	</div>
	<script src="../wordInfo.js"> </script>
	</body>
</html>
""".replace("\t", "")

INDEX_PAGE_HTML = """
<html>
	<head>
		<meta charset='UTF-8' />
		<title></title>
		<script src="../levenshtein.min.js"> </script>
		<link rel="stylesheet" type="text/css" href="../style.css" />
	</head>
	<body>
		<div id="all-wrapper">
			<!-- <h1></h1> -->
			<ul id='words'>
				<noscript id="wordList">

				</noscript>
			</ul>
			<script>
				wordsArray = [
					$WORDS_OBJECT
				];
			</script>
			<script src='../index_search.js'>   </script>
		</div>
	</body>
</html>
""".replace("\t", "")

FRONT_PAGE_HTML = """
<html>
	<head>
		<meta charset='UTF-8' />
		<title>Language Selection</title>
	</head>
	<body>
		<h1>Languages</h1>
		<ul id='language-list-html'></ul>
	</body>
</html>
""".replace("\t", "")

OCCURENCE_TABLE_ROW_HTML = """
<span>
<tr>
	<td class="variation"></td>
	<td class="file"></td>
	<td class="kwic-prec"></td>
	<td class="kwic"></td>
	<td class="kwic-post"></td>
	<td class="region"></td>
	<td class="pos"></td>
</tr>
<tr>
	<td colspan="7" style="text-align: center;"><code class="xml prettyprint"></code></td>
</tr>
</span>
""".replace("\t", "")
