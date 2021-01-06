
specification_map = {
    # RDF and OSLC attributes
    'Specification_id': {'attribute': '_BaseResource__identifier', 'oslc_property': 'DCTERMS.identifier'},
    'Title': {'attribute': '_BaseResource__title', 'oslc_property': 'DCTERMS.title'},
    'Description': {'attribute': '_BaseResource__description', 'oslc_property': 'DCTERMS.description'},
    'Author': {'attribute': '_BaseResource__creator', 'oslc_property': 'DCTERMS.creator'},

    # RM and Custom attributes
    'Product': {'attribute': '_BaseResource__short_title', 'oslc_property': 'DCTERMS.shortTitle'},
    'Subject': {'attribute': '_BaseResource__subject', 'oslc_property': 'DCTERMS.subject'},
    'Source': {'attribute': '_Requirement__elaborated_by', 'oslc_property': 'OSLC_RM.elaboratedBy'},
    'Category': {'attribute': '_Requirement__constrained_by', 'oslc_property': 'OSLC_RM.constrainedBy'},
    'Discipline': {'attribute': '_Requirement__satisfied_by', 'oslc_property': 'OSLC_RM.satisfiedBy'},
    'Revision': {'attribute': '_Requirement__tracked_by', 'oslc_property': 'OSLC_RM.trackedBy'},
    'Target_Value': {'attribute': '_Requirement__validated_by', 'oslc_property': 'OSLC_RM.validatedBy'},
    'Degree_of_fulfillment': {'attribute': '_Requirement__affected_by', 'oslc_property': 'OSLC_RM.affectedBy'},
    'Status': {'attribute': '_Requirement__decomposed_by', 'oslc_property': 'OSLC_RM.decomposedBy'},

    # CUSTOM attributes
    'PUID': {'attribute': '_Requirement__puid', 'oslc_property': 'OSLC_RM.puid'},
    'Project': {'attribute': '_BaseResource__subject', 'oslc_property': 'DCTERMS.subject'},
}
