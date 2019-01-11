import json


def split():
    result_list = []
    need_set = set()
    with open('data/train so post/post-test.json', 'r') as test_f:
        test_list = json.load(test_f)
        for post in test_list:
            need_set.add(post['id'])
        print 'post number : %d' % (len(need_set))
        with open('data/train so post/paragraph.json', 'r') as paragraph_f:
            paragraph_list = json.load(paragraph_f)
            index = 0
            for paragraph in paragraph_list:
                print index
                if paragraph['post_id'] in need_set:
                    result_list.append(paragraph)
                index += 1
    f = open('data/train so post/paragraph-test.json', 'w')
    json.dump(result_list, f, indent=4)
    f.close()
    print 'correct: %d' % (len(result_list))

if __name__ == '__main__':
    split()