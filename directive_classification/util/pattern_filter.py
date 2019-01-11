#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# for Method Call Directive
def filterMethodCallDirective(str):

    # Not Null Directive
    searchObj = re.search('(@exception|@throws).*(be|is|are)+\s*(equal|equivalent to)*\s*null', str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NotNullDirective"

    #Null Allowed Directive
    searchObj = re.search("(@param)*.+(can|could|may)\s*(be|is|are)\s*(equivalent|equal to)*\s*null", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NullAllowedDirective"

    searchObj = re.search("null (be|is|are)* ignored", str,re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NullAllowedDirective"

    searchObj = re.search("or null|null means|this parameter is null|null returns|null otherwise|null indicates|If null|Specify null to", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NullAllowedDirective"

    searchObj = re.search("null (results|use|be passed in)", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NullAllowedDirective"


    #Not Null Directive
    # antipattern:
    # null should not be inserted into a Queue.
    # null means that the catalog name should not be used to narrow the search.
    # passing a null argument to a constructor or method in this class will cause a {@link NullPointerException} to be thrown.

    searchObj = re.search("non-null", str, re.M | re.S|re.I)
    if searchObj:
        print searchObj.group()
        return "NotNullDirective"

    searchObj = re.search("(never|not)\s*(be)*\s*null", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NotNullDirective"

    searchObj = re.search("(neither|none of).*(be|is|are)+\s*(equal|equivalent to)*\s*null", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NotNullDirective"




    # Number Range Directive
    searchObj = re.search("(>|<|=|<=|>=|<>) (\d+|([A-Z]+\w*)+|[a-z]+([A-Z]+\w*)+)", str, re.M | re.S )
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("equals \d+", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(be|is|are).* (less|greater|larger|equal|equivalent|below).* (than|to).* (\d+|number|([A-Z]+\w*)+|[a-z]+([A-Z]+\w*)+)", str, re.M | re.S )
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(be|is|are).* (less|greater|larger|below)", str,
                          re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(be|is|are).* (at least|at most).*\d+", str,
                          re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"


    searchObj = re.search("(be|is|are).* between \d+ and \d+", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("range.* between .* and .*", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(range|between).*(\d+\s*(and|to|-|~|,)\s*\d+)", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"


    searchObj = re.search("(be|is|are) .*(negative|positive|false|true|non-zero)", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("and.*(be|is|are).* the same", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(be|is|are).* (in|out of|outside).* range", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(be|is|are).* (in|out) of bounds", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(be|is|are).* \d+", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("one of.* (constant|value).*(such as|:).*([A-Z]+\w*)+(.+([A-Z]+\w*)+)+", str, re.M | re.S )
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(either of|one of).* ([A-Z]+\w*)+(\s*,\s*([A-Z]+\w*)+)+", str,
                          re.M | re.S )
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"


    searchObj = re.search("(be|is|are).* {(\d+,*)+}", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(value.* (be|is|are)|one of).* {.*}(\s*,\s*{.*})+", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"

    searchObj = re.search("(be|is|are) .*(negative|positive|non-negative|non-positive)", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "NumberRangeDirective"



    #Method Parameter Type Directive
    searchObj = re.search("(be|is|are) of.+type", str, re.M | re.S )
    if searchObj:
        print searchObj.group()
        return "MethodParameterTypeDirective"

    searchObj = re.search(
        "subclass of.* (([A-Z]+\w*)+|(int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))",
        str, re.M | re.S)
    if searchObj:
        print searchObj.group()
        return "MethodParameterTypeDirective"

    searchObj = re.search("(@throws|@exception|parameter|property|value|@param|key|element).*(must|should)* (be|is|are|implement).* (([A-Z]+\w*)+|(int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))", str, re.M | re.S)
    if searchObj:
        print searchObj.group()
        return "MethodParameterTypeDirective"

    searchObj = re.search("(be|is|are).*(equivalent|equal to|a class derived from|an instance of).* (([A-Z]+\w*)+|(int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))", str, re.M | re.S)
    if searchObj:
        print searchObj.group()
        return "MethodParameterTypeDirective"


    #Return Value Directive
    searchObj = re.match("return|result", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "ReturnValueDirective"

    searchObj = re.search("Return|Result", str, re.M | re.S )
    if searchObj:
        print searchObj.group()
        return "ReturnValueDirective"


    searchObj = re.search("@return", str, re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "ReturnValueDirective"

    searchObj = re.search("(return|returns|returned|returning)\s+(a|the|this)?\s*(([A-Z]+\w*)+|executor|collection|map|.* data|set)", str, re.M | re.S )
    if searchObj:
        print searchObj.group()
        return "ReturnValueDirective111"

    searchObj = re.search("(value|parameter|object)s?\s+(is|be|are)?\s*(return|returns|returned|returning)", str,
                          re.M | re.S | re.I)
    if searchObj:
        print searchObj.group()
        return "ReturnValueDirective"

    searchObj = re.search("(method|\w+\(.*\))\s+(must|should|can|could|may)?\s*(return|returns|returned|returning)\s+(a|the|this)?.*(([A-Z]+\w*)+|true|false|element|object)", str,
                          re.M | re.S )
    if searchObj:
        print searchObj.group()
        return "ReturnValueDirective"

    return ""



print filterMethodCallDirective(
    """the Type objects returned for it must accurately reflect the actual type parameters us"""
    )
# for Subclassing Directive
def filterSubclassingDirective(str):
    pass


# for Miscellaneous Directive
def filterMiscellaneousDirective(str):
    pass