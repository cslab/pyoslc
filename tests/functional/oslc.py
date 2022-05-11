class PyOSLC:
    def __init__(self, client):
        self._client = client
        self.headers = {
            "Accept": "application/rdf+xml",
            "Content-Type": "application/rdf+xml",
        }

    def get_swagger(self, path="/"):
        return self._client.get(path)

    def get_url(self, url):
        return self._client.get(url)

    def get_catalog(self, rdf_presentation=None):

        if rdf_presentation:
            self.headers = {
                "accept": rdf_presentation,
                "content-type": rdf_presentation,
            }

        return self._client.get("/oslc/services/catalog", headers=self.headers)

    def get_service_provider(self, service_provider):
        return self._client.get(
            "/oslc/services/provider/{}".format(service_provider), headers=self.headers
        )

    def get_query_capability(
        self,
        service_provider,
        paging=False,
        page_size=None,
        page_number=None,
        prefixes=None,
        where=None,
        select=None,
    ):
        query = "/oslc/services/provider/{}/resources".format(service_provider)
        if paging:
            query += "?oslc.paging=True"
        if page_size:
            query += "&oslc.pageSize={size}".format(size=page_size)
        if page_number:
            query += "&oslc.pageNo={number}".format(number=page_number)

        query += "?" if not query.__contains__("?") else "&"

        if select:
            query += "oslc.select={attr}".format(attr=select)

        if prefixes:
            query += "&oslc.prefix={prfx}".format(prfx=prefixes)

        return self._client.get(query, headers=self.headers)

    def post_creation_factory(self, service_provider, payload):
        return self._client.post(
            "/oslc/services/provider/{}/resources".format(service_provider),
            data=payload,
            headers=self.headers,
        )

    def get_query_resource(self, service_provider, resource):
        return self._client.get(
            "/oslc/services/provider/{}/resources/requirement/{}".format(
                service_provider, resource
            ),
            headers=self.headers,
        )

    def put_query_capability(self, service_provider, resource, payload, etag):
        headers = {"If-Match": etag}
        self.headers.update(headers)
        return self._client.put(
            "/oslc/services/provider/{}/resources/requirement/{}".format(
                service_provider, resource
            ),
            data=payload,
            headers=self.headers,
        )

    def delete_query_capability(self, service_provider, resource):
        return self._client.delete(
            "/oslc/services/provider/{}/resources/requirement/{}".format(
                service_provider, resource
            ),
            headers=self.headers,
        )

    def create(self, project_id):
        payload = """
            <rdf:RDF
                xmlns:oslc="http://open-services.net/ns/core#"
                xmlns:oslc_rm="http://open-services.net/ns/rm#"
                xmlns:dcterms="http://purl.org/dc/terms/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">

                <oslc_rm:Requirement
                    rdf:about="http://localhost/oslc/services/provider/{project_id}/resources/X1C2V3B6">
                    <oslc_rm:satisfiedBy>Software Development</oslc_rm:satisfiedBy>
                    <dcterms:description>The OSLC RM Specification needs to be awesome 3</dcterms:description>
                    <oslc_rm:constrainedBy>Customer Requirement</oslc_rm:constrainedBy>
                    <oslc_rm:trackedBy>0</oslc_rm:trackedBy>
                    <oslc_rm:validatedBy>1</oslc_rm:validatedBy>
                    <dcterms:title>The SAFER FTA should not limit EVA crewmember mobility</dcterms:title>
                    <oslc_rm:affectedBy>0</oslc_rm:affectedBy>
                    <oslc:shortTitle>SDK-Dev</oslc:shortTitle>
                    <dcterms:creator>Mario</dcterms:creator>
                    <dcterms:subject>Project-1</dcterms:subject>
                    <oslc_rm:elaboratedBy>Ian Altman</oslc_rm:elaboratedBy>
                    <dcterms:identifier>X1C2V3B6</dcterms:identifier>
                    <oslc_rm:decomposedBy>Draft</oslc_rm:decomposedBy>
                </oslc_rm:Requirement>
            </rdf:RDF>
            """.format(
            project_id=project_id
        )

        return self.post_creation_factory(project_id, payload)

    def update(self, project_id, etag):
        payload = """
            <rdf:RDF
                xmlns:oslc="http://open-services.net/ns/core#"
                xmlns:oslc_rm="http://open-services.net/ns/rm#"
                xmlns:dcterms="http://purl.org/dc/terms/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <oslc_rm:Requirement
                    rdf:about="http://localhost/oslc/services/provider/Project-1/resources/requirement/X1C2V3B6">
                    <oslc_rm:satisfiedBy>[[UPDATED]] - Software Development</oslc_rm:satisfiedBy>
                    <dcterms:description>[[UPDATED]] - The OSLC RM Specification needs to be awesome 3</dcterms:description>
                    <oslc_rm:constrainedBy>[[UPDATED]] - Customer Requirement</oslc_rm:constrainedBy>
                    <oslc_rm:trackedBy>0</oslc_rm:trackedBy>
                    <oslc_rm:validatedBy>1</oslc_rm:validatedBy>
                    <dcterms:title>[[UPDATED]] - The SAFER FTA should not limit EVA crewmember mobility</dcterms:title>
                    <oslc_rm:affectedBy>0</oslc_rm:affectedBy>
                    <oslc:shortTitle>[[UPDATED]] - SDK-Dev</oslc:shortTitle>
                    <dcterms:creator>Mario</dcterms:creator>
                    <dcterms:subject>Project-1</dcterms:subject>
                    <oslc_rm:elaboratedBy>Ian Altman</oslc_rm:elaboratedBy>
                    <dcterms:identifier>X1C2V3B6</dcterms:identifier>
                    <oslc_rm:decomposedBy>Draft</oslc_rm:decomposedBy>
                </oslc_rm:Requirement>
            </rdf:RDF>
            """

        return self.put_query_capability(project_id, "X1C2V3B6", payload, etag)

    def delete(self, project_id, resource_id):
        return self.delete_query_capability(project_id, resource_id)

    def list(self):
        """
        Method for listing the requirements/specifications
        taken from the synthetic data
        """

        headers = {
            "Content-Type": "application/json-ld",
            "Accept": "application/json-ld",
        }

        return self._client.get("oslc/rm/requirement", headers=headers)

    def item(self, requirement_id):
        """
        Method for retrieving the information
        for a specific requirement/specification
        based on the id sent as parameter
        """

        headers = {
            "Content-Type": "application/json-ld",
            "Accept": "application/json-ld",
        }

        return self._client.get(
            "oslc/rm/requirement/" + requirement_id, headers=headers
        )

    def get_rootservices(self, rdf_presentation=None):

        if rdf_presentation:
            self.headers = {
                "accept": rdf_presentation,
                "content-type": rdf_presentation,
            }

        return self._client.get("/oslc/services/rootservices", headers=self.headers)

    def get_publisher(self):
        return self._client.get("/oslc/services/config/publisher", headers=self.headers)

    def post_consumer_register(self, payload):
        return self._client.post(
            "/register", json=payload, headers={"content-type": "application/json"}
        )

    def create_consumer(self):
        payload = {
            "name": "pyoslc/rm",
            "secret": "s3cret_",
            "secretType": "string",
            "trusted": True,
            "userId": None,
        }

        return self.post_consumer_register(payload)

    def get_configuration_catalog(self):
        return self._client.get("/oslc/services/config", headers=self.headers)

    def get_configuration_components(self):
        return self._client.get(
            "/oslc/services/config/components", headers=self.headers
        )

    def get_configuration_selection(self):
        return self._client.get("/oslc/services/config/selection", headers=self.headers)

    def get_configuration_streams(self):
        return self._client.get("/oslc/services/config/selection?stream=baselines")

    def get_stream(self, stream_id):
        return self._client.get("/oslc/services/config/stream/{}".format(stream_id))

    def get(self, url):
        return self._client.get(url)
