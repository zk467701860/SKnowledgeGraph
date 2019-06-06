import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import xml.dom.minidom
import MySQLdb

def notNull(string):
    searchObj = re.search('@param (\w+).* ((not be null)|(not null))', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = ""
        print param
        return [param, condition]

    searchObj = re.search('May not be null', string, re.M | re.S | re.I)
    if searchObj:
        param = "ALL"
        condition = ""
        print param
        return [param, condition]

    searchObj = re.search('((@throws)|(@exception)) .*if (the)* (\w+) is null', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(5)
        condition = ""
        print param
        return [param, condition]

    searchObj = re.search('@return .*never null', string, re.M | re.S | re.I)
    if searchObj:
        param = "RETURN VALUE"
        condition = ""
        print param
        return [param, condition]

    searchObj = re.search('neither (\w+) is null', string, re.M | re.S | re.I)
    if searchObj:
        param = "ALL"
        condition = ""
        print param
        return [param, condition]

    return ['', '']

def nullSemantics(string):
    searchObj = re.search('@?param (\w+).* may be null.* if null, (.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]
    searchObj = re.search('@?param (\w+).* or null.* if null, (.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]

    searchObj = re.search('@?param (\w+).* may be null.* (if.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]

    searchObj = re.search('@?param (\w+).* or null.*(if.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]

    searchObj = re.search('@?param (\w+).* ((may be)|or) null.*', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = ''
        print param, condition
        return [param, condition]

    searchObj = re.search('@?param (\w+).* or null.*(in which case.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]

    searchObj = re.search('null means\s*(that)?\s*((the)? (.+) should.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(4)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]

    searchObj = re.search('If (.*) is null,(.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]

    searchObj = re.search('@param (\w+).* null.* (if.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]

    searchObj = re.search('@?param (\w+).*, (null (uses|means|results|ignored).*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = searchObj.group(2)
        print param, condition
        return [param, condition]

    searchObj = re.search('@param (\w*).*should be null', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        condition = ''
        print param, condition
        return [param, condition]

    return ['', '']

def numberRange(string):
    searchObj = re.search('@param (\w+).*must be (.*) or greater', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        range = [str(searchObj.group(2)),'infinite']
        enum = ''
        print param, range, enum
        return [param, range, enum]

    searchObj = re.search('@param (\w+).*must be non-negative', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        range = ['0', 'infinite']
        enum = ''
        print param, range, enum
        return [param, range, enum]

    searchObj = re.search('(.*) must be between (\d+) (to|and) (\d+)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        range = [str(searchObj.group(2)), str(searchObj.group(4))]
        enum = ''
        print param, range, enum
        return [param, range, enum]

    searchObj = re.search('(.*) is between (\d+) (to|and) (\d+)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        range = [str(searchObj.group(2)), str(searchObj.group(4))]
        enum = ''
        print param, range, enum
        return [param, range, enum]

    searchObj = re.search('@param (\w+).*must be (>|>=)\s*(\d+)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        range = [str(searchObj.group(3)), 'infinite']
        enum = ''
        print param, range, enum
        return [param, range, enum]

    searchObj = re.search('@param (\w+).*must be (<|<=)\s*(\d+)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        range = [ 'infinite',str(searchObj.group(3))]
        enum = ''
        print param, range, enum
        return [param, range, enum]

    searchObj = re.search('@param (\w+).*must be either (.*) or (.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        range = [searchObj.group(2), searchObj.group(3)]
        enum = ''
        print param, range, enum
        return [param, range, enum]

    searchObj = re.search('@param (\w+).*(between|range) (\d+)-(\d+)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        range = [str(searchObj.group(3)), str(searchObj.group(4))]
        enum = ''
        print param, range, enum
        return [param, range, enum]


    return ['', [], '']

def stringFormat(string):
    searchObj = re.search('@param (\w+).*must be ("\w+")', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        encode = ''
        form = searchObj.group(2)
        print param, encode, form
        return [param, encode, form]

    searchObj = re.search('(.*) must conform to (RFC 2965)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        encode = searchObj.group(2)
        form = ''
        print param, encode, form
        return [param, encode, form]

    searchObj = re.search('The format of (\w+) should follow that specified in (RFC 2732)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        encode = searchObj.group(2)
        form = ''
        print param, encode, form
        return [param, encode, form]

    searchObj = re.search('@param (\w+).*must be (.*)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        encode = searchObj.group(2)
        form = ''
        print param, encode, form
        return [param, encode, form]

    searchObj = re.search('((\w+\s+)+)must be ((\w+\s+)+)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        encode = searchObj.group(3)
        form = ''
        print param, encode, form
        return [param, encode, form]

    searchObj = re.search('If the? (\w+).*in (RFC 2253|X.509|X.501|Unicode 3.2)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        encode = searchObj.group(2)
        form = ''
        print param, encode, form
        return [param, encode, form]

    searchObj = re.search('@param (\w+).*(PKCS #8|X.509|ISO 4217|)', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        encode = searchObj.group(2)
        form = ''
        print param, encode, form
        return [param, encode, form]


    return ['', '', '']

def methodParameterType(string):
    searchObj = re.search('(.*) (must|should) (be|is|are) .*of.+type (([A-Z]+\w*)+|(int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))', string, re.M | re.S | re.I)
    if searchObj:
        param = searchObj.group(1)
        type = searchObj.group(4)
        print param, type
        return [param, type]


    searchObj = re.search('@param (\w+).*(must|should) implement.* ([A-Z]+\w*)', string, re.M | re.S)
    if searchObj:
        param = searchObj.group(1)
        type = searchObj.group(3)
        print param, type
        return [param, type]

    searchObj = re.search('The? (.*) (Must|must|should) implement.* ([A-Z]+\w*)', string, re.M | re.S)
    if searchObj:
        param = searchObj.group(1)
        type = searchObj.group(3)
        print param, type
        return [param, type]

    searchObj = re.search('The? (.*) (Must|must|should) implement.* (\w+(\.\w+)+)', string, re.M | re.S)
    if searchObj:
        param = searchObj.group(1)
        type = searchObj.group(3)
        print param, type
        return [param, type]

    searchObj = re.search('@param (\w+).*subclass of.* (([A-Z]+\w*)+|(int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))', string, re.M | re.S )
    if searchObj:
        param = searchObj.group(1)
        type = searchObj.group(2)
        print param, type
        return [param, type]

    searchObj = re.search('((\w+\s+)+)must be ((\w+\s+)+)(([A-Z]+\w*)+|(int |int\.|char|long|short|double|float|string|boolean|comparable|comparator|serialized))', string, re.M | re.S)
    if searchObj:
        param = searchObj.group(1)
        type = searchObj.group(2)
        print param, type
        return [param, type]


    return ['', '']

def returnValue(string):
    searchObj = re.search('(Returns .*\.?)', string, re.M | re.S)
    if searchObj:
        desc = searchObj.group(1)
        condition = ''
        print desc, condition
        return [desc, condition]

    searchObj = re.search('(@return .*\.?)', string, re.M | re.S | re.I)
    if searchObj:
        desc = searchObj.group(1)
        condition = ''
        print desc, condition
        return [desc, condition]

    searchObj = re.search('if (.*), (.*)', string, re.M | re.S | re.I)
    if searchObj:
        desc = searchObj.group(2)
        condition = searchObj.group(1)
        print desc, condition
        return [desc, condition]

    searchObj = re.search('(.*) if (.*)', string, re.M | re.S | re.I)
    if searchObj:
        desc = searchObj.group(1)
        condition = searchObj.group(2)
        print desc, condition
        return [desc, condition]

    searchObj = re.search('(the returned (\w+) is.*)',string, re.M | re.S|re.I)
    if searchObj:
        desc = searchObj.group(1)
        condition = ''
        print desc, condition
        return [desc, condition]

    searchObj = re.search('(should|must) (\w+)*\s*return (.*)', string, re.M | re.S | re.I)
    if searchObj:
        desc = searchObj.group(3)
        condition = ''
        print desc, condition
        return [desc, condition]

    searchObj = re.search('(returned|results|result|).*(must|should) (.*)\.?', string, re.M | re.S | re.I)
    if searchObj:
        desc = searchObj.group(3)
        condition = ''
        print desc, condition
        return [desc, condition]

    searchObj = re.search('(returned|results|result|).*(be|is|are) (.*)\.?', string, re.M | re.S | re.I)
    if searchObj:
        desc = searchObj.group(3)
        condition = ''
        print desc, condition
        return [desc, condition]

    return ['', '']

def methodCallVisibility(string):
    searchObj = re.search('(call|use).* method if (.*)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 0
        desc = searchObj.group(2)
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('((should not)|(discouraged from)).*(call|use).* method', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 0
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('not.*be.*(call|use|reference)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 0
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('method .*(should)*.*not.*be (relied|used|referenced)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 0
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('[A-Z]+.* should (no|not) .*be (used|instantiated)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 0
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('be necessary to use .*method', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('Constructor .*used (in|for|by)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('(this|it) .*(be|is|are) .*called (from|outside)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('call .*method directly', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('(method|constructor) only used in', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('method is for .*only', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('(method|constructor) .*(should)*.*be (relied|used|referenced|called)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('(should).*(relied|used|referenced|called).*method', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('is internal to', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('may (call|instantiate) .*(method|class)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('class .*not .*be instantiated', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 0
        desc = ''
        print visibility, desc
        return [visibility, desc]

    searchObj = re.search('class .*may .*be (instantiated|used)', string, re.M | re.S | re.I)
    if searchObj:
        visibility = 1
        desc = ''
        print visibility, desc
        return [visibility, desc]

    return ['', '']

def exceptionRaising(string):
    searchObj = re.search('(\w*Exception) .*(be|is|are) .*thrown', string, re.M | re.S|re.I)
    if searchObj:
        excep = searchObj.group(1)
        condition = ''
        print excep, condition
        return [excep, condition]

    searchObj = re.search('(@exception|@throws) (\w*Exception).* (if|If)(.*)', string, re.M | re.S )
    if searchObj:
        excep = searchObj.group(2)
        condition = searchObj.group(4)
        print excep, condition
        return [excep, condition]

    searchObj = re.search('(@exception|@throws) (\w*Exception)', string, re.M | re.S)
    if searchObj:
        excep = searchObj.group(2)
        condition = ''
        print excep, condition
        return [excep, condition]

    searchObj = re.search('(not|never) (raise|throw).* (\w*Exception)', string, re.M | re.S|re.I)
    if searchObj:
        excep = searchObj.group(3)
        condition = 'not throw'
        print excep, condition
        return [excep, condition]

    searchObj = re.search('(raise|throw).* (\w*Exception)', string, re.M | re.S|re.I)
    if searchObj:
        excep = searchObj.group(2)
        condition = ''
        print excep, condition
        return [excep, condition]

    return ['', '']

def methodCallSequence(string):
    searchObj = re.search('(after|before) (a|the) (([\w\.]+)).*((being used)|calling|using|invoking|called)', string,
                          re.M | re.S | re.I)
    if searchObj:
        compMethod = searchObj.group(3)
        seq = searchObj.group(1)
        print compMethod, seq
        return [compMethod, seq]

    searchObj = re.search('(after|before) (([\w\.]+)).*((being used)|calling|using|invoking|called)', string, re.M | re.S | re.I)
    if searchObj:
        compMethod = searchObj.group(2)
        seq = searchObj.group(1)
        print compMethod, seq
        return [compMethod, seq]

    searchObj = re.search('(should|must) be called .*(whenever|when|associated with) (a|the) (\w+)', string, re.M | re.S | re.I)
    if searchObj:
        compMethod = searchObj.group(4)
        seq = 'after'
        print compMethod, seq
        return [compMethod, seq]

    searchObj = re.search('(should|must) be called .*(whenever|when|associated with) (\w+)', string, re.M | re.S | re.I)
    if searchObj:
        compMethod = searchObj.group(3)
        seq = 'after'
        print compMethod, seq
        return [compMethod, seq]

    searchObj = re.search('(invoked|called|call|calls) .*(before|after) (a|the) ([\w\.]+)', string, re.M | re.S | re.I)
    if searchObj:
        compMethod = searchObj.group(4)
        seq = searchObj.group(2)
        print compMethod, seq
        return [compMethod, seq]

    searchObj = re.search('(invoked|called|call|calls) .*(before|after) ([\w\.]+)', string, re.M | re.S | re.I)
    if searchObj:
        compMethod = searchObj.group(3)
        seq = searchObj.group(2)
        print compMethod, seq
        return [compMethod, seq]

    return ['', '']

def extensibleClassIdentification(string):
    searchObj = re.search('@noextend', string, re.M | re.S | re.I)
    if searchObj:
        extensible = 0
        print extensible
        return [extensible, '']

    searchObj = re.search('not.*(implemented|implement) .*(interface)', string, re.M | re.S | re.I)
    if searchObj:
        extensible = 0
        print extensible
        return [extensible, '']

    searchObj = re.search('(implemented|implement) .*(interface)', string, re.M | re.S | re.I)
    if searchObj:
        extensible = 1
        print extensible
        return [extensible, '']

    searchObj = re.search('(may|should|can).*not.*subclass', string, re.M | re.S | re.I)
    if searchObj:
        extensible = 0
        print extensible
        return [extensible, '']

    searchObj = re.search('(may|should|can) subclass', string, re.M | re.S | re.I)
    if searchObj:
        extensible = 1
        print extensible
        return [extensible, '']

    searchObj = re.search('(it|class|interface) .*(be|is|are) not.*(subclassed|extended|implemented)', string,
                          re.M | re.S | re.I)
    if searchObj:
        extensible = 0
        print extensible
        return [extensible, '']

    searchObj = re.search('(it|class|interface) .*(be|is|are) .*(subclassed|extended|implemented)', string, re.M | re.S | re.I)
    if searchObj:
        extensible = 1
        print extensible
        return [extensible, '']

    searchObj = re.search('not.*(instantiate|extend) .*(class|interface)', string, re.M | re.S | re.I)
    if searchObj:
        extensible = 0
        print extensible
        return [extensible, '']

    searchObj = re.search('(instantiate|extend) .*(class|interface)', string, re.M | re.S | re.I)
    if searchObj:
        extensible = 1
        print extensible
        return [extensible, '']


    return ['', '']

def methodOverriding(string):
    searchObj = re.search('(subclass)(es)? .*(not|never).*(reimplement|override|extend|override|extend)', string, re.M | re.S | re.I)
    if searchObj:
        override = 0
        print override
        return [override, '']

    searchObj = re.search('(subclass)(es)? .*(reimplement|override|extend|override|extend)', string, re.M | re.S | re.I)
    if searchObj:
        override = 1
        print override
        return [override, '']

    searchObj = re.search('(not|never).*(extend) .*method', string, re.M | re.S | re.I)
    if searchObj:
        override = 0
        print override
        return [override, '']

    searchObj = re.search('(extend) .*method', string, re.M | re.S | re.I)
    if searchObj:
        override = 1
        print override
        return [override, '']

    searchObj = re.search('method .*(not|never).*(override|overridden|re-implemented|extended|implemented)', string,
                          re.M | re.S | re.I)
    if searchObj:
        override = 0
        print override
        return [override, '']

    searchObj = re.search('method .*(override|overridden|re-implemented|extended|implemented)', string, re.M | re.S | re.I)
    if searchObj:
        override = 1
        print override
        return [override, '']

    searchObj = re.search('(not|never).*(override|overridden|re-implemented|extended|implemented)', string, re.M | re.S | re.I)
    if searchObj:
        override = 0
        print override
        return [override, '']

    searchObj = re.match("Override", string, re.M | re.S )
    if searchObj:
        override = 1
        print override
        return [override, '']

    return ['', '']

def methodExtension(string):
    searchObj = re.search("(call|invoke).*(super\.\w+)", string, re.M | re.S| re.I)
    if searchObj:
        parentMethod = searchObj.group(2)
        print parentMethod
        return [parentMethod, '']

    searchObj = re.search("(call|invoke).*super implementation", string, re.M | re.S | re.I)
    if searchObj:
        parentMethod = 'self'
        print parentMethod
        return [parentMethod, '']

    searchObj = re.search("(call|invoke).* super", string, re.M | re.S | re.I)
    if searchObj:
        parentMethod = 'self'
        print parentMethod
        return [parentMethod, '']

    searchObj = re.search("(super.\w+).* (should|must) be (called|invoked)", string, re.M | re.S| re.I)
    if searchObj:
        parentMethod = searchObj.group(1)
        print parentMethod
        return [parentMethod, '']

    return ['', '']

def callContractSubclassing(string):
    searchObj = re.search("(subclasses|subclass) .*(call) .*(method|constructor)", string, re.M | re.S | re.I)
    if searchObj:
        invokeMethod = searchObj.group(1)
        print invokeMethod
        return [invokeMethod, '']

    searchObj = re.search("If you override this method, then you should", string, re.M | re.S | re.I)
    if searchObj:
        invokeMethod = searchObj.group(1)
        print invokeMethod
        return [invokeMethod, '']

    return ['', '']

def alternativeDirective(string):
    searchObj = re.search("@deprecated", string, re.M | re.S | re.I)
    if searchObj:
        invokeMethod = searchObj.group(1)
        print invokeMethod
        return [invokeMethod, '']

    return ['', '']

def synchronizationDirective(string):
    searchObj = re.search("thread-safe", string, re.M | re.S | re.I)
    if searchObj:
        invokeMethod = searchObj.group(1)
        print invokeMethod
        return [invokeMethod, '']

    return ['', '']


alternativeDirective('super.getLabelProvider must be invoked.  ')

# domTree = xml.dom.minidom.parse("../data/directives.xml")
# dataset = domTree.getElementsByTagName("dataset")[0]
# for group in dataset.getElementsByTagName("group"):
#     name = group.getAttribute("name").replace(" ","")
#     #todo
#     if name == "AlternativeDirective" :
#         directives = group.getElementsByTagName("directive")
#
#         for directive in directives:
#             directiveKind = directive.getAttribute("kind").replace(" ","").decode("utf-8").encode("utf-8")
#             #todo
#             if directiveKind == "AlternativeDirective":
#                 title = directive.getAttribute("containing-api-element").replace(" ", "").decode("utf-8").encode("utf-8")
#                 title1 = title[0:title.rfind('/')]
#                 methodName = title1[title1.rfind('/')+1:]
#                 className = title1[0:title1.rfind('/')]
#
#                 line = directive.firstChild.wholeText.strip()
#                 line = line.decode("utf-8").encode("utf-8")
#                 line = line.replace("\t", " ").replace("\n", " ")
#                 line = line.decode("utf-8").encode("utf-8")
#
#                 #todo
#                 list = alternativeDirective(line)
#                 if list[0] == '':
#                     continue
#
#                 db = MySQLdb.connect("localhost", "root", "root", "test", charset='utf8')
#                 cursor = db.cursor()
#                 #todo
#                 sql = "INSERT INTO api(class, method, param, other1, other2,directive,kind) VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (className,methodName,'',list[0],'',title+" "+line.replace('"',"").replace('\'',''),directiveKind)
#                 cursor.execute(sql)
#                 db.commit()
#                 # try:
#                 #     cursor.execute(sql)
#                 # except:
#                 #     db.commit()
#                 # else:
#                 #     db.commit()
#                 db.close()
