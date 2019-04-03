def remove_namespace(tagtext):
	tokens = tagtext.split()
	modified_tagtext = ""
	for e in tokens:
		if not e.startswith("xmlns"):
			modified_tagtext += " " + e
		else:
			ns_stripped = False
			for character in e:
				if character == '>':
					ns_stripped = True
				if ns_stripped:
					modified_tagtext += character

	return modified_tagtext

def word_list_to_str_list(word_list):
	str_list = ""
	for e in word_list:
		str_list += e.text + " "
	return str_list

def whitespace_to_space(text):
	if text == None or len(text) < 1:
		return ""
	return " ".join(text.split())
