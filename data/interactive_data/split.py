import json
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--add_zhihu', default=False, action='store_true', help="if True, will only generate query generation data")
args = parser.parse_args()

data_1 = json.load(open('data.json', 'r', encoding='utf8'))

if args.add_zhihu:
    data_2 = json.load(open('data_augmentation_zhihu.json', 'r', encoding='utf8'))
    data = data_1 + data_2
else:
    data = data_1

print(len(data))
random.shuffle(data)

if args.add_zhihu:
    data_train = {'data': data[: 6000]}
    data_dev = {'data': data[6000: 6200]}
    data_test = {'data': data[6200: ]}
else:
    data_train = {'data': data[: 4700]}
    data_dev = {'data': data[4700: 5100]}
    data_test = {'data': data[5100: ]}

print(len(data_train['data']))
print(len(data_dev['data']))
print(len(data_test['data']))
json.dump(data_dev, open('dev.json', 'w', encoding='utf8'), indent = 4, ensure_ascii=False, )
json.dump(data_test, open('test.json', 'w', encoding='utf8'), indent = 4, ensure_ascii=False, )
json.dump(data_train, open('train.json', 'w', encoding='utf8'), indent = 4, ensure_ascii=False, )

