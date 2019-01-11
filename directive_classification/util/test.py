import json

nondir = open("../data/dataset.json","r")
nondirjson = json.load(nondir)

nontext = []
for tmp in nondirjson:

    if tmp['label'] == 0 or tmp['label'] == 1:
        nontext.append(tmp['text'])
print len(nontext)

# 0.891603053435
# 0.891603053435
# ----------------------------/n
# {u'nonDir': 200, u'MiscellaneousDirective': 62, u'MethodCallDirective': 228, u'SubclassingDirective': 94}
# {u'nonDir': 200, u'MiscellaneousDirective': 87, u'MethodCallDirective': 247, u'SubclassingDirective': 121}
# {u'nonDir': 201, u'MiscellaneousDirective': 87, u'MethodCallDirective': 262, u'SubclassingDirective': 105}
# nonDir:	 p:0.995025	 r:1.000000	 f:0.997506
# MiscellaneousDirective:	 p:0.712644	 r:0.712644	 f:0.712644
# MethodCallDirective:	 p:0.870229	 r:0.923077	 f:0.895874
# SubclassingDirective:	 p:0.895238	 r:0.776860	 f:0.831858
# 0.903536977492
# 0.903536977492
# ----------------------------/n
# {u'nonDir': 199, u'MiscellaneousDirective': 49, u'MethodCallDirective': 219, u'SubclassingDirective': 95}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 201, u'MiscellaneousDirective': 60, u'MethodCallDirective': 243, u'SubclassingDirective': 118}
# nonDir:	 p:0.990050	 r:0.995000	 f:0.992519
# MiscellaneousDirective:	 p:0.816667	 r:0.680556	 f:0.742424
# MethodCallDirective:	 p:0.901235	 r:0.920168	 f:0.910603
# SubclassingDirective:	 p:0.805085	 r:0.848214	 f:0.826087
# 0.868167202572
# 0.868167202572
# ----------------------------/n
# {u'nonDir': 200, u'MiscellaneousDirective': 54, u'MethodCallDirective': 213, u'SubclassingDirective': 73}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 203, u'MiscellaneousDirective': 88, u'MethodCallDirective': 246, u'SubclassingDirective': 85}
# nonDir:	 p:0.985222	 r:1.000000	 f:0.992556
# MiscellaneousDirective:	 p:0.613636	 r:0.750000	 f:0.675000
# MethodCallDirective:	 p:0.865854	 r:0.894958	 f:0.880165
# SubclassingDirective:	 p:0.858824	 r:0.651786	 f:0.741117
# 0.889067524116
# 0.889067524116
# ----------------------------/n
# {u'nonDir': 200, u'MiscellaneousDirective': 48, u'MethodCallDirective': 223, u'SubclassingDirective': 82}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 201, u'MiscellaneousDirective': 68, u'MethodCallDirective': 258, u'SubclassingDirective': 95}
# nonDir:	 p:0.995025	 r:1.000000	 f:0.997506
# MiscellaneousDirective:	 p:0.705882	 r:0.666667	 f:0.685714
# MethodCallDirective:	 p:0.864341	 r:0.936975	 f:0.899194
# SubclassingDirective:	 p:0.863158	 r:0.732143	 f:0.792271
# 0.882636655949
# 0.882636655949
# ----------------------------/n
# {u'nonDir': 199, u'MiscellaneousDirective': 39, u'MethodCallDirective': 225, u'SubclassingDirective': 86}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 199, u'MiscellaneousDirective': 53, u'MethodCallDirective': 275, u'SubclassingDirective': 95}
# nonDir:	 p:1.000000	 r:0.995000	 f:0.997494
# MiscellaneousDirective:	 p:0.735849	 r:0.541667	 f:0.624000
# MethodCallDirective:	 p:0.818182	 r:0.945378	 f:0.877193
# SubclassingDirective:	 p:0.905263	 r:0.767857	 f:0.830918
# 0.890675241158
# 0.890675241158
# ----------------------------/n
# {u'nonDir': 199, u'MiscellaneousDirective': 44, u'MethodCallDirective': 228, u'SubclassingDirective': 83}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 200, u'MiscellaneousDirective': 58, u'MethodCallDirective': 271, u'SubclassingDirective': 93}
# nonDir:	 p:0.995000	 r:0.995000	 f:0.995000
# MiscellaneousDirective:	 p:0.758621	 r:0.611111	 f:0.676923
# MethodCallDirective:	 p:0.841328	 r:0.957983	 f:0.895874
# SubclassingDirective:	 p:0.892473	 r:0.741071	 f:0.809756
# 0.905144694534
# 0.905144694534
# ----------------------------/n
# {u'nonDir': 200, u'MiscellaneousDirective': 54, u'MethodCallDirective': 220, u'SubclassingDirective': 89}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 200, u'MiscellaneousDirective': 75, u'MethodCallDirective': 247, u'SubclassingDirective': 100}
# nonDir:	 p:1.000000	 r:1.000000	 f:1.000000
# MiscellaneousDirective:	 p:0.720000	 r:0.750000	 f:0.734694
# MethodCallDirective:	 p:0.890688	 r:0.924370	 f:0.907216
# SubclassingDirective:	 p:0.890000	 r:0.794643	 f:0.839623
# 0.889067524116
# 0.889067524116
# ----------------------------/n
# {u'nonDir': 200, u'MiscellaneousDirective': 47, u'MethodCallDirective': 214, u'SubclassingDirective': 92}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 200, u'MiscellaneousDirective': 69, u'MethodCallDirective': 246, u'SubclassingDirective': 107}
# nonDir:	 p:1.000000	 r:1.000000	 f:1.000000
# MiscellaneousDirective:	 p:0.681159	 r:0.652778	 f:0.666667
# MethodCallDirective:	 p:0.869919	 r:0.899160	 f:0.884298
# SubclassingDirective:	 p:0.859813	 r:0.821429	 f:0.840183
# 0.900321543408
# 0.900321543408
# ----------------------------/n
# {u'nonDir': 200, u'MiscellaneousDirective': 39, u'MethodCallDirective': 229, u'SubclassingDirective': 92}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 202, u'MiscellaneousDirective': 46, u'MethodCallDirective': 270, u'SubclassingDirective': 104}
# nonDir:	 p:0.990099	 r:1.000000	 f:0.995025
# MiscellaneousDirective:	 p:0.847826	 r:0.541667	 f:0.661017
# MethodCallDirective:	 p:0.848148	 r:0.962185	 f:0.901575
# SubclassingDirective:	 p:0.884615	 r:0.821429	 f:0.851852
# 0.90192926045
# 0.90192926045
# ----------------------------/n
# {u'nonDir': 200, u'MiscellaneousDirective': 49, u'MethodCallDirective': 227, u'SubclassingDirective': 85}
# {u'nonDir': 200, u'MiscellaneousDirective': 72, u'MethodCallDirective': 238, u'SubclassingDirective': 112}
# {u'nonDir': 201, u'MiscellaneousDirective': 64, u'MethodCallDirective': 265, u'SubclassingDirective': 92}
# nonDir:	 p:0.995025	 r:1.000000	 f:0.997506
# MiscellaneousDirective:	 p:0.765625	 r:0.680556	 f:0.720588
# MethodCallDirective:	 p:0.856604	 r:0.953782	 f:0.902584
# SubclassingDirective:	 p:0.923913	 r:0.758929	 f:0.833333

nondir.close()