# -*- coding: utf-8 -*-

import time
import torch
import traceback
from interaction import platformctrl_interactive
import json
import re
import time
from training.dataset_interactive.make_data_search_model import WebGPT_Dataset
from cpm_live.generation.bee import CPMBeeGenerationWithBan, CPMBeeBeamSearch
from cpm_live.models import CPMBeeTorch, CPMBeeConfig
from cpm_live.tokenizers import CPMBeeTokenizer
import argparse

def model_predict_cpmb(question, label2logit, inference_json, modelcpmb, tokenizer):
    op = platformctrl_interactive.Operator()
    op.execute(platformctrl_interactive.Operation.START)

    past_href = None
    in_page = False
    last_page = None
    ban_down = False
    ban_up = False
    ban_abstract = False
    ban_search = False
    ban_finish = False
    ban_go_back = False
    asked_questions = [] # asked questions 每次搜索还是有重复的问题

    continue_down = 0
    now_loads = 0 
    now_digs = 0 
    continue_searchs = 0 
    beam_size = 3

    # max lenght 4096, avoid memory overflow
    MEMORY_OVERFLOW_LENGTH=3072

    action2id = {'下翻': 0, '上翻': 1, '返回': 2, '新增摘要': 3, '合并摘要': 4, '一号页面': 5, '二号页面': 6, '三号页面': 7, '结束': 8, '搜索': 9, '开始': 10, '拒答': 11, '至顶': 12}

    with torch.inference_mode(): 
        now_time = time.time()

        beam_search = CPMBeeBeamSearch(
            model=modelcpmb,
            tokenizer=tokenizer,
        )
        step_id = -1
        while True:
            step_id += 1
            if step_id >= 100:
                print("max step reached, exit.")
                break

            time.sleep(1)
            print('the current step: %d, now time consumed for the last step: %f' % (step_id, time.time() - now_time))
            now_time = time.time()
            inference_dataset = WebGPT_Dataset("intermediate_file", "test", add_query = False, add_abstract = False, abstract_all_tokens = True, add_action=True, write_file=False)
            src_line = inference_dataset.data[-1][0]
            feasible_state = torch.tensor([inference_dataset.data[-1][-1]])
            src_line = src_line.strip()
            src_line = src_line.replace(" ", "")
            src_line = re.sub('<', '<<', src_line)
            instance = [{'source': src_line, '<ans>': ""}]

            gen = CPMBeeGenerationWithBan(
                    model=modelcpmb,
                    tokenizer=tokenizer,
                    feasible_state=feasible_state,
                    ban_down=ban_down,
                    ban_abstract=ban_abstract,
                    ban_up=ban_up,
                    ban_search=ban_search,
                    ban_finish=ban_finish,
                    ban_go_back=ban_go_back,
                    label2logit=label2logit,
                    step_id=step_id
            )

            if ban_abstract:
                ban_abstract = False
            if ban_search:
                ban_search = False
            if ban_finish:
                ban_finish = False
            if ban_down:
                ban_down = False
            if ban_up:
                ban_up = False
            if ban_go_back:
                ban_go_back = False
            
            '''top_p = CPMBeeRandomSampling(
                    model=modelcpmb,
                    tokenizer=tokenizer,
            )
            inference_results = top_p.generate(instance, repetition_penalty=1.2)[0]
            print('without ban:',inference_results)'''
            
            inference_results = gen.generate(instance, max_length=512, repetition_penalty=1.2)[0]
            print("new action")
            print(src_line)
            print(inference_results['<ans>'])
            input()
            if inference_results['<ans>'] not in action2id:
                print("action不在预定义的action中，改成结束")
                inference_results['<ans>'] = '结束'
            next_action_id = action2id[inference_results['<ans>']]

            # The following constraints are manually defined rules, which can stablize the search process. You can also change it to your personalized rules.
            if step_id > 10 and now_loads < 2 and next_action_id == 8:
                print("Trigger a rule: if only one load page is executed, do not terminate it so early, reselecting a new action")
                digests = op.get_digests()
                abstract_num = 0
                for dig in digests:
                    abstract_num += len(dig)
                if abstract_num <= 3:
                    ban_finish = True
                    continue
            elif next_action_id == 0 and continue_down >= 3: # do not allow to scroll down more than 3 times consequtively
                ban_down = True
                last_page = current_page
                continue
            elif next_action_id == 9 and continue_searchs >= 4: # do not allow to search more than 4 times if no page is loaded
                ban_search = True
                last_page = current_page
                continue

            # illegal judgement
            if in_page == False and next_action_id == 2:
                print("error: trying to go back to the previous page, but the current page is the first page")
                ban_go_back = True
                continue
            if in_page == False and (last_page is not None): 
                if len(last_page) == 2 and next_action_id == 7:
                    print("the last page only has 2 pages, redirecting to the second page")
                    next_action_id = 6
                elif len(last_page) == 1 and next_action_id in [6, 7]:
                    print("the last page only has 1 page, redirecting to the first page")
                    next_action_id = 5
            if in_page == True and next_action_id in [5,6,7]:
                print("error: trying to load a new page, but the current mode is not the search mode")
                continue

            if next_action_id == 0:
                continue_down += 1
                action_name = "TRIGGER_SCROLL_DOWN"
                page_down_state = op.page_down()
                if page_down_state == False:
                    ban_down = True
                    last_page = current_page
                    continue

                if in_page:
                    current_page = op.get_page_detail()
                    action = {"action": action_name, "pageContentInViewport": current_page}
                else:
                    current_page = op.get_page_detail()
                    action = {"action": action_name, "pageContentInViewport": current_page}
                    past_href = [k["href"] for k in current_page]
            elif next_action_id == 1:
                continue_down = 0
                action_name = "TRIGGER_SCROLL_UP"
                
                page_up_state = op.page_up()
                if page_up_state == False:
                    ban_up = True
                    last_page = current_page
                    continue

                if in_page:
                    current_page = op.get_page_detail()
                    action = {"action": action_name, "pageContentInViewport": current_page}
                else:
                    current_page = op.get_page_detail()
                    action = {"action": action_name, "pageContentInViewport": current_page}
                    past_href = [k["href"] for k in current_page]
            elif next_action_id == 2:
                continue_down = 0
                action_name = "PAGE_GO_BACK"
                op.execute(platformctrl_interactive.Operation.GO_BACK)
                current_page = op.get_page_detail()
                action = {"action": action_name, "pageContentInViewport": current_page}
                past_href = [k["href"] for k in current_page]
                in_page = False
            elif next_action_id == 3:
                continue_down = 0
                action_name = "ADD_DIGEST"
                now_digs += 1

                # need to simplify
                action = {"action": action_name, "details": {"text": "no abstract"}, "digests": op.get_digests()}
                inference_json["data"][0]["actions"].insert(-1, action)
                json.dump(inference_json, open('intermediate_file/test.json', 'w', encoding='utf8'), ensure_ascii=False)
                inference_dataset = WebGPT_Dataset("intermediate_file", "test", add_query = False, add_abstract = True, abstract_all_tokens = True, add_action=False, write_file=False)
                src_line = inference_dataset.data[-1][0]
                feasible_state = torch.tensor([inference_dataset.data[-1][-1]])
                src_line = src_line.strip()
                src_line = src_line.replace(" ", "")
                src_line = re.sub('<', '<<', src_line)
                instance = [{'source': src_line, '<ans>': ""}]
                decode_abstract = beam_search.generate(instance, max_length=512, repetition_penalty=1.2, beam_size=beam_size)[0]["<ans>"]
                op.execute(platformctrl_interactive.Operation.ADD_DIGEST, decode_abstract)

                print("new abstract")
                print(src_line)
                print(decode_abstract)
                input()

                inference_json["data"][0]["actions"] = inference_json["data"][0]["actions"][: -2] + [inference_json["data"][0]["actions"][-1]]
                action = {"action": action_name, "details": {"text": decode_abstract}, "digests": op.get_digests()}
            elif next_action_id == 4:
                continue_down = 0
                action_name = "MERGE_DIGEST"
                op.merge([-2,-1])
                action = {"action": action_name, "digests": op.get_digests()}
            elif next_action_id in [5, 6, 7]:
                continue_down = 0
                now_loads += 1 
                continue_searchs = 0
                if next_action_id == 5:
                    op.execute(platformctrl_interactive.Operation.LOAD_PAGE_1)
                elif next_action_id == 6:
                    op.execute(platformctrl_interactive.Operation.LOAD_PAGE_2)
                elif next_action_id == 7:
                    op.execute(platformctrl_interactive.Operation.LOAD_PAGE_3)
                current_page = op.get_page_detail()
                action_name = "LOAD_PAGE_DETAIL"
                action = {"action": action_name, "pageContentInViewport": current_page, "details": {"href": past_href[next_action_id - 5]}}
                in_page = True
            elif next_action_id == 8:
                print("结束搜索决策，开始生成答案")
                break
            elif next_action_id == 9:
                continue_down = 0

                action_name = "PRESS_SEARCH"

                # if decode_query in asked_questions: # 若第二次搜索则可以用beam——search
                #     decode_query_beam_best = get_beam_query_cpm3('best')
                #     decode_query_beam_worst = get_beam_query_cpm3('worst')
                #     if decode_query_beam_best not in asked_questions:
                #         print('use best beam search')
                #         decode_query = decode_query_beam_best
                #     elif decode_query_beam_worst not in asked_questions:
                #         print('use worst beam search')
                #         decode_query = decode_query_beam_worst
                #     else:
                #         break # 实在没有就直接break掉
                
                # need to simplify
                action = {"action": action_name, "details": {"keyword": "no query", "result": []}, "pageContentInViewport": []}
                inference_json["data"][0]["actions"].insert(-1, action)
                json.dump(inference_json, open('intermediate_file/test.json', 'w', encoding='utf8'), ensure_ascii=False)
                inference_dataset = WebGPT_Dataset("intermediate_file", "test", add_query = True, add_abstract = False, abstract_all_tokens = True, add_action=False, write_file=False)
                src_line = inference_dataset.data[-1][0]
                feasible_state = torch.tensor([inference_dataset.data[-1][-1]])
                src_line = src_line.strip()
                src_line = src_line.replace(" ", "")
                src_line = re.sub('<', '<<', src_line)
                instance = [{'source': src_line, '<ans>': ""}]
                decode_query = beam_search.generate(instance, max_length=512, repetition_penalty=1.2, beam_size=beam_size)[0]["<ans>"]
                # remove \n in query, otherwise it will cause error in Bing
                decode_query = re.sub(r'\n', '', decode_query)

                print("new query")
                print(src_line)
                print(decode_query)
                input()

                continue_searchs += 1
                op.execute(platformctrl_interactive.Operation.SEARCH, decode_query)
                current_page = op.get_page_detail()
                inference_json["data"][0]["actions"] = inference_json["data"][0]["actions"][: -2] + [inference_json["data"][0]["actions"][-1]]
                action = {"action": action_name, "details": {"keyword": decode_query, "result": []}, "pageContentInViewport": current_page}
                past_href = [k["href"] for k in current_page]
                
                asked_questions.append(decode_query)
                in_page = False

            last_page = current_page
            inference_json["data"][0]["actions"].insert(-1, action)
            json.dump(inference_json, open('intermediate_file/test.json', 'w', encoding='utf8'), ensure_ascii=False)


        # Start QA
        Qa_time = time.time()
        new_context = ""
        total_length = 0

        digests = op.get_digests()
        abstracts = []
        for dig in digests:
            context_part = []
            for chunk in dig:
                context_part.append(chunk["desc"])
            abstracts.append("".join(context_part))

        for c in abstracts:
            if total_length >= MEMORY_OVERFLOW_LENGTH:
                break
            c_len = len(c)
            if total_length + c_len >= MEMORY_OVERFLOW_LENGTH:
                c = c[: MEMORY_OVERFLOW_LENGTH - total_length]
            total_length += c_len
            new_context += "摘要：" + c + "；"
        context = new_context
        src_line = context + "问题：" + question + "；答案："
        src_line = re.sub(' ', '', src_line)
        src_line = re.sub('<', '<<', src_line)
        instance = [
            {'source': src_line, '<ans>': ''},
        ]
        print(src_line)
        answer = beam_search.generate(instance, max_length=768, beam_size=3, repetition_penalty=1.2)[0]['<ans>']
        print('the question is:')
        print(question)
        print('the abstracts are:')
        print(abstracts)
        print('the answer is:')
        print(answer)
        print('the time QA is:%f' % (time.time() - Qa_time))
        op.end()
        return {'question': question, 'abstract': abstracts, 'answer': answer}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default="dump_prediction.json")
    parser.add_argument('--ckpt_path', type=str, default="../training/results/cpm_bee_510_multi4-epoch-2.pt")
    args = parser.parse_args()

    config = CPMBeeConfig.from_json_file("../cpm_live/config/cpm-bee-10b.json")
    tokenizer = CPMBeeTokenizer()
    modelcpmb = CPMBeeTorch(config=config)
    modelcpmb.load_state_dict(torch.load(args.ckpt_path))
    modelcpmb.cuda()

    all_actions = {'TRIGGER_SCROLL_DOWN': tokenizer.encode('下翻'), 'TRIGGER_SCROLL_UP': tokenizer.encode('上翻'), 'PAGE_GO_BACK': tokenizer.encode('返回'), 'ADD_DIGEST': tokenizer.encode('新增摘要'), 'MERGE_DIGEST': tokenizer.encode('合并摘要'), 'LOAD_PAGE_DETAIL-0': tokenizer.encode('一号页面'), 'LOAD_PAGE_DETAIL-1': tokenizer.encode('二号页面'), 'LOAD_PAGE_DETAIL-2': tokenizer.encode('三号页面'), 'RECORD_CLOSE': tokenizer.encode('结束'), 'PRESS_SEARCH': tokenizer.encode('搜索'), 'RECORD_START': tokenizer.encode('开始'), 'RECORD_REJECT': tokenizer.encode('拒答'), 'TRIGGER_SCROLL_TO_TOP': tokenizer.encode('至顶')}
    label2logit = torch.LongTensor([v[0][0] for k,v in all_actions.items()]).cuda()

    # torch.set_printoptions(profile="full")

    dump_list = []
    print("In the original paper, we use four modules for the whole framework, here we simplify it using a multi-task trained one. For each question, we call a search model to search for 3 times and merge the obtained abstracts after deduplication.")
    for question in ["张国荣为什么这么多年依然被铭记？", "为什么现在的房子卖不动？", "为什么中国不禁止人名重复？", "为什么有那么多人买小米呢？", "为什么河南饮食走不出去？", "为什么不建议买游戏本？", "为什么国内狗狗不能上公交地铁，国外却当作习以为常？", "为什么应届生的身份这么值钱？", "为什么说娶女教师不好？", "为什么电竞需要天赋极高？",  "什么是修心的最高境界?", "为什么新国标红绿灯存在大量争议？", "为什么央视不播日本动画了？", "为什么小公司留不住人?", "为什么现在都不看电视了？", "为什么闲鱼越做越差？", "为什么游泳馆不分男女？", "为什么中国神仙比较负责任？", "为什么中国人不用浴缸洗澡？", "为什么NBA在中国没有以前火了？", "为何中国的农民却赚不了多少钱？", "为什么 AlphaGo 不敢挑战麻将？"]:
        inference_json = {"data": [{'_id': 'test_001', 'actions': [{"action": "RECORD_START", "details": {}, "digests": [], "keyword": "", "triggerAt": 1650969909468, "stackLength": 0, "step": 0, "traceId": "718dd8557f9bf83d80468c954c88", "currentPageInfo": {"title": "", "type": "", "href": "", "scrollTop": 0}}, {"action": "RECORD_CLOSE", "details": {"digests": []}, "digests": [], "keyword": "", "triggerAt": 1650969912433, "stackLength": 0, "step": 0, "traceId": "718dd8557f9bf83d80468c954c88", "currentPageInfo": {"title": "", "type": "", "href": "", "scrollTop": 0}}], 'digests': [], 'question': question, 'answer': '未知'}]}
        json.dump(inference_json, open('intermediate_file/test.json', 'w', encoding='utf8'), ensure_ascii=False)
        pred_dict = model_predict_cpmb(question, label2logit, inference_json, modelcpmb, tokenizer)
        # except Exception as e:
        #     traceback.print_exc()
        dump_list.append(pred_dict)
    json.dump(dump_list, open(args.data_path, 'w'), ensure_ascii=False, indent = 4)

if __name__ == "__main__":
    main()