
DIGIT = "0-9"
LETTER = "A-Za-z"
ALPHANUMERIC = LETTER + DIGIT
DECIMAL = "[+-]?[" + DIGIT + "]+(\\.[" + DIGIT + "]+)?([eE][+-]?[" + DIGIT + "]+)?"
STRING_ESC = "\".*?\""
LANGTAG = "@[" + LETTER + "](-?[" + ALPHANUMERIC + "])*"
PN_PREFIX = "[" + LETTER + "](\\.?[" + ALPHANUMERIC + "_-])*"
PREFIXED_NAME = PN_PREFIX + ":[" + ALPHANUMERIC + "_](\\.?[" + ALPHANUMERIC + "_-])*"
IDENTIFIER = "\\*|" + PREFIXED_NAME
OPERATOR = "(([!<>]?=)|[<>])"
IRI_REF = "<(([^<>\"{}\\|`\\\\])+)>"
VALUE = "(" + IRI_REF + "|true|false|" + DECIMAL + "|" + STRING_ESC + "(" + LANGTAG + "|\\^\\^" + PREFIXED_NAME + ")?)"
COMPARISION = OPERATOR + VALUE
IN = " (in) \\[((.+?))\\]"
SCOPED_TERM = "\\{((.+))\\}"
TERM = r"(" + IDENTIFIER + ")((" + COMPARISION + ")|(" + IN + ")|(" + SCOPED_TERM + "))"
PROPERTY = "(" + IDENTIFIER + ")((" + SCOPED_TERM + ")?)"
PREFIX_DEF = "(" + PN_PREFIX + ")=" + IRI_REF
