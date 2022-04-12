
DIGIT = "0-9"
LETTER = "A-Za-z"
ALPHANUMERIC = LETTER + DIGIT
DECIMAL = r"[+-]?[" + DIGIT + "]+(\\.[" + DIGIT + "]+)?([eE][+-]?[" + DIGIT + "]+)?"
STRING_ESC = r"\".*?\""
LANGTAG = r"@[" + LETTER + "](-?[" + ALPHANUMERIC + "])*"
PN_PREFIX = r"[" + LETTER + "](\\.?[" + ALPHANUMERIC + "_-])*"
PREFIXED_NAME = PN_PREFIX + r":[" + ALPHANUMERIC + "_](\\.?[" + ALPHANUMERIC + "_-])*"
IDENTIFIER = r"\*|" + PREFIXED_NAME
OPERATOR = r"(([!<>]?=)|[<>])"
IRI_REF = r"<(([^<>\"{}\|`\\])+)>"
VALUE = r"(" + IRI_REF + "|true|false|" + DECIMAL + "|" + STRING_ESC + "(" + LANGTAG + "|\\^\\^" + PREFIXED_NAME + ")?)"
COMPARISION = OPERATOR + VALUE
IN = r" (in) \[((.+?))\]"
SCOPED_TERM = r"\{((.+?))\}"
TERM = r"(" + IDENTIFIER + ")((" + COMPARISION + ")|(" + IN + ")|(" + SCOPED_TERM + "))"
PROPERTY = r"(" + IDENTIFIER + ")((" + SCOPED_TERM + ")?)"
PREFIX_DEF = r"(" + PN_PREFIX + ")=" + IRI_REF
