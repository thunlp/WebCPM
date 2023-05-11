import json
from sklearn.metrics import f1_score, precision_score, recall_score
from rouge import Rouge
import numpy as np
import jieba
import string

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str, required=True)
parser.add_argument('--evaluate_action', default=False, action='store_true')
parser.add_argument('--evaluate_query', default=False, action='store_true')
parser.add_argument('--evaluate_abstract', default=False, action='store_true')
parser.add_argument('--abstract_all_tokens', default=False, action='store_true')
parser.add_argument('--evaluate_answer', default=False, action='store_true')
args = parser.parse_args()

def get_rouge_over_list(prediction, groundtruth):
    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)
    if len(remove_punc(prediction)) == 0:
        return 0.0
    rouge = Rouge()
    if type(groundtruth)==list:
        if len(groundtruth)==0:
            return 0
        return np.max([rouge.get_scores(prediction, gt, avg=True)["rouge-l"]["f"] for gt in groundtruth])
    prediction = ' '.join(jieba.cut(prediction,use_paddle=True))
    groundtruth = ' '.join(jieba.cut(groundtruth,use_paddle=True))
    return rouge.get_scores(prediction, groundtruth, avg=True)["rouge-l"]["f"]

if __name__ == "__main__":
    target_list = []
    pred_list = []
    f = open(args.input_file, 'r', encoding='utf-8')
    lines = f.readlines()
    results = [json.loads(line) for line in lines]

    if args.evaluate_action:
        actions = ['下翻', '上翻', '返回', '新增摘要', '合并摘要', '一号页面', '二号页面', '三号页面', '结束', '搜索', '开始', '拒答', '至顶']
        action2id = {a: idx for idx, a in enumerate(actions)}

        not_in = 0
        for result in results:
            instance = result['instance']
            source = instance[0]['source']
            target = result['answer']
            decoded = result['decode_tokens']
            if decoded not in action2id:
                not_in += 1
            else:
                # we do not include these three actions in evaluation, they take up minimal proportion and can be neglected
                # TODO: remove these actions during training
                if decoded in ['开始', '拒答', '至顶'] or target in ['开始', '拒答', '至顶']:
                    continue
                # support the multi-task setting, where the inference file could contain supporting fact extraction and query generation
                if target not in actions:
                    continue
                
                pred_list += [action2id[decoded]]
                target_list += [action2id[target]]

        print(len(results))
        print(not_in)
        print(float(not_in) / len(results))

        macro_f1 = f1_score(target_list, pred_list, average='macro')
        micro_f1 = f1_score(target_list, pred_list, average='micro')
        all_f1 = f1_score(target_list, pred_list, average=None).tolist()
        all_f1 = {actions[idx]: v for idx, v in enumerate(all_f1)}
        macro_precision = precision_score(target_list, pred_list, average='macro')
        micro_precision = precision_score(target_list, pred_list, average='micro')
        macro_recall = recall_score(target_list, pred_list, average='macro')
        micro_recall = recall_score(target_list, pred_list, average='micro')

        print({'micro_f1': micro_f1, 'macro_f1': macro_f1, 'micro_precision': micro_precision, 'macro_precision': macro_precision, 'micro_recall': micro_recall, 'macro_recall': macro_recall})

        print(all_f1)

    elif args.evaluate_query:
        rouges = []
        for result in results:
            instance = result['instance']
            source = instance[0]['source']
            target = result['answer']
            decoded = result['decode_tokens']
            # support the multi-task setting, where the inference file could contain action prediction and supporting fact extraction
            if len(target) == 0 or not source.endswith("请生成新的合适的查询语句："):
                continue
            r = get_rouge_over_list(decoded, target)
            rouges.append(r)
        print('target rouge {}'.format(np.mean(rouges)))

    elif args.evaluate_answer:
        def get_ngram(text, n):
            ngram_list = []
            for i in range(len(text)-n+1):
                ngram_list.append(text[i: i+n])
            return list(set(ngram_list))

        def get_novelty(source, target, n):
            ngram_source = get_ngram(source, n)
            ngram_target = get_ngram(target, n)
            return float(len([x for x in ngram_target if x not in ngram_source])) / len(ngram_target)
        
        rouges = [] 
        original = []
        length = []
        for result in results:
            instance = result['instance'][0]
            source = instance['source']
            decode_tokens = instance['<ans>']
            r = get_rouge_over_list(decode_tokens, result['answer'])
            rouges.append(r)
            original_2gram = get_novelty(source, decode_tokens, 2)
            original_3gram = get_novelty(source, decode_tokens, 3)
            original_4gram = get_novelty(source, decode_tokens, 4)
            original_overall = (original_2gram + original_3gram + original_4gram) / 3
            original.append(original_overall)
            length.append(len(decode_tokens))

        print("rouge score: {}".format(np.mean(rouges)))
        print("original score: {}".format(np.mean(original)))
        print("length score: {}".format(np.mean(length)))

    elif args.evaluate_abstract:
        if args.abstract_all_tokens:
            rouges = []
            for result in results:
                instance = result['instance']
                source = instance[0]['source']
                target = result['answer']
                decoded = result['decode_tokens']
                # support the multi-task setting, where the inference file could contain action prediction and query generation
                if len(target) == 0 or not source.endswith("请对当前界面内容摘取和问题相关的内容："):
                    continue
                r = get_rouge_over_list(decoded, target)
                rouges.append(r)
            print('target rouge {}'.format(np.mean(rouges)))
        else:
            # TODO: add evaluation for predicting only the start and end tokens, will add soon
            raise NotImplementedError