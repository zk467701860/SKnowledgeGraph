import sys
reload(sys)
sys.setdefaultencoding('utf8')
import fasttext
from pattern_filter import *
from universal_pattern import *

def sentence2knowledge(text):
    #利用已有分类模型进行概要类别分类，得到句子概要类别
    classifier = fasttext.load_model('news_fasttext.model.bin', label_prefix='__label__')
    es = classifier.predict(text)

    #利用各概要类别下的模式进行详细类别分类，得到句子详细类别
    ess = ''
    if es == 'MethodCallDirective':
        ess = filterMethodCallDirective(text)
    elif es == 'SubclassingDirective':
        ess = filterSubclassingDirective(text)
    elif es == 'MiscellaneousDirective':
        ess = filterMiscellaneousDirective(text)
    elif es == 'NonDirective':
        pass
    if ess == '':
        return []

    #利用各详细类别下的抽取模式，将自然语言形式的语句转化成结构化的约束知识
    result = []
    if ess == 'NotNullDirective':
        result = notNull(text)
    elif ess == 'NullSemanticDirective':
        result = nullSemantics(text)
    elif ess == 'NumberRangeDirective':
        result = numberRange(text)
    elif ess == 'StringFormatDirective':
        result = stringFormat(text)
    elif ess == 'MethodParameterTypeDirective':
        result = methodParameterType(text)
    elif ess == 'ReturnValueDirective':
        result = returnValue(text)
    elif ess == 'MethodCallVisibilityDirective':
        result = methodCallVisibility(text)
    elif ess == 'ExceptionRaisingDirective':
        result = exceptionRaising(text)
    elif ess == 'ExtensibleClassIdentificationDirective':
        result = extensibleClassIdentification(text)
    elif ess == 'MethodOverridingDirective':
        result = methodOverriding(text)
    elif ess == 'MethodExtensionDirective':
        result = methodExtension(text)
    elif ess == 'CallContractSubclassingDirective':
        result = callContractSubclassing(text)
    elif ess == 'MethodCallSequenceDirective':
        result = methodCallSequence(text)
    elif ess == 'SynchronizationDirective':
        result = synchronizationDirective(text)
    elif ess == 'AlternativeDirective':
        result = alternativeDirective(text)

    return result