"""
Read XML with segmented inscriptions and insert word ids.

TODO: Use click.
TODO: Configure logging in .ini
TODO: More consistent/correct type hinting.
"""
import configparser
import logging
from pathlib import Path

from lxml import etree

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("iip_toolkit")
log.setLevel(logging.INFO)

config = configparser.ConfigParser()
config.read("iip_toolkit.ini")

INPATH = Path(config["word_indexer"]["infile_path"])
OUTPATH = Path(config["word_indexer"]["outfile_path"])


def index_file(filename: str = None) -> Path:
    """
    Adds @ids to all "words" in the inscription. Takes and returns a file path.
    """
    log.info("Adding ids to file %s", filename)

    fileid = Path(filename).stem
    log.debug("File ID: %s", fileid)

    infile = INPATH / filename
    outfile = OUTPATH / filename
    log.debug("Reading from %s; writing to %s.", infile, outfile)
    # Open and xmlify filename
    epidoc = etree.parse(infile.open("r", encoding="utf8"))

    # find <div type="edition" subtype="transcription_segmented">
    words = epidoc.xpath(
        '//tei:div[@type="edition" and @subtype="transcription_segmented"]/tei:p/*',
        namespaces={"tei": "http://www.tei-c.org/ns/1.0"},
    )

    log.debug("Adding indexes to %d words.", len(words))

    # Add an @id to each child
    for i, word in enumerate(words, start=1):
        word.set("{http://www.w3.org/XML/1998/namespace}id", f"{fileid}-{i}")

    # Save the file
    log.debug("Saving to %s.", outfile)
    with outfile.open("w", encoding="utf8") as outf:
        outf.write(etree.tostring(epidoc, encoding="utf8", pretty_print=True).decode())

    return outfile


def index_files() -> bool:
    """
    Process every file in INPATH.
    """
    for infile in INPATH.glob("*.xml"):
        try:
            log.debug("Calling index_file for %s", infile)
            index_file(infile.name)
        except etree.XMLSyntaxError as exc:
            log.warning("Error reading file %s as XML: %s", infile, exc)


if __name__ == "__main__":
    log.info("Indexing all files in %s", (INPATH,))
    index_files()
