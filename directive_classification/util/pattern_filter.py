#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# for Method Call Directive
def filterMethodCallDirective(str):


    #Null Allowed Directive
    searchObj = re.search("(@param)*.+(can|could|may)\s*(be|is|are)\s*(equivalent|equal to)*\s*null", str, re.M | re.S | re.I)
    if searchObj:
        ##print searchObj.group()
        return "NullAllowedDirective"

    searchObj = re.search("null (be|is|are)* ignored", str,re.M | re.S | re.I)
    if searchObj:
        ##print searchObj.group()
        return "NullAllowedDirective"

    searchObj = re.search("or null|null means|this parameter is null|null returns|null otherwise|null indicates|If null|Specify null to", str, re.M | re.S | re.I)
    if searchObj:
        ##print searchObj.group()
        return "NullAllowedDirective"

    searchObj = re.search("null (results|use|be passed in)", str, re.M | re.S | re.I)
    if searchObj:
        ##print searchObj.group()
        return "NullAllowedDirective"

    #
    #
    # #Not Null Directive
    # # antipattern:
    # # null should not be inserted into a Queue.
    # # null means that the catalog name should not be used to narrow the search.
    # # passing a null argument to a constructor or method in this class will cause a {@link NullPointerException} to be thrown.
    #
    # searchObj = re.search('(@exception|@throws).*(be|is|are)+\s*(equal|equivalent to)*\s*null', str, re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "NotNullDirective"
    #
    # searchObj = re.search("non-null", str, re.M | re.S|re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NotNullDirective"
    #
    # searchObj = re.search("(never|not)\s*(be)*\s*null", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NotNullDirective"
    #
    # searchObj = re.search("(neither|none of).*(be|is|are)+\s*(equal|equivalent to)*\s*null", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NotNullDirective"
    #
    #
    #
    #
    # # Number Range Directive
    # searchObj = re.search("(>|<|=|<=|>=|<>) (\d+|([A-Z]+\w*)+|[a-z]+([A-Z]+\w*)+)", str, re.M | re.S )
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    # searchObj = re.search("equals \d+", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    # # searchObj = re.search("(be|is|are).* (less|greater|larger|equal|equivalent|below).* (than|to).* (\d+|number)", str, re.M | re.S )#|([A-Z]+\w*)+|[a-z]+([A-Z]+\w*)+
    # # if searchObj:
    # #     ##print searchObj.group()
    # #     return "NumberRangeDirective"
    #
    # # searchObj = re.search("(be|is|are).* (less|greater|larger|below)", str,
    # #                       re.M | re.S | re.I)
    # # if searchObj:
    # #     ##print searchObj.group()
    # #     return "NumberRangeDirective"
    #
    # # searchObj = re.search("(be|is|are).* (at least|at most).*\d+", str,
    # #                       re.M | re.S | re.I)
    # # if searchObj:
    # #     ##print searchObj.group()
    # #     return "NumberRangeDirective"
    #
    #
    # searchObj = re.search("(be|is|are).* between \d+ and \d+", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    # searchObj = re.search("range.* between .* and .*", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    # searchObj = re.search("(range|between).*(\d+\s*(and|to|-|~|,)\s*\d+)", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    #
    # # searchObj = re.search("(be|is|are) .*(negative|positive|false|true|non-zero)", str, re.M | re.S | re.I)
    # # if searchObj:
    # #     ##print searchObj.group()
    # #     return "NumberRangeDirective"
    #
    # # searchObj = re.search("and.*(be|is|are).* the same", str, re.M | re.S | re.I)
    # # if searchObj:
    # #     ##print searchObj.group()
    # #     return "NumberRangeDirective"
    #
    # searchObj = re.search("(be|is|are).* (in|out of|outside).* range", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    # searchObj = re.search("(be|is|are).* (in|out) of bounds", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    # # searchObj = re.search("(be|is|are).* \d+", str, re.M | re.S | re.I)
    # # if searchObj:
    # #     ##print searchObj.group()
    # #     return "NumberRangeDirective"
    #
    # searchObj = re.search("one of.* (constant|value).*(such as|:).*([A-Z]+\w*)+(.+([A-Z]+\w*)+)+", str, re.M | re.S )
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    # searchObj = re.search("(either of|one of).* ([A-Z]+\w*)+(\s*,\s*([A-Z]+\w*)+)+", str,
    #                       re.M | re.S )
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    #
    # searchObj = re.search("(be|is|are).* {(\d+,*)+}", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    # searchObj = re.search("(value.* (be|is|are)|one of).* {.*}(\s*,\s*{.*})+", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"

    # searchObj = re.search("(be|is|are) .*(negative|positive|non-negative|non-positive)", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "NumberRangeDirective"
    #
    #
    #
    # #Method Parameter Type Directive
    # searchObj = re.search("((([A-Z]+\w+)[A-Z]+\w*)|parameter).*(be|is|are) .*of.+type", str, re.M | re.S )
    # if searchObj:
    #     ##print searchObj.group()
    #     return "MethodParameterTypeDirective"
    #
    # searchObj = re.search("(argument|element|key)s? .*must (be|(come from)) .*type", str, re.M | re.S)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "MethodParameterTypeDirective"
    #
    # searchObj = re.search("(key|value|element|property)s?.*(must|should) implement .*[A-Z]+\w*", str, re.M | re.S)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "MethodParameterTypeDirective"
    #
    # searchObj = re.search(
    #     "subclass of.* (([A-Z]+\w*)+|(int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))",
    #     str, re.M | re.S)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "MethodParameterTypeDirective"
    #
    # searchObj = re.search("(@throws|@exception|parameter|property|value|@param|key|element).*(must|should)* (be|is|are|implement).* ((int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))", str, re.M | re.S)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "MethodParameterTypeDirective"
    #
    # searchObj = re.search("(be|is|are).*(equivalent|equal to|a class derived from|an instance of).* ((int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))", str, re.M | re.S)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "MethodParameterTypeDirective"
    #
    #
    # #Return Value Directive
    # searchObj = re.match("return|result", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    # searchObj = re.search("Return|Result", str, re.M | re.S )
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    #
    # searchObj = re.search("@return", str, re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    # searchObj = re.search("(return|returns|returned|returning)\s+(a|the|this)?\s*(([A-Z]+\w*)+|executor|collection|map|.* data|set)", str, re.M | re.S )
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective111"
    #
    # searchObj = re.search("(value|parameter|object)s?\s+(is|be|are)?\s*(return|returns|returned|returning)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    # searchObj = re.search("(method|\w+\(.*\))\s+(must|should|can|could|may)?\s*(return|returns|returned|returning)\s+(a|the|this)?.*(([A-Z]+\w*)+|true|false|element|object|null)", str,
    #                       re.M | re.S )
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    # searchObj = re.search("(result|results|returned \w*)\s+(must|should|can|could|may)?\s+(is|be|are)+",str,
    #                     re.M | re.S)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    # searchObj = re.search("\s+(must|should|can|could|may)?\s+return", str,
    #                       re.M | re.S)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    # searchObj = re.search("this method must allocate a new array", str,
    #                       re.M | re.S|re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    # searchObj = re.search("(results|array|token|iterator) returned", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    # searchObj = re.search("(must|should) be returned", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     ##print searchObj.group()
    #     return "ReturnValueDirective"
    #
    #
    # #String Format Directive
    # searchObj = re.search("(must|should) (be|is|are|start with|starting|ends with) .*(\".*\"|\'.*\'|string)", str,
    #                       re.M | re.S| re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "StringFormatDirective"
    #
    # searchObj = re.search("(start with|starting|ends with) .*(\".*\"|\'.*\'|string)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "StringFormatDirective"
    #
    # # searchObj = re.search("string .*(are|is|start with|starting|ends with) .*(\".*\"|\'.*\'|string)", str,
    # #                       re.M | re.S | re.I)
    # # if searchObj:
    # #     # print searchObj.group()
    # #     return "StringFormatDirective"
    #
    # searchObj = re.search("string .*must .*(contain|be)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "StringFormatDirective"
    #
    # searchObj = re.search("(string|encoded|currencyCode|encodedKey|used with) .*((RFC \d+)|UTF-8|ASCII|X.509|ISO \d+)", str,
    #                       re.M | re.S)
    # if searchObj:
    #     #print searchObj.group()
    #     return "StringFormatDirective"
    #
    # searchObj = re.search("the format .*(follow|(be taken from)) .*(RFC|Unicode)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "StringFormatDirective"
    #
    # searchObj = re.search("must conform to RFC", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "StringFormatDirective"
    #
    # searchObj = re.search("string .*must .*be .*digit", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "StringFormatDirective"
    #
    # searchObj = re.search("sequence of characters must represent", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "StringFormatDirective"
    #
    # searchObj = re.search("The specified provider must be registered in the security provider list.", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "StringFormatDirective"
    #
    #
    # #Method Call Visibility Directive
    # searchObj = re.search("be necessary to use .*method", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("Constructor .*used (in|for|by)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("(this|it) .*(be|is|are) .*called (from|outside)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("call .*method directly", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("((should not)|(discouraged from)) call .*method", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("method .*(should)*.*not.*be (relied|used|referenced)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("method is for .*only", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("[A-Z]+.* should (no|not) .*be (used|instantiated)", str,
    #                       re.M | re.S)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("method .*(should)*.*be (relied|used|referenced|called)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("(should).*(relied|used|referenced|called).*method", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("is internal to", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     #print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("may (call|instantiate) .*(method|class)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodCallVisibilityDirective"
    #
    # searchObj = re.search("class .*(may|not) .*be instantiated", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodCallVisibilityDirective"


    # #Exception Raising Directive    @exception; @throws; throw an IllegalArgumentException; raise exceptions
    # searchObj = re.search("Exception .*(be|is|are) .*thrown", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "ExceptionRaisingDirective"
    #
    # searchObj = re.search("@exception|@throws", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "ExceptionRaisingDirective"
    #
    # searchObj = re.search("throw .*Exception", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "ExceptionRaisingDirective"
    #
    # searchObj = re.search("raise .*Exception", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "ExceptionRaisingDirective"


    # #Method Call Sequence Directive
    # searchObj = re.search("(after|before) .*((being used)|calling|using|invoking|called)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodCallSequenceDirective"
    #
    # searchObj = re.search("(should|must) be called .*(whenever|when|associated with)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodCallSequenceDirective"
    #
    # searchObj = re.search("(invoked|called|call|calls) .*(before|after)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodCallSequenceDirective"




    # #Extensible Class Identification  Directive
    # searchObj = re.search("(instantiate|extend) .*(class|interface)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "ExtensibleClassIdentificationDirective"
    #
    # searchObj = re.search("(implemented|implement) .*(interface)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "ExtensibleClassIdentificationDirective"
    #
    # searchObj = re.search("(may|should|can) subclass", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "ExtensibleClassIdentificationDirective"
    #
    # searchObj = re.search("(it|class|interface) .*(be|is|are) .*(subclassed|extended|implemented)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "ExtensibleClassIdentificationDirective"


    # #Method Overriding Directive
    # searchObj = re.search("(subclass)(es)? .*(reimplement|override|extend|override|extend)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodOverridingDirective"
    #
    # searchObj = re.search("(extend) .*method", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodOverridingDirective"
    #
    # searchObj = re.search("method .*(override|overridden|re-implemented|extended|implemented)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodOverridingDirective"
    #
    # searchObj = re.match("Override", str,
    #                       re.M | re.S )
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodOverridingDirective"



    # #Method Extension Directive
    # searchObj = re.search("(call|invoke) (super.|(.*super))", str,
    #                      re.M | re.S|re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodExtensionDirective"
    #
    # searchObj = re.search("(super.).* (should|must) be (called|invoked)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "MethodExtensionDirective"



    # #Call Contract Subclassing Directive
    # searchObj = re.search("(subclasses|subclass) .*(call) .*(method|constructor)", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "CallContractSubclassingDirective"
    #
    # searchObj = re.search("If you override this method, then you should", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "CallContractSubclassingDirective"



    # #Alternative Directive
    # searchObj = re.search("@deprecated", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "AlternativeDirective"
    #
    # searchObj = re.search("preferable to", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "AlternativeDirective"
    #
    # searchObj = re.search("be more efficient to use", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "AlternativeDirective"
    #
    # searchObj = re.search("instead", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "AlternativeDirective"
    #
    # searchObj = re.search("replace", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "AlternativeDirective"
    #
    # searchObj = re.search("a better choice", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "AlternativeDirective"


    #Synchronization Directive
    # searchObj = re.search("thread-safe", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "SynchronizationDirective111"
    #
    # searchObj = re.search("synchronized", str,
    #                       re.M | re.S | re.I)
    # if searchObj:
    #     # print searchObj.group()
    #     return "SynchronizationDirective111"



    return ""
print filterMethodCallDirective(
     """@param autoGeneratedKeys a flag indicating whether auto-generated keys should be returned; one of Statement.RETURN_GENERATED_KEYS or Statement.NO_GENERATED_KEYS"""
    )
# for Subclassing Directive
def filterSubclassingDirective(str):
    pass


# for Miscellaneous Directive
def filterMiscellaneousDirective(str):
    pass