"""
Read XML with segmented inscriptions and insert word ids.

TODO: Use click.
TODO: Configure logging in .ini
TODO: More consistent/correct type hinting.
"""
import configparser
import logging
from pathlib import Path
from typing import Tuple

from lxml import etree

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("iip_toolkit")
log.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read("iip_toolkit.ini")

INPATH = Path(config["word_indexer"]["infile_path"])
OUTPATH = Path(config["word_indexer"]["outfile_path"])


def index_file(filename: str = None) -> Path:
    """
    Adds @ids to all "words" in the inscription. Takes and returns a file path.
    """
    print(log)
    log.info(f"Adding ids to file {filename}")

    fileid = Path(filename).stem
    log.debug(f"File ID: {fileid}")

    infile = INPATH / filename
    outfile = OUTPATH / filename
    log.debug(f"Reading from {infile}; writing to {outfile}.")
    # Open and xmlify filename
    epidoc = etree.parse(infile.open("r", encoding="utf8"))

    # find <div type="edition" subtype="transcription_segmented">
    words = epidoc.xpath(
        '//tei:div[@type="edition" and @subtype="transcription_segmented"]/tei:p/*',
        namespaces={"tei": "http://www.tei-c.org/ns/1.0"},
    )

    log.debug(f"Adding indexes to {len(words)} words.")

    # Add an @id to each child
    for i, word in enumerate(words, start=1):
        word.set('{http://www.w3.org/XML/1998/namespace}id', f"{fileid}-{i}")

    # Save the file
    log.debug(f"Saving to {outfile}.")
    with outfile.open("w", encoding="utf8") as outf:
        outf.write(etree.tostring(epidoc, encoding="utf8", pretty_print=True).decode())
        
    return outfile


def index_files() -> bool:
    for infile in INPATH.glob('*.xml'):
        index_file(infile.name)


if __name__ == "__main__":
    index_files()
