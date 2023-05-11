import json
import random
import re
import os
from cpm_live.dataset import build_dataset

def separate_strings(text):
    text = re.sub(r'\d+\.', '', text) # remove numbers and dots
    text = re.sub(r'[\'\"\“\”\‘]', '', text)
    phrases = text.strip().split("\n")
    phrases = [phrase.strip() for phrase in phrases if phrase.strip()]
    return phrases

def create_data():
    data = []

    base_path = "../../data/pipeline_data"

    # constructing answer data
    def load_data(path):
        data = []
        with open(path) as fin:
            lines = fin.readlines()
            for line in lines:
                line_new = json.loads(line.strip())
                line_new["context"] = line_new["abstracts"]
                data.append(line_new)
        return data

    data += load_data(os.path.join(base_path, "answer_20000.json"))

    data_new = []
    for line in data:
        question = line["question"]
        context = line["context"]
            
        new_context = ""
        for c in context:
            if len(c) == 0:
                continue
            new_context += "摘要：" + c + "；"
        context = new_context
        
        context = re.sub('<', '<<', context)

        answer = line["answer"]
        
        if answer[-1] not in ["。", "！", "？"]:
            continue
        if answer[: 3] == "答案：":
            answer = answer[3: ]
        elif answer[: 2] == "答：":
            answer = answer[2: ]
        answer = re.sub('<', '<<', answer)
        question = re.sub('<', '<<', question)
        src_line = context + "问题：" + question + "；答案："
        tgt_line = answer
        if len(tgt_line) < 100:
            continue
        data_new.append([src_line, tgt_line])

    data = data_new
    print(len(data))

    # constructing query data
    with open(os.path.join(base_path, "query_40000.json")) as fin:
        lines = fin.readlines()
        for line in lines:
            line_new = json.loads(line.strip())
            data.append(["原始问题：" + line_new["question"] + "搜索引擎查询语句：", "；".join(separate_strings(line_new["answer"]))])
    print(len(data))

    # constructing abstracts data    
    with open(os.path.join(base_path, "abstract_50000.json")) as fin:
        lines = fin.readlines()
        for line in lines:
            line_new = json.loads(line.strip())
            if len(line_new["abstracts"]) < 8 and "无" in line_new["abstracts"]:
                continue
            data.append(["原始问题：" + line_new["question"] + "当前搜索引擎查询语句：" + line_new["query"] + "当前页面具体内容：" + line_new["page_detail"] + "摘取和原问题相关的摘要：", line_new["abstracts"]])
    print(len(data))

    random.shuffle(data)

    train_data = data[: -int(0.1 * len(data))]
    dev_data = data[-int(0.1 * len(data)): -int(0.05 * len(data))]
    test_data = data[-int(0.05 * len(data)): ]

    def dump_file(split, data):
        with open("{}.txt".format(split), 'w') as fout:
            for i, item in enumerate(data):
                src_line = item[0]
                tgt_line = item[1]
                src_line = src_line.strip()
                tgt_line = tgt_line.strip()
                src_line = re.sub('<', '<<', src_line)
                tgt_line = re.sub('<', '<<', tgt_line)
                fout.write(json.dumps({'source': src_line, '<ans>': tgt_line}, ensure_ascii=False) + '\n')

        fin = open('{}.txt'.format(split), 'r', encoding='utf-8')
        lines = fin.readlines()

        write_path = "./{}_data".format(split)
        if not os.path.exists(write_path):
            os.makedirs(write_path)

        # the write_path directory should contain no files
        with build_dataset(write_path, "data") as dataset:
            for data in lines:
                data = json.loads(data)
                dataset.write(data)

    dump_file("train", train_data)
    dump_file("dev", dev_data)
    dump_file("test", test_data)

if __name__ == "__main__":
    create_data()

