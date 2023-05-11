# -*- coding: utf-8 -*-

import time
import torch
import traceback
from interaction import platformctrl_pipeline
import json
import re
import time
from cpm_live.generation.bee import CPMBeeBeamSearch
from cpm_live.models import CPMBeeTorch, CPMBeeConfig
from cpm_live.tokenizers import CPMBeeTokenizer
from utils import add_ref
import argparse

def model_predict_cpmb(modelcpmb, tokenizer_cpmb, question, max_abstract_num=3, whether_corrupt_abstract=True):
    op = platformctrl_pipeline.Operator()
    beam_search = CPMBeeBeamSearch(
        model=modelcpmb,
        tokenizer=tokenizer_cpmb,
    )

    # topk_decoding = CPMBeeRandomSampling(
    #     model=modelcpmb,
    #     tokenizer=tokenizer_cpmb,
    # )

    # max lenght 4096, avoid memory overflow
    MEMORY_OVERFLOW_LENGTH=3072

    def whether_filter_source(href, filter_hrefs):
        for k in filter_hrefs:
            if k in href:
                print("filtering the current source: " + href)
                return True
        return False

    with torch.inference_mode():
        question_input = question.strip()
        src_line = "原始问题：" + question_input + "搜索引擎查询语句："
        src_line = re.sub('<', '<<', src_line)
        instance = [
            {"source": src_line, "<ans>": ""},
        ]
        queries = beam_search.generate(instance, max_length=192, beam_size=3, repetition_penalty=1.05)[0]['<ans>'].split("；")
        queries = list(set(queries))
        print(queries)
        abstracts = []
        hrefs = []
        accessed_links = []
        # todo 不同query得到的data的重合网页需要去掉
        filter_hrefs = []
        # filter_hrefs = ['zhihu.com']
        for query in queries:
            print("current query is: " + query + "\n")
            query = re.sub(r'\n', '', query)
            searched_results = op.search(query)
            # visit 3 pages per query, you can increase the num
            max_page_per_query = min(3, op.get_page_num())
            for page_idx in range(max_page_per_query):
                if len(abstracts) >= max_abstract_num:
                    break
                if searched_results[page_idx]["url"] in accessed_links or whether_filter_source(searched_results[page_idx]["url"], filter_hrefs):
                    continue
                else:
                    accessed_links.append(searched_results[page_idx]["url"])

                # src_line = "原始问题：" + question_input + "当前搜索引擎查询语句：" + query + "搜索引擎返回页面：" + "标题：" + searched_results[page_idx]["title"] + "；简介：" + searched_results[page_idx]["summary"] + "是否和原始问题相关？"
                # src_line = re.sub('<', '<<', src_line)
                # instance = [
                #     {"source": src_line, "<ans>": ""}
                # ]
                # whether_load_page = beam_search.generate(instance, max_length=8, beam_size=3, repetition_penalty=1.05)[0]["<ans>"]
                # if whether_load_page == "否":
                #     print("跳过页面：" + searched_results[page_idx]["title"] + "\n")
                #     continue
                # else:
                #     print("进入页面：" + searched_results[page_idx]["title"] + "\n")

                print("进入页面：" + searched_results[page_idx]["name"] + "\n")

                href, page_detail = op.load_page(page_idx)
                if page_detail is None:
                    print("your connection fails, no page rendered")
                    continue
                if len(page_detail) == 0:
                    print("page no content, continue \n")
                    continue
                print("页面内容：" + page_detail)
                print(href)
                print("\n")
                # 分window摘要
                extract_times = int(len(page_detail) / MEMORY_OVERFLOW_LENGTH) + 1
                abstract = []
                print("dividing into " + str(extract_times) + "sub pages")
                for idx in range(extract_times):
                    start = idx * MEMORY_OVERFLOW_LENGTH
                    end = (idx+1) * MEMORY_OVERFLOW_LENGTH if (idx+1) * MEMORY_OVERFLOW_LENGTH < len(page_detail) else len(page_detail)
                    if end - start < 256:
                        print("remaining page too short, skip")
                        continue
                    detail = page_detail[start: end]
                    print("sub page " + str(idx) + ": \n" + detail)

                    src_line = "原始问题："+ question_input + "当前搜索引擎查询语句：" + query + "当前页面具体内容：" + detail + "摘取和原问题相关的摘要："
                    src_line = re.sub('<', '<<', src_line)
                    instance = [
                        {"source": src_line, "<ans>": ""}
                    ]
                    # sub_abstract = topk_decoding.generate(instance, max_length=512, top_p=0.9, repetition_penalty=1.05)[0]["<ans>"]
                    sub_abstract = beam_search.generate(instance, max_length=512, beam_size=3, repetition_penalty=1.05)[0]["<ans>"]
                    if sub_abstract != "无" and len(sub_abstract) != 0:
                        abstract.append(sub_abstract)
                        print("摘取内容：" + sub_abstract + "\n")
                    else:
                        print("无摘取 \n")
                if len(abstract) > 0:
                    hrefs.append(href)
                    abstracts.append("".join(abstract))
            if len(abstracts) >= max_abstract_num:
                break
                
        # print("loading QA model")
        # ckpt_path = "/data/private/qinyujia/CPM-Live-master/cpm-live/results/cpm_bee_qa_v2_new4-best.pt"
        # modelcpmb.load_state_dict(torch.load(ckpt_path))
        # modelcpmb.cuda()
        # print("loading ended")
        Qa_time = time.time()
        new_context = ""
        total_length = 0

        # if whether_corrupt_abstract:
        #     abstracts = currupt_abstract_v2(abstracts)

        for c in abstracts:
            if total_length >= MEMORY_OVERFLOW_LENGTH:
                break
            c_len = len(c)
            if total_length + c_len >= MEMORY_OVERFLOW_LENGTH:
                c = c[: MEMORY_OVERFLOW_LENGTH - total_length]
            total_length += c_len
            new_context += "摘要：" + c + "；"
        context = new_context
        src_line = context + "问题：" + question_input + "；答案："
        src_line = re.sub(' ', '', src_line)
        src_line = re.sub('<', '<<', src_line)
        instance = [
            {'source': src_line, '<ans>': ''},
        ]
        answer = beam_search.generate(instance, max_length=768, beam_size=3, repetition_penalty=1.05)[0]['<ans>']
        answer_addref = add_ref({'question': question, 'abstract': abstracts, 'href': hrefs, 'answer': answer})
        print('the question is:')
        print(question)
        print('the abstrcts are:')
        print(abstracts)
        print('the answer is:')
        print(answer)
        print('reference link')
        print(hrefs)
        print('addref answer')
        print(answer_addref)
        print('the time QA is:%f' % (time.time() - Qa_time))

        return {'question': question, 'abstract': abstracts, 'href': hrefs, 'answer': answer, 'answer_add_ref': answer_addref}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default="dump_prediction.json")
    parser.add_argument('--ckpt_path', type=str, default="../training/results/cpm_bee_qa_v2_combine-best.pt")
    args = parser.parse_args()

    config = CPMBeeConfig.from_json_file("cpm_live/config/cpm-bee-10b.json")
    tokenizer_cpmb = CPMBeeTokenizer()
    modelcpmb = CPMBeeTorch(config=config)

    modelcpmb.load_state_dict(torch.load(args.ckpt_path))
    modelcpmb.cuda()

    dump_list = []
    for question in ["发改委表示「今年首批中央储备冻猪肉于 8 日投放」，释放了什么信号？可能带来哪些影响？", "历史上，蓝玉的死究竟冤不冤？", "为何成都此次疫情如此严重？", "为什么千辛万苦考公务员，但考上公务员以后，并没有想象中那么快乐？", "为什么中国人能自己赚而西方必须抢？", "同样是9月7日发布，不谈其它，只谈性能，到底买华为Mate50还是iPhone14？", "2022年了，谁能告诉我，农民在家种地，为什么退休没有退休金？", "发达国家真的会教给留学生核心技术吗？", "《西虹市首富》中王多鱼为什么选择挑战花光十亿而不是直接拿走一千万？", "为什么大部分人都为了赚钱而奋斗？而不是为了理想而奋斗？", "大学的本质和职责是什么？", "如果好人没好报，为什么我们还要做好人？", "为什么现在的一些00后长得那么成熟？"]:
        try:
            pred_dict = model_predict_cpmb(modelcpmb, tokenizer_cpmb, question, max_abstract_num=5, whether_corrupt_abstract=False)
        except Exception as e:
            traceback.print_exc()
        dump_list.append(pred_dict)
    json.dump(dump_list, open(args.data_path, 'w'), ensure_ascii=False, indent = 4)