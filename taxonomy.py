from xbrl import schema
from xbrl import const

class Taxonomy:
    """ entry_points is a list of entry point locations
        cache_folder is the place where to store cached Web resources """
    def __init__(self, entry_points, container_pool):
        self.entry_points = entry_points
        self.pool = container_pool
        self.schemas = {}
        self.linkbases = {}
        self.concepts = {}
        self.concepts_by_qname = {}
        self.base_sets = {}
        self.defaults = {}
        self.load()
        self.compile()

    def load(self):
        for ep in self.entry_points:
            sh = schema.Schema(ep, self.pool, self)

    def compile(self):
        for lb in self.linkbases.items():
            for xl in lb[1].links:
                xl.compile()
        for bs in self.base_sets.items():
            if bs[1].arc_name != 'definitionArc':
                continue
            if bs[1].arcrole == const.XDT_DIMENSION_DEFAULT_ARCROLE:
                pass
