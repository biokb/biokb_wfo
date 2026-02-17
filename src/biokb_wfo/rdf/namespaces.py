"""RDF namespace URIs."""

from rdflib import Namespace

from biokb_wfo.constants import BASE_URI

WFO_BASE_URI = "https://www.worldfloraonline.org/taxon/wfo-0000042097"

# WFO URIs to Fraunhofer
NODE_NS = Namespace(f"{BASE_URI}/node#")
REL_NS = Namespace(f"{BASE_URI}/relation#")
WFO_NS = Namespace("https://www.worldfloraonline.org/taxon/wfo-")
IPNI_NS = Namespace("https://www.ipni.org/n/")
