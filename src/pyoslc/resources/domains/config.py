from pyoslc.resources.models import BaseResource


class ConfigurationResource(BaseResource):
    def __init__(
        self,
        about=None,
        types=None,
        properties=None,
        description=None,
        identifier=None,
        short_title=None,
        title=None,
        contributor=None,
        creator=None,
        subject=None,
        created=None,
        modified=None,
        type=None,
        discussed_by=None,
        instance_shape=None,
        service_provider=None,
        relation=None,
        short_id=None,
        modified_by=None,
        was_derived_from=None,
        was_revision_of=None,
        was_generated_by=None,
    ):

        super(ConfigurationResource, self).__init__(
            about,
            types,
            properties,
            description,
            identifier,
            short_title,
            title,
            contributor,
            creator,
            subject,
            created,
            modified,
            type,
            discussed_by,
            instance_shape,
            service_provider,
            relation,
        )

        self.__short_id = short_id if short_id is not None else ""
        self.__modified_by = modified_by if modified_by is not None else ""
        self.__was_derived_from = (
            was_derived_from if was_derived_from is not None else ""
        )
        self.__was_revision_of = was_revision_of if was_revision_of is not None else ""
        self.__was_generated_by = (
            was_generated_by if was_generated_by is not None else ""
        )

    @property
    def short_id(self):
        return self.__short_id

    @short_id.setter
    def short_id(self, short_id):
        self.__short_id = short_id

    @property
    def modified_by(self):
        return self.__modified_by

    @modified_by.setter
    def modified_by(self, modified_by):
        self.__modified_by = modified_by

    @property
    def was_derived_from(self):
        return self.__was_derived_from

    @was_derived_from.setter
    def was_derived_from(self, was_derived_from):
        self.__was_derived_from = was_derived_from

    @property
    def was_revision_of(self):
        return self.__was_revision_of

    @was_revision_of.setter
    def was_revision_of(self, was_revision_of):
        self.__was_revision_of = was_revision_of

    @property
    def was_generated_by(self):
        return self.__was_generated_by

    @was_generated_by.setter
    def was_generated_by(self, was_generated_by):
        self.__was_generated_by = was_generated_by

    def to_rdf(self, graph):
        super(BaseResource, self).to_rdf(graph)


class ConfigurationItem(ConfigurationResource):
    def __init__(
        self,
        about=None,
        types=None,
        properties=None,
        description=None,
        identifier=None,
        short_title=None,
        title=None,
        contributor=None,
        creator=None,
        subject=None,
        created=None,
        modified=None,
        type=None,
        discussed_by=None,
        instance_shape=None,
        service_provider=None,
        relation=None,
        short_id=None,
        modified_by=None,
        was_derived_from=None,
        was_revision_of=None,
        was_generated_by=None,
        is_version_of=None,
        version_id=None,
    ):

        super(ConfigurationItem, self).__init__(
            about,
            types,
            properties,
            description,
            identifier,
            short_title,
            title,
            contributor,
            creator,
            subject,
            created,
            modified,
            type,
            discussed_by,
            instance_shape,
            service_provider,
            relation,
            short_id,
            modified_by,
            was_derived_from,
            was_revision_of,
            was_generated_by,
        )

        self.__is_version_of = is_version_of if is_version_of is not None else ""
        self.__version_id = version_id if version_id is not None else ""

    @property
    def is_version_of(self):
        return self.__is_version_of

    @is_version_of.setter
    def is_version_of(self, is_version_of):
        self.__is_version_of = is_version_of

    @property
    def version_id(self):
        return self.__version_id

    @version_id.setter
    def version_id(self, version_id):
        self.__version_id = version_id

    def to_rdf(self, graph):
        super(BaseResource, self).to_rdf(graph)


