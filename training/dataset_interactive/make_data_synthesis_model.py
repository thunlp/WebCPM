import json
import random
import re
from rouge import Rouge
import os
import string
import numpy as np
import argparse

class SentenceSplitter(object):
    def __init__(self, end_operator):
        self.end_operator = end_operator

    def cut(self, text):
        sentence_set = [sentence.strip() for sentence in text.split("\n") if sentence.strip()]
        res = []

        for sentence in sentence_set:
            try:
                for s in self.rules(sentence, []):
                    res.append(s)
            except Exception as e:
                res.append(sentence)

        return res

    def rules(self, sentence, cut_list):
        self.text = sentence
        if not self.text:
            return cut_list
        
        # 如果为对话 则切分
        if self.text[0] == "“":
            couple_index = self.text.find("”")
            # 如果匹配到
            if couple_index != -1:
                if self.text[couple_index-1] in self.end_operator:
                    cut_list.append(self.text[:couple_index+1])
                    # 继续切分余下的句子
                    text = self.text[couple_index+1:]
                    return self.rules(text, cut_list)
                else:
                    end_operator = re.search("|".join(self.end_operator), self.text)
                    if end_operator:
                        end_operator_index = self.text.index(end_operator.group())
                        if "“" not in self.text[couple_index:end_operator_index]:
                            cut_list.append(self.text[:end_operator_index+1])
                            # 继续切分余下的句子
                            text = self.text[end_operator_index+1:]
                            return self.rules(text, cut_list)
                        else:
                            couple_index_2 = self.text[couple_index+1:].find("”")
                            if couple_index_2 != -1:
                                couple_index_2 = couple_index_2 + couple_index+1
                                if couple_index_2 == len(self.text) - 1:
                                    cut_list.append(self.text)
                                    return cut_list
                                elif self.text[couple_index_2 - 1] in self.end_operator:
                                    cut_list.append(self.text[:couple_index_2 + 1])
                                    text = self.text[couple_index_2 + 1:]
                                    return self.rules(text, cut_list)
                                elif self.text[couple_index_2 + 1] in self.end_operator:
                                    cut_list.append(self.text[:couple_index_2 + 2])
                                    text = self.text[couple_index_2 + 2:]
                                    return self.rules(text, cut_list)
                                else:
                                    cut_list.append(self.text)
                                    return cut_list
                    else:
                        cut_list.append(self.text)
                        return cut_list
            else:
                cut_list.append(self.text)
                return cut_list
                
        else:
            end_operator = re.search("|".join(self.end_operator), self.text)
            if end_operator:
                end_operator_index = self.text.index(end_operator.group())
                # xxxxxxx。
                if "“" not in self.text[:end_operator_index] or \
                        ("“" in self.text[:end_operator_index] and "”" in self.text[:end_operator_index]):
                    if end_operator.group() == "……":
                        end_operator_index += 1

                    if "”" in self.text[end_operator_index+1:]:
                        couple_index = self.text[end_operator_index+1:].find("”") + end_operator_index + 1
                        if couple_index == len(self.text) - 1:
                            cut_list.append(self.text)
                            return cut_list
                        elif self.text[couple_index-1] in self.end_operator:
                            cut_list.append(self.text[:couple_index+1])
                            text = self.text[couple_index+1:]
                            return self.rules(text, cut_list)
                        else:
                            cut_list.append(self.text[:end_operator_index + 1])
                            # 继续切分余下的句子
                            text = self.text[end_operator_index + 1:]
                            return self.rules(text, cut_list)
                    else:
                        cut_list.append(self.text[:end_operator_index+1])
                        # 继续切分余下的句子
                        text = self.text[end_operator_index+1:]
                        return self.rules(text, cut_list)
                # “xxxxxx。xxxx”
                else:
                    couple_index = self.text.find("”")
                    # 如果引号在句子末尾直接返回， 不再切割
                    if couple_index == len(self.text) - 1:
                        cut_list.append(self.text)
                        return cut_list
                    elif couple_index != -1:
                        if self.text[couple_index-1] in self.end_operator:
                            cut_list.append(self.text[:couple_index+1])
                            # 继续切分余下的句子
                            text = self.text[couple_index+1:]
                            return self.rules(text, cut_list)
                        elif self.text[couple_index+1] in self.end_operator:
                            cut_list.append(self.text[:couple_index+2])
                            # 继续切分余下的句子
                            text = self.text[couple_index+2:]
                            return self.rules(text, cut_list)
                        else:
                            cut_list.append(self.text)
                            return cut_list
                    else:
                        cut_list.append(self.text)
                        return cut_list
            else:
                cut_list.append(self.text)
                return cut_list

def remove_unused_abstract(c, answer_split, prob, threshold):
    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)
    rouge = Rouge()

    whether_remove = True
    for cc in c:
        cc_new = ' '.join(cc.split())
        if len(remove_punc(cc)) == 0:
            continue
        for ans in answer_split:
            try:
                if rouge.get_scores(cc_new, ' '.join(ans.split()), avg=True)["rouge-l"]["f"] > threshold:
                    whether_remove = False
                    break
            except:
                print(c)
                print(cc_new)
        if whether_remove == False:
            break
    if random.random() > prob and whether_remove:
        return True
    else:
        return False

