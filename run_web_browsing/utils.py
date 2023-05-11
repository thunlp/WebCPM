import re
from rouge import Rouge

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
                print(e)
                print(sentence)

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
                                    # 继续切分余下的句子
                                    text = self.text[couple_index_2 + 1:]
                                    return self.rules(text, cut_list)
                                elif self.text[couple_index_2 + 1] in self.end_operator:
                                    cut_list.append(self.text[:couple_index_2 + 2])
                                    # 继续切分余下的句子
                                    text = self.text[couple_index_2 + 2:]
                                    return self.rules(text, cut_list)
                                else:
                                    cut_list.append(self.text)
                                    return cut_list
                    else:
                        cut_list.append(self.text)
                        return cut_list
            # 错误符号用法直接返回该句子
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

def get_rougeL_recall(source, answer):
    n = len(source)
    m = len(answer)
    f = [[0 for i in range(n + 1)] for i in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if source[j] == answer[i]:
                f[i+1][j+1] = f[i][j] + 1
            else:
                f[i+1][j+1] = max(f[i][j+1], f[i+1][j])
    return float(f[m][n]) / len(answer)

def add_ref(instance):
    abstracts = instance["abstract"]
    if len(abstracts) == 0:
        return None
    
    result = instance["answer"]
    ss_2 = SentenceSplitter(["。", "？", "！", "；", ';', "……", "…"])
    sentences = ss_2.cut(result)

    #assume that one sentence only has one reference
    ref = [0] * len(sentences)
    rouge = Rouge()
    for st_id, sentence in enumerate(sentences):
        score = 0
        best_id = 0
        for ab_id, abstract in enumerate(abstracts):
            #print('ab:',abstract)
            #print('st:',sentence)
            '''try:
                cur_score = rouge.get_scores(' '.join(list(abstract)), ' '.join(list(sentence)))[0]["rouge-l"]["r"]
            except:
                print(len(abstract))
                print(len(sentence))
                cur_score = 0'''
            cur_score = get_rougeL_recall(list(abstract), list(sentence))
            if cur_score > score:
                score = cur_score
                best_id = ab_id
        if score > 0.45:
            ref[st_id] = best_id + 1
    #print(ref)

    context = ''
    for it, abstract in enumerate(abstracts):
        context += f'【{it + 1}】' + abstract
    
    #merge references
    raw_ref = ref
    ref = [''] * len(sentences)
    for it in range(len(sentences) - 2):
        if (raw_ref[it] != 0) and (raw_ref[it] == raw_ref[it + 2]) and (raw_ref[it] != raw_ref[it + 1]):
            ids = [raw_ref[it], raw_ref[it + 1]]
            low = it
            while (low > 0) and (raw_ref[low - 1] in ids) and (ref[low-1] == ''):
                low -= 1
            high = it + 3
            while (high < len(sentences)) and (raw_ref[high] in ids) and (ref[high] == ''):
                high += 1
            if 0 in ids:
                ref_st = f'【{sum(ids)}】'
            else:
                ref_st = f'【{ids[0]}】【{ids[1]}】'
            ref[low:high] = [ref_st] * (high - low)
            it = high - 1
    for it in range(len(sentences)):
        if (ref[it] == '') and (raw_ref[it] != 0):
            ref[it] = f'【{raw_ref[it]}】'
    #print(ref)
    for it in range(len(sentences) - 1):
        if ref[it] != ref[it+1]:
            sentences[it] += ref[it]
    sentences[-1] += ref[-1]
    result = ''.join(sentences)
    return result