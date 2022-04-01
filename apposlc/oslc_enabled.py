from pyoslc_server import OSLCAPP

from apposlc.adapter import CreatorAdapter, RequirementAdapter, TestCaseAdapter


class OSLCEnabled:

    def __init__(self):
        self.app = OSLCAPP(prefix='/oslc')

        cdb_adapters = [
            {
                "identifier": "part",
                "title": "Part Adapter",
                "description": "Part Adapter for OSLC",
            },
            {
                "identifier": "cdbrqm_spec_object",
                "title": "Requirements Adapter",
                "description": "Requirements Adapter for OSLC",
            },
            {
                "identifier": "project",
                "title": "Project Adapter",
                "description": "Project Adapter for OSLC",
            },
        ]

        for adpt in cdb_adapters:
            self.app.api.add_adapter(
                adapter=RequirementAdapter(
                    identifier=adpt['identifier'],
                    title=adpt['title'],
                    description=adpt["description"],
                )
            )

        requirement_adapter = RequirementAdapter(
            identifier='adapter',
            title='Requirement Adapter',
            description='Requirement Adapter for OSLC',
        )

        self.app.api.add_adapter(
            adapter=requirement_adapter
        )

        self.app.api.add_adapter(
            TestCaseAdapter(
                identifier='tests',
                title='test case',
                description='test case'),
        )

        self.app.api.add_adapter(CreatorAdapter(
            identifier='creator',
            title='Creator Service',
            description='Service Provider for Creators'
        ))

    def __call__(self, environ, start_response):
        """
        Callable function required
        """

        if self.app.wsgi_check(environ):
            return self.app(environ, start_response)

        start_response("200 OK", [('Content-type', 'text/plain')])
        return [b'Hello World, This could be a CE Application !']