def create_data(data_type, data_path, augmented_data_part):
    
    raw_data = []
    for d in json.load(open("{}/{}.json".format(data_path, data_type), 'r'))['data']:
        context = []
        digests = d["digests"]
        answer = d["answer"]
        question = d["question"]
        for dig in digests:
            dig = dig["datas"]
            context_part = []
            for chunk in dig:
                context_part.append(chunk["desc"])
            context.append("".join(context_part))

        raw_data.append({
            "context": context,
            "question": question,
            "answer": answer,
            "data_type": "type1",
        })
    
    for d in augmented_data_part:
        d["data_type"] = "type2"
        raw_data.append(d)
    
    
    coarsegrained_splitter = SentenceSplitter(["。", "？", "！"])
    finegrained_splitter = SentenceSplitter(["。", "？", "！", "；", ';', "：", ":", "~", "……", "…", "，", "、", ","])

    def dump_file(file_name, type, raw_data):
        with open(file_name, 'w') as fout:
            src_length = []
            tgt_length = []
            for i, line in enumerate(raw_data):
                question = line["question"]
                context = line["context"]
                data_type = line["data_type"]
                # print(context)
                # print(line["answer"])
                if type == "train" and data_type == "type1":
                    cut_answer = coarsegrained_splitter.cut(line["answer"])
                    new_context = [c for c in context if not remove_unused_abstract(coarsegrained_splitter.cut(c), cut_answer, 0, 0.3)]
                    if len(new_context) != 0:
                        context = new_context
                    
                    # whether to add an irrelevant fact
                    # if random.random() > 0.85:
                    #     noise_context = raw_data[int(random.random() * len(raw_data)) - 1]["context"]
                    #     if len(noise_context) > 0:
                    #         noise_context = random.choice(noise_context)
                    #         if noise_context is not []:
                    #             context.insert(random.randint(0,len(context)), noise_context)

                    new_context = []
                    for c in context:
                        c = [cc for cc in coarsegrained_splitter.cut(c)]
                        
                        def remove_prob(c, prob, split_model):
                            for id, cc in enumerate(c):
                                new_c = []
                                for ccc in split_model.cut(cc):
                                    if random.random() > prob:
                                        new_c.append(ccc)
                                new_c = "".join(new_c)
                                if len(new_c) != 0:
                                    c[id] = new_c
                            return c

                        c = remove_prob(c, 0.25, finegrained_splitter)
                        
                        if random.random() > 0.8:
                            if random.random() > 0.5:
                                new_context.append("".join(c[: int(len(c) / 2)]))
                                new_context[int(random.random() * len(new_context))-1] += "".join(c[int(len(c) / 2): ])
                            else:
                                new_context.append("".join(c[int(len(c) / 2): ]))
                                new_context[int(random.random() * len(new_context))-1] += "".join(c[: int(len(c) / 2)])
                        else:
                            new_context.append("".join(c))
                        
                    context = new_context
                    
                    shuffle_idx = [i for i in range(len(context))]
                    if random.random() > 0.85:
                        random.shuffle(shuffle_idx)
                    context = [context[shuffle_idx[i]] for i in range(len(shuffle_idx))]
                    
                new_context = ""
                for c in context:
                    if len(c) == 0:
                        continue
                    new_context += "摘要：" + c + "；"
                context = new_context
                context = re.sub('<', '<<', context)
                answer = line["answer"]
                # print(new_context)
                # print('\n')
                # input()
                
                if data_type == "type1":
                    answer = re.sub(r'(【1】|【2】|【3】|【4】|【5】|【6】|【7】|【8】|【9】|【10】|【11】|【12】|【13】|【14】|【15】|【16】|【17】|【18】|【19】|【20】|<1>|<2>|<3>|<4>|<5>|<6>|<7>|<8>|<9>|<10>|<11>)', '', answer)
                answer = re.sub('<', '<<', answer)
                question = re.sub('<', '<<', question)
                src_line = context + "问题：" + question + "；答案："
                tgt_line = answer
                src_line = src_line.strip()
                tgt_line = tgt_line.strip()
                src_length.append(len(src_line))
                tgt_length.append(len(tgt_line))
                fout.write(json.dumps({'source': src_line, '<ans>': tgt_line}, ensure_ascii=False) + '\n')
            print(np.mean(src_length))
            print(np.mean(tgt_length))

    dump_file('{}_synthesis.txt'.format(data_type), data_type, raw_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default="../../data/interactive_data")
    parser.add_argument('--augment_qa_data', default=False, action='store_true', help="whether to augment the synthesis data")
    parser.add_argument('--augment_data_path', type=str, default="../../data/pipeline_data")

    args = parser.parse_args()

    if args.augment_qa_data:
        def load_data(path):
            data = []
            with open(path) as fin:
                lines = fin.readlines()
                for line in lines:
                    line_new = json.loads(line.strip())
                    line_new["context"] = line_new["abstracts"]
                    data.append(line_new)
            return data

        augmented_data = load_data(os.path.join(args.augment_data_path, "answer_20000.json"))
        random.shuffle(augmented_data)
    else:
        augmented_data = []

    for data_type in ["train", "dev", "test"]:
        if data_type == "train":
            augmented_data_part = augmented_data[: int(len(augmented_data) * 0.9)]
        elif data_type == "dev":
            augmented_data_part = augmented_data[int(len(augmented_data) * 0.9): int(len(augmented_data) * 0.95)]
        elif data_type == "test":
            augmented_data_part = augmented_data[int(len(augmented_data) * 0.95): ]

        create_data(data_type, args.data_path, augmented_data_part)