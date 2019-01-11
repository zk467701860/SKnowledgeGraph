from unittest import TestCase

from entity_link.corpus import AliasStatisticsUtil


class TestAliasStatisticsUtil(TestCase):
    def test_init_vocabulary_from_json(self):
        aliasStatisticsUtil = AliasStatisticsUtil()
        aliasStatisticsUtil.init_vocabulary_from_json("alias_to_entity_count.json")
        self.assertEqual(5, len(aliasStatisticsUtil.label_vocabulary))

        aliasStatisticsUtil.init_vocabulary_from_json("token_lower_alias_to_entity_count.json")
        self.assertEqual(5, len(aliasStatisticsUtil.label_vocabulary))

    def test_count_occur_in_content(self):
        aliasStatisticsUtil = AliasStatisticsUtil()
        aliasStatisticsUtil.init_vocabulary_from_json("alias_to_entity_count.json")
        aliasStatisticsUtil.count_occur_in_content('''An java.lang.animation() listener receives notifications from an animation. Notifications indicate animation related events, such as the end or the repetition of the animation. onAnimationStart
added in API level 26 onAnimationStart(Animator animation, 
                boolean isReverse) onAnimationStart(Animator, 
                boolean)
public void onAnimationStart (Animator animation, 
                boolean isReverse)
Notifies the start of the animation as well as the animation's overall play direction. This method's default behavior is to call onAnimationStart(Animator). This method can be overridden, though not required, to get the additional play direction info when an animation starts. Skipping calling super when overriding this method results in onAnimationStart(Animator) not getting called.

Parameters
animation	Animator: The started animation.
isReverse	boolean: Whether the animation is playing in reverse.''')
        aliasStatisticsUtil.write_to_tsv("alias_to_entity.tsv")

        aliasStatisticsUtil.init_vocabulary_from_json("token_lower_alias_to_entity_count.json")
        aliasStatisticsUtil.count_occur_in_content('''An java.lang.animation() listener receives notifications from an animation. Notifications indicate animation related events, such as the end or the repetition of the animation. onAnimationStart
        added in API level 26 onAnimationStart(Animator animation, 
                        boolean isReverse) onAnimationStart(Animator, 
                        boolean) animatorlistener
        public void onAnimationStart (Animator animation, 
                        boolean isReverse)
        Notifies the start of the animation as well as the animation's overall play direction. This method's default behavior is to call onAnimationStart(Animator). This method can be overridden, though not required, to get the additional play direction info when an animation starts. Skipping calling super when overriding this method results in onAnimationStart(Animator) not getting called.

        Parameters
        animation	Animator: The started animation.
        isReverse	boolean: Whether the animation is playing in reverse.''')
        aliasStatisticsUtil.write_to_tsv("token_lower_alias_to_entity.tsv")

    def test_write_to_tsv_ngram(self):
        aliasStatisticsUtil = AliasStatisticsUtil(alias_ngram=True)
        aliasStatisticsUtil.init_vocabulary_from_json("token_lower_alias_to_entity_count.json")
        aliasStatisticsUtil.count_occur_in_content('''An java.lang.animation() listener receives notifications from an animation. Notifications indicate animation related events, such as the end or the repetition of the animation. onAnimationStart
        added in API level 26 onAnimationStart(Animator animation, 
                        boolean isReverse) onAnimationStart(Animator, 
                        boolean) animatorlistener
        public void onAnimationStart (Animator animation, 
                        boolean isReverse)
        Notifies the start of the animation as well as the animation's overall play direction. This method's default behavior is to call onAnimationStart(Animator). This method can be overridden, though not required, to get the additional play direction info when an animation starts. Skipping calling super when overriding this method results in onAnimationStart(Animator) not getting called.

        Parameters
        animation	Animator: The started animation.
        isReverse	boolean: Whether the animation is playing in reverse.''')
        aliasStatisticsUtil.write_to_tsv("ngram_token_lower_alias_to_entity.tsv")
