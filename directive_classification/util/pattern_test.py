
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import xml.dom.minidom
from pattern_filter import filterMethodCallDirective

domTree = xml.dom.minidom.parse("../data/directive_other.xml")
dataset = domTree.getElementsByTagName("dataset")[0]

TP = 0
FP = 0
FN = 0
TN = 0
for group in dataset.getElementsByTagName("group"):
    name = group.getAttribute("name").replace(" ","")
    if True :
        directives = group.getElementsByTagName("directive")

        for directive in directives:
            directiveKind = directive.getAttribute("kind").replace(" ","").decode("utf-8").encode("utf-8")
            if directiveKind == "NullSemanticsDirective":
                directiveKind = "NullAllowedDirective"

            correctKind = "NullAllowedDirective"

            line = directive.firstChild.wholeText.strip()
            line = line.decode("utf-8").encode("utf-8")
            line = line.replace("\t", " ").replace("\n", " ")
            line = line.decode("utf-8").encode("utf-8")

            directiveTestKind = filterMethodCallDirective(line)
            # if directiveTestKind == "SynchronizationDirective111":
            #     TP = TP + 1
            #     continue

            if directiveTestKind == correctKind and directiveKind == correctKind:
                TP = TP + 1
            elif directiveTestKind == correctKind and directiveKind != correctKind:
                FP = FP + 1
                print "FP: "+line
            elif directiveTestKind != correctKind and directiveKind != correctKind:
                TN = TN + 1
            else:
                FN = FN + 1
                print "FN: "+line

print "TP FP FN TN:"
print TP, FP, FN, TN
pricision = float(TP)/(float(TP)+float(FP))
print "pricision: "
print pricision
recall = float(TP)/(float(TP)+float(FN))
print "recall: "
print recall


