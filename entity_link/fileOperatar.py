import json
import nltk

def deletePostJsonStopWords():
    stop_word_list = nltk.corpus.stopwords.words('english')
    # fw = codecs.open('data/alias-entity-counts1.tsv', 'w', 'utf-8')
    index = 0
    with open('data/train so post/post.json', 'r') as load_f:
        load_dict = json.load(load_f)
        for post in reversed(load_dict):
            alias_entity = post['alias_entity']
            for pair in reversed(alias_entity):
                if pair['alias'].lower() in stop_word_list:
                    print post['id']
                    index += 1
                    alias_entity.remove(pair)
            if len(alias_entity)  == 0:
                load_dict.remove(post)
        with open('data/train so post/post1.json', 'w') as write_f:
            json.dump(load_dict, write_f, indent=4)
    print index
    # fw.write('%s\n' % (new_line))
    # fw.close()

if __name__ == '__main__':
    deletePostJsonStopWords()