class Configuration(ConfigurationResource):
    def __init__(
        self,
        about=None,
        types=None,
        properties=None,
        description=None,
        identifier=None,
        short_title=None,
        title=None,
        contributor=None,
        creator=None,
        subject=None,
        created=None,
        modified=None,
        type=None,
        discussed_by=None,
        instance_shape=None,
        service_provider=None,
        relation=None,
        short_id=None,
        modified_by=None,
        was_derived_from=None,
        was_revision_of=None,
        was_generated_by=None,
        member=None,
        contains_relation=None,
        contained_by_relation=None,
        component=None,
        mutable=None,
        action=None,
    ):

        super(Configuration, self).__init__(
            about,
            types,
            properties,
            description,
            identifier,
            short_title,
            title,
            contributor,
            creator,
            subject,
            created,
            modified,
            type,
            discussed_by,
            instance_shape,
            service_provider,
            relation,
            short_id,
            modified_by,
            was_derived_from,
            was_revision_of,
            was_generated_by,
        )

        self.__member = member if member is not None else set()
        self.__contains_relation = (
            contains_relation if contains_relation is not None else set()
        )
        self.__contained_by_relation = (
            contained_by_relation if contained_by_relation is not None else set()
        )
        self.__component = component if component is not None else set()
        self.__mutable = mutable if mutable is not None else ""
        self.__action = action if action is not None else set()

    @property
    def member(self):
        return self.__member

    @member.setter
    def member(self, member):
        self.__member = member

    def add_member(self, member):
        if member:
            self.__member.append(member)

    @property
    def contains_relation(self):
        return self.__contains_relation

    @contains_relation.setter
    def contains_relation(self, contains_relation):
        self.__contains_relation = contains_relation

    def add_contains_relation(self, contains_relation):
        if contains_relation:
            self.__contains_relation.append(contains_relation)

    @property
    def contained_by_relation(self):
        return self.__contained_by_relation

    @contained_by_relation.setter
    def contained_by_relation(self, contained_by_relation):
        self.__contained_by_relation = contained_by_relation

    def add_contained_by_relation(self, contained_by_relation):
        if contained_by_relation:
            self.__contained_by_relation.append(contained_by_relation)

    @property
    def component(self):
        return self.__component

    @component.setter
    def component(self, component):
        self.__component = component

    def add_component(self, component):
        if component:
            self.__component.append(component)

    @property
    def mutable(self):
        return self.__mutable

    @mutable.setter
    def mutable(self, mutable):
        self.__mutable = mutable

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, action):
        self.__action = action

    def add_action(self, action):
        if action:
            self.__action.append(action)


class Component(ConfigurationResource):
    def __init__(
        self,
        about=None,
        types=None,
        properties=None,
        description=None,
        identifier=None,
        short_title=None,
        title=None,
        contributor=None,
        creator=None,
        subject=None,
        created=None,
        modified=None,
        type=None,
        discussed_by=None,
        instance_shape=None,
        service_provider=None,
        relation=None,
        short_id=None,
        modified_by=None,
        was_derived_from=None,
        was_revision_of=None,
        was_generated_by=None,
        member=None,
        contains_relation=None,
        contained_by_relation=None,
        is_version_of=None,
    ):
        super(Component, self).__init__(
            about,
            types,
            properties,
            description,
            identifier,
            short_title,
            title,
            contributor,
            creator,
            subject,
            created,
            modified,
            type,
            discussed_by,
            instance_shape,
            service_provider,
            relation,
            short_id,
            modified_by,
            was_derived_from,
            was_revision_of,
            was_generated_by,
        )

        self.__member = member if member is not None else set()
        self.__contains_relation = (
            contains_relation if contains_relation is not None else set()
        )
        self.__contained_by_relation = (
            contained_by_relation if contained_by_relation is not None else set()
        )
        self.__is_version_of = is_version_of if is_version_of is not None else ""

    @property
    def member(self):
        return self.__member

    @member.setter
    def member(self, member):
        self.__member = member

    def add_member(self, member):
        if member:
            self.__member.append(member)

    @property
    def contains_relation(self):
        return self.__contains_relation

    @contains_relation.setter
    def contains_relation(self, contains_relation):
        self.__contains_relation = contains_relation

    def add_contains_relation(self, contains_relation):
        if contains_relation:
            self.__contains_relation.append(contains_relation)

    @property
    def contained_by_relation(self):
        return self.__contained_by_relation

    @contained_by_relation.setter
    def contained_by_relation(self, contained_by_relation):
        self.__contained_by_relation = contained_by_relation

    def add_contained_by_relation(self, contained_by_relation):
        if contained_by_relation:
            self.__contained_by_relation.append(contained_by_relation)

    @property
    def is_version_of(self):
        return self.__is_version_of

    @is_version_of.setter
    def is_version_of(self, is_version_of):
        self.__is_version_of = is_version_of
