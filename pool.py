import os
from xbrl import resolver, instance, taxonomy, schema, tpack


class Pool:
    def __init__(self, cache_folder=None):
        self.cache_folder = cache_folder
        if cache_folder:
            self.resolver = resolver.Resolver(cache_folder)
        self.taxonomies = {}
        self.discovered = {}
        self.schemas = {}
        self.linkbases = {}
        self.instances = {}
        self.packaged_entrypoints = {}  # Index of all packages in the cache/taxonomy_packages folder by entrypoint
        self.packaged_locations = None
        self.active_packages = {}  # Currently opened taxonomy packages

    def index_packages(self):
        """ Index the content of taxonomy packages found in cache/taxonomies/ """
        package_files = [os.path.join(r, file) for r, d, f in
                         os.walk(self.cache_folder) for file in f if file.endswith('.zip')]
        for pf in package_files:
            pck = tpack.TaxonomyPackage(pf)
            for ep in pck.entrypoints:
                self.packaged_entrypoints[ep[1]] = pf

    def add_instance(self, location, key=None, attach_taxonomy=False):
        xid = instance.Instance(location=location, container_pool=self)
        if key is None:
            key = location
        self.instances[key] = xid
        if attach_taxonomy and xid.xbrl is not None:
            # Ensure that if schema references are relative, the location base for XBRL document is added to them
            entry_points = [e if e.startswith('http') else os.path.join(xid.base, e).replace('\\', '/')
                            for e in xid.xbrl.schema_refs]
            tax = self.add_taxonomy(entry_points)
            xid.taxonomy = tax

    def add_schema(self, location, container_taxonomy):
        sh = schema.Schema(location, self, container_taxonomy)
        self.schemas[location] = sh
        if container_taxonomy is None:
            return
        container_taxonomy.schemas[location] = sh

    def add_taxonomy(self, entry_points):
        self.packaged_locations = {}
        for ep in entry_points:
            pf = self.packaged_entrypoints.get(ep)
            if not pf:
                continue
            pck = tpack.TaxonomyPackage(pf)
            pck.compile()
            for pf in pck.files.items():
                self.packaged_locations[pf[0]] = (pck, pf[1])  # A tuple
        tax = taxonomy.Taxonomy(entry_points, self)
        key = ','.join(entry_points)
        self.taxonomies[key] = tax
        self.packaged_locations = None
        return tax

    def info(self):
        return '\n'.join([
            f'Taxonomies: {len(self.taxonomies)}',
            f'Instance documents: {len(self.instances)}',
            f'Taxonomy schemas: {len(self.schemas)}',
            f'Taxonomy linkbases: {len(self.linkbases)}'])

