DEFAULT_OUTPUT_NAME = "wordlist"
DEBUG = True 
TEI_NS = "{http://www.tei-c.org/ns/1.0}"
XML_NS = "{http://www.w3.org/XML/1998/namespace}"
IGNORE = ['⎜', '{', '}', '|', '-', '(', '?', ')', ',', ';', '.', ':', 
           '"', "'", "<", ">", "+", "[", "]", "∙", "_", "/", "#", "*", 
           '~', '‧', '´', '=']
INCLUDE_TRAILING_LINEBREAK = [TEI_NS + "persName", TEI_NS + "expan", 
                              TEI_NS + "choice", TEI_NS + "hi", TEI_NS +
                              "supplied", TEI_NS + "num", TEI_NS + 
                              "div", TEI_NS + "unclear", TEI_NS + "placeName"]
LATIN_CODES = ["la", "lat"]
GREEK_CODES = ["grc"]
codes = [
	["latin",["la", "lat"]],
	["hebrew",["heb", "he"]],
	["greek",["grc", "grk"]],
	["aramaic",["arc"]],
]

INFO_PAGE_HTML = """
<html>
	<head>
		<meta charset='UTF-8' />
	</head>
	<body>
		<h1></h1>
		<table>
			<tr>
				<td>Occurences: </td><td id='num-occurences'></td>
			</tr>
		</table>
		<h2>Variations</h2>
		<ul id='variations'>
		</ul>
		<h2>Files</h2>
		<ul id='files'>
		</ul>
		<h2>Xml</h2>
		<ul id='xml-occurences'></ul>
		<h2>Regions</h2>
		<ul id='regions'>
		</ul>
	</body>
</html>
""".replace("\t", "")

INDEX_PAGE_HTML = """
<html>
	<head>
		<meta charset='UTF-8' />
		<title></title>
		<link rel="stylesheet" type="text/css" href="../style.css" />
	</head>
	<body>
		<h1></h1>
		<ul id='words'></ul>
		<script src='../index_search.js'>   </script>
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