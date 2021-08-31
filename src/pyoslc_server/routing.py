from werkzeug.routing import Rule


class OSLCRule(Rule):

    def __init__(self, string, oslc_methods=None, *args, **kwargs):
        super(OSLCRule, self).__init__(string, *args, **kwargs)
        self.oslc_methods = oslc_methods
