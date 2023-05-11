import json
import re
from tokenizer import CPM3Tokenizer
from cpm_live.dataset import build_dataset
import os
import argparse
import random

class WebGPT_Dataset:
    def __init__(self, path, split, add_query, add_abstract, abstract_all_tokens, add_action):
        path = f"{path}/{split}.json"
        self.add_query = add_query
        self.add_abstract = add_abstract
        self.abstract_all_tokens = abstract_all_tokens
        self.add_action = add_action

        self.tokenizer = CPM3Tokenizer("vocab_new.txt")

        self.action2idx = {'TRIGGER_SCROLL_DOWN': 'A：下翻', 'TRIGGER_SCROLL_UP': 'B：上翻', 'PAGE_GO_BACK': 'C：返回', 'ADD_DIGEST': 'D：新增摘要', 'MERGE_DIGEST': 'E：合并摘要', 'LOAD_PAGE_DETAIL-0': 'F：一号页面', 'LOAD_PAGE_DETAIL-1': 'G：二号页面', 'LOAD_PAGE_DETAIL-2': 'H：三号页面', 'RECORD_CLOSE': 'I：结束', 'PRESS_SEARCH': 'J：搜索', 'RECORD_START': 'K：开始', 'RECORD_REJECT': 'L：拒答', 'TRIGGER_SCROLL_TO_TOP': 'M：至顶'}

        self.action2idx = {k: v[2: ] for k,v in self.action2idx.items()}
        self.action_start2idx = {k: v for k,v in self.action2idx.items()}

        self.id2action_start = {v[0]: k for k,v in self.action_start2idx.items()}
        self.action_verbalizer = [self.action_start2idx[k][0] for k in self.action_start2idx]
        self.action_target = {v: idx for idx,v in enumerate(self.action_verbalizer)}
        self.action_ban2idx = {k: idx for idx, k in enumerate(list(self.action2idx.keys()))}

        self.action_num = {}

        self.idx = 0
        self.data = []
        for idx, item in enumerate(json.load(open(path, "r", encoding='utf-8'))["data"]):
            all_actions = item["actions"]
            in_page = False

            def get_view(content):
                prev_link = {}
                next_view = ""
                prev_titles = []
                all_titles = []
                for idx, view in enumerate(content):
                    all_titles.append(view["title"])
                    encode_content = "标题：" + view["title"] + "；简介：" + view["summary"]
                    if idx != len(content) - 1:
                        encode_content += "\n"
                    next_view += self.action2idx['LOAD_PAGE_DETAIL-' + str(idx)] + encode_content
                    prev_link[view["href"]] = idx
                    prev_titles.append(view["title"])
                return prev_link, next_view, prev_titles, all_titles

            def get_next_quote(digests):
                next_quote = ""
                for quote_num, quotes in enumerate(digests):
                    quote_tmp = ""
                    for quote in quotes:
                        quote_tmp += quote["desc"]
                    tokenized_quote = self.tokenizer.encode(quote_tmp)
                    if len(tokenized_quote) <= 50:
                        next_quote += "摘要" + str(quote_num) + "：" + quote_tmp
                    else:
                        next_quote += "摘要" + str(quote_num) + "：" + self.tokenizer.decode(tokenized_quote[: 25]) + "..." + self.tokenizer.decode(tokenized_quote[-25: ])
                    if quote_num != len(digests) - 1:
                        next_quote += "\n"
                return next_quote

            info_dict = {"question": item["question"], "quotes": [], "past_actions": [], "title": [], "text": [], "actions_left": 100, "next_action": [], "feasible_state": None, "past_view": [], "cur_all_titles": []}
            next_view, past_view, next_title, next_quote, past_action, prev_titles, next_feasible_state = [], [], [], [], [], [], [1 for _ in range(len(self.action_target))]

            cur_all_titles = []
            for action in all_actions:
                action_name = action["action"]
                if action_name == "LOAD_PAGE_DETAIL":
                    act_name = 'LOAD_PAGE_DETAIL-' + str(prev_link[action["details"]["href"]])
                else:
                    act_name = action_name
                if act_name not in self.action_num:
                    self.action_num[act_name] = 0
                self.action_num[act_name] += 1

                info_dict["past_actions"].append(past_action)
                info_dict["title"] = next_title
                info_dict["text"] = next_view
                info_dict["past_view"] = past_view
                info_dict["quotes"] = next_quote
                info_dict["feasible_state"] = next_feasible_state
                past_view = info_dict["text"]

                if action_name == "RECORD_START":
                    info_dict["next_action"] = self.action_start2idx[action_name]
                    past_action = self.action2idx["RECORD_START"] + "；"
                    banned_actions = ['RECORD_START', 'RECORD_CLOSE', 'LOAD_PAGE_DETAIL-0', 'ADD_DIGEST', 'TRIGGER_SCROLL_DOWN', 'PAGE_GO_BACK', 'LOAD_PAGE_DETAIL-2', 'LOAD_PAGE_DETAIL-1', 'TRIGGER_SCROLL_UP', 'MERGE_DIGEST', 'TRIGGER_SCROLL_TO_TOP']
                    next_feasible_state = self.ban_action(banned_actions)
                    continue
                elif action_name == "PRESS_SEARCH":
                    search_query = action["details"]["keyword"]
                    prev_link, next_view, prev_titles, all_titles = get_view(action["pageContentInViewport"])
                    for title in all_titles:
                        if title not in cur_all_titles:
                            cur_all_titles.append(title)

                    info_dict["next_action"] = [self.action_start2idx[action_name], search_query]

                    next_title = search_query
                    past_action = self.action2idx["PRESS_SEARCH"] + search_query + "；"
                    in_page = False
                    banned_actions = ['RECORD_START', 'ADD_DIGEST', 'TRIGGER_SCROLL_UP', 'MERGE_DIGEST', 'TRIGGER_SCROLL_TO_TOP']
                    next_feasible_state = self.ban_action(banned_actions)
                elif action_name == "LOAD_PAGE_DETAIL":
                    info_dict["next_action"] = self.action_start2idx['LOAD_PAGE_DETAIL-' + str(prev_link[action["details"]["href"]])]
                    next_view = action["pageContentInViewport"]

                    past_action = self.action2idx['LOAD_PAGE_DETAIL-' + str(prev_link[action["details"]["href"]])] + prev_titles[prev_link[action["details"]["href"]]] + "；"
                    assert in_page == False
                    in_page = True
                    banned_actions = ['RECORD_START', 'LOAD_PAGE_DETAIL-0', 'LOAD_PAGE_DETAIL-2', 'LOAD_PAGE_DETAIL-1', 'TRIGGER_SCROLL_UP', 'MERGE_DIGEST', 'TRIGGER_SCROLL_TO_TOP']
                    next_feasible_state = self.ban_action(banned_actions)
                elif action_name == "ADD_DIGEST":
                    abstract = action["details"]["text"]
                    decoded_abstract = self.tokenizer.encode(abstract)
                    num_start_end_tokens = 10
                    if not self.abstract_all_tokens:
                        abstract = "起始字符：" + self.tokenizer.decode(decoded_abstract[: num_start_end_tokens]) + "-结束字符：" + self.tokenizer.decode(decoded_abstract[-num_start_end_tokens: ])
                    info_dict["next_action"] = [self.action_start2idx[action_name], abstract]

                    next_quote = get_next_quote(action["digests"])
                    past_action = self.action2idx["ADD_DIGEST"] + "；" + self.tokenizer.decode(decoded_abstract[: num_start_end_tokens]) + "***" + self.tokenizer.decode(decoded_abstract[-num_start_end_tokens: ]) + "；"
                    assert in_page == True
                    banned_actions = ['RECORD_START', 'LOAD_PAGE_DETAIL-0', 'LOAD_PAGE_DETAIL-2', 'LOAD_PAGE_DETAIL-1']
                    next_feasible_state = self.ban_action(banned_actions)
                elif action_name == "TRIGGER_SCROLL_DOWN":
                    info_dict["next_action"] = self.action_start2idx[action_name]
                    if in_page:
                        next_view = action["pageContentInViewport"]
                    else:
                        prev_link, next_view, prev_titles, all_titles = get_view(action["pageContentInViewport"])
                        for title in all_titles:
                            if title not in cur_all_titles:
                                cur_all_titles.append(title)
                    past_action = self.action2idx["TRIGGER_SCROLL_DOWN"] + "；"
                    if in_page:
                        banned_actions = ['RECORD_START', 'LOAD_PAGE_DETAIL-0', 'LOAD_PAGE_DETAIL-2', 'LOAD_PAGE_DETAIL-1']
                    else:
                        # should ban MERGE_DIGEST, fix later
                        banned_actions = ['RECORD_START', 'ADD_DIGEST']
                    next_feasible_state = self.ban_action(banned_actions)
                elif action_name == "TRIGGER_SCROLL_UP":
                    info_dict["next_action"] = self.action_start2idx[action_name]
                    if in_page:
                        next_view = action["pageContentInViewport"]
                    else:
                        prev_link, next_view, prev_titles, all_titles = get_view(action["pageContentInViewport"])
                        for title in all_titles:
                            if title not in cur_all_titles:
                                cur_all_titles.append(title)
                    past_action = self.action2idx["TRIGGER_SCROLL_UP"] + "；"
                    if in_page:
                        banned_actions = ['RECORD_START', 'LOAD_PAGE_DETAIL-0', 'LOAD_PAGE_DETAIL-2', 'LOAD_PAGE_DETAIL-1']
                    else:
                        banned_actions = ['RECORD_START', 'ADD_DIGEST', 'MERGE_DIGEST']
                    next_feasible_state = self.ban_action(banned_actions)
                elif action_name == "MERGE_DIGEST":
                    info_dict["next_action"] = self.action_start2idx[action_name]
                    next_quote = get_next_quote(action["digests"])
                    past_action = self.action2idx["MERGE_DIGEST"] + "；"
                    # assert in_page == True
                    # should ban LOAD_PAGE, fix later
                    # banned_actions = ['RECORD_START', 'LOAD_PAGE_DETAIL-0', 'LOAD_PAGE_DETAIL-2', 'LOAD_PAGE_DETAIL-1']
                    banned_actions = ['RECORD_START']
                    next_feasible_state = self.ban_action(banned_actions)
                elif action_name == "PAGE_GO_BACK":
                    if "pageContentInViewport" in action:
                        prev_link, next_view, prev_titles, all_titles = get_view(action["pageContentInViewport"])
                        for title in all_titles:
                            if title not in cur_all_titles:
                                cur_all_titles.append(title)
                    info_dict["next_action"] = self.action_start2idx[action_name]
                    past_action = self.action2idx["PAGE_GO_BACK"] + "；"
                    in_page = False
                    banned_actions = ['RECORD_START', 'ADD_DIGEST', 'MERGE_DIGEST']
                    next_feasible_state = self.ban_action(banned_actions)
                elif action_name == "RECORD_CLOSE":
                    info_dict["next_action"] = self.action_start2idx[action_name]
                    past_action = self.action2idx["RECORD_CLOSE"] + "；"
                elif action_name == "TRIGGER_SCROLL_TO_TOP":
                    info_dict["next_action"] = self.action_start2idx[action_name]
                    if in_page:
                        next_view = action["pageContentInViewport"]
                    else:
                        prev_link, next_view, prev_titles, all_titles = get_view(action["pageContentInViewport"])
                        for title in all_titles:
                            if title not in cur_all_titles:
                                cur_all_titles.append(title)
                    past_action = self.action2idx["TRIGGER_SCROLL_UP"] + "；"
                    if in_page:
                        banned_actions = ['RECORD_START', 'LOAD_PAGE_DETAIL-0', 'LOAD_PAGE_DETAIL-2', 'LOAD_PAGE_DETAIL-1']
                    else:
                        banned_actions = ['RECORD_START', 'ADD_DIGEST', 'MERGE_DIGEST']
                    next_feasible_state = self.ban_action(banned_actions)
                else:
                    print("wrong action name, plz check here!")
                    print(action_name)
                
                info_dict['cur_all_titles'] = ""  
                for title in cur_all_titles:
                    info_dict['cur_all_titles'] += title + '\n'

                if action_name == "PRESS_SEARCH":
                    act = info_dict["next_action"][0]
                    search_query = info_dict["next_action"][1]
                    if self.add_query:
                        info_dict["next_action"] = search_query
                        context_ids, next_action = self.make_input(info_dict, type="query")
                        self.data.append([context_ids, next_action])
                        self.idx += 1
                    if self.add_action:
                        info_dict["next_action"] = act
                        context_ids, next_action = self.make_input(info_dict, type="action")
                        self.data.append([context_ids, next_action])
                        self.idx += 1
                elif action_name == "ADD_DIGEST":
                    act = info_dict["next_action"][0]
                    abstract = info_dict["next_action"][1]
                    if self.add_abstract:
                        info_dict["next_action"] = abstract
                        context_ids, next_action = self.make_input(info_dict, type="abstract")
                        self.data.append([context_ids, next_action])
                        self.idx += 1
                    if self.add_action:
                        info_dict["next_action"] = act
                        context_ids, next_action = self.make_input(info_dict, type="action")
                        self.data.append([context_ids, next_action])
                        self.idx += 1
                elif self.add_action:
                    context_ids, next_action = self.make_input(info_dict, type="action")
                    self.data.append([context_ids, next_action])
                    self.idx += 1
                
                info_dict["actions_left"] -= 1
        print(self.action_num)
        with open('{}_search.txt'.format(split), 'w') as fout:
            for item in self.data:
                src_line = item[0]
                tgt_line = item[1]
                src_line = src_line.strip()
                tgt_line = tgt_line.strip()
                src_line = src_line.replace(" ", "")
                tgt_line = tgt_line.replace(" ", "")
                # replacing `<` with `<<` is required in the tokenization process of CPMB model.
                src_line = re.sub('<', '<<', src_line)
                tgt_line = re.sub('<', '<<', tgt_line)
                fout.write(json.dumps({'source': src_line, '<ans>': tgt_line}, ensure_ascii=False) + '\n')

        fin = open('{}_search.txt'.format(split), 'r', encoding='utf-8')
        lines = fin.readlines()
        fin.close()

        if args.add_synthesis:
            # You should first execute make_data_synthesis_model.py to obtain the txt files needed for answer synthesis.
            print("adding data from the synthesis model")
            fin = open('{}_synthesis.txt'.format(split), 'r', encoding='utf-8')
            lines += fin.readlines()
            fin.close()
        random.shuffle(lines)

        write_path = "./{}_data".format(split)
        if not os.path.exists(write_path):
            os.makedirs(write_path)

        # the write_path directory should contain no files
        with build_dataset(write_path, "data") as dataset:
            for data in lines:
                data = json.loads(data)
                dataset.write(data)


    def make_input(self, info_dict, type="action"):
        context_ids = ""
        def convert_nothing(info):
            return "无" if len(info) == 0 else info

        context_ids += "问题：\n" + info_dict["question"] + "\n"
        context_ids += "摘要：\n" + convert_nothing(info_dict["quotes"]) + "\n"

        last_few_actions = ""
        for past_action in info_dict["past_actions"]:
            if past_action != []:
                last_few_actions += past_action
                
        context_ids += "当前搜索：\n" + convert_nothing(info_dict["title"]) + "\n"
        context_ids += "上回界面：\n" + convert_nothing(info_dict["past_view"]) + "\n"
        context_ids += "当前界面：\n" + convert_nothing(info_dict["text"]) + "\n"

        context_ids += "剩余操作步数：" + str(info_dict["actions_left"]) + "\n"
        
        if type == "action":
            context_ids += "可选操作："
            for idx, k in enumerate(self.action2idx):
                context_ids += self.action2idx[k]
                if idx != len(self.action2idx) - 1:
                    context_ids += "；"
            context_ids += "\n"
        
        context_ids += "历史操作：" + convert_nothing(last_few_actions) + "\n"
        
        if type == "action":
            context_ids += "下一步操作："
        elif type == "query":
            context_ids += "请生成新的合适的查询语句："
        elif type == "abstract":
            context_ids += "请对当前界面内容摘取和问题相关的内容："

        next_action = info_dict["next_action"]

        # print(context_ids)
        # print(next_action)
        # input()

        return context_ids, next_action

    def ban_action(self, banned_actions):
        tmp = [1 for _ in range(len(self.action_target))]
        for action in banned_actions:
            tmp[self.action_ban2idx[action]] = 0
        return tmp

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default="../../data/interactive_data")
    parser.add_argument('--add_query', default=False, action='store_true', help="if True, will only generate query generation data")
    parser.add_argument('--add_abstract', default=False, action='store_true', help="if True, will only generate supporting fact extraction data")
    parser.add_argument('--abstract_all_tokens', default=False, action='store_true', help="if True, supporting fact extraction module will generate all the tokens, instead of only the first / last few tokens")
    parser.add_argument('--add_action', default=False, action='store_true', help="if True, will generate action prediction data")
    parser.add_argument('--add_synthesis', default=False, action='store_true', help="if True, will load local data for the synthesis model")

    args = parser.parse_args()

    # put your data at args.data_path
    for data_type in ["train", "dev", "test"]:
        _ = WebGPT_Dataset(args.data_path, data_type, add_query = args.add_query, add_abstract = args.add_abstract, abstract_all_tokens = args.abstract_all_tokens, add_action=args.add_action)