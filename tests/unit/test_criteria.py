
def test_criteria_prefixes(criteria):
    prfx = "foaf=<http://xmlns.com/foaf/0.1/>,oslc_rm=<http://open-services.net/ns/rm#>,oslc_cm=<http://open-services.net/ns/cm#>,contact_plm=<https://contact-software.com/ontologies/v1.0/plm#>"
    criteria.prefix(prfx)

    assert criteria.prefixes
    assert "foaf" in criteria.prefixes
    assert "oslc_rm" in criteria.prefixes
    assert "oslc_cm" in criteria.prefixes
    assert "contact_plm" in criteria.prefixes

def test_criteria_where(criteria):
    prfx = "dcterms=<http://purl.org/dc/terms/>,foaf=<http://xmlns.com/foaf/0.1/>,oslc_qm=<http://open-services.net/ns/qm#>,oslc_rm=<http://open-services.net/ns/rm#>,oslc_cm=<http://open-services.net/ns/cm#>,contact_plm=<https://contact-software.com/ontologies/v1.0/plm#>"
    qry = "oslc_cm:quality_top-level.in in [\"high-top.quality\",\"medium-low.quality\"] and oslc_cm:severity in [\"high\",\"medium\"] and oslc_cm:polarity=true and oslc_cm:weight=-20.22e3 and oslc_cm:title=\"machine\" and oslc_rm:discipline{contact_plm:text=\"General\"} and dcterms:creator{foaf:firstName=\"Esser, Rebekka\"} and oslc_qm:testcase=<http://example.com/tests/31459> and oslc_qm:name=\"cat\"@en-us and oslc_qm:age=\"42\"^^xsd:integer"

    criteria.prefix(prfx)
    criteria.where(qry)

    assert criteria.prefixes
    assert criteria.conditions

    conditions = {p.prop: p.props if p.scoped else p.values for p in criteria.conditions}
    
    assert "http://open-services.net/ns/cm#quality_top-level.in" in conditions
    assert "http://open-services.net/ns/rm#discipline" in conditions
    assert "http://purl.org/dc/terms/creator" in conditions
