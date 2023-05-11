from cpm_live.generation.bee import CPMBeeBeamSearch
from cpm_live.models import CPMBeeTorch, CPMBeeConfig
from cpm_live.tokenizers import CPMBeeTokenizer
import torch
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--test_file', type=str, required=True)
parser.add_argument('--output_file', type=str, required=True)
parser.add_argument('--ckpt_path', type=str, required=True)
# setting beam size to 1 would significantly accelerate inference, but hurt the performance a little bit
parser.add_argument('--beam_size', type=int, default=3, required=False)
args = parser.parse_args()

if __name__ == "__main__":
    config = CPMBeeConfig.from_json_file("config/cpm-bee-10b.json")
    tokenizer = CPMBeeTokenizer()
    model = CPMBeeTorch(config=config)

    model.load_state_dict(torch.load(args.ckpt_path))
    model.cuda()

    # use beam search
    beam_search = CPMBeeBeamSearch(
        model=model,
        tokenizer=tokenizer,
    )

    fin = open(args.test_file, 'r', encoding='utf-8')
    lines = fin.readlines()
    fin.close()
    fout = open(args.output_file, "w", encoding="utf-8")
    
    for data_idx in range(len(lines)):
        instance = [json.loads(lines[data_idx])]
        answer = instance[0]["<ans>"]
        instance[0]["<ans>"] = ""
        try:
            inference_results = beam_search.generate(instance, max_length=512, repetition_penalty=1.2, beam_size=args.beam_size)[0]
            fout.write(json.dumps({"instance": instance, 'answer': answer, 'decode_tokens': inference_results["<ans>"]}, ensure_ascii=False) + '\n')
            print("input: {}".format(inference_results["source"]))
            print("inference: {}".format(inference_results["<ans>"]))
            print("ground_truth: {}".format(answer))
            print('\n')
            fout.flush()
        except:
            print("memory overflow of data index {}".format(data_idx))
    fout.close()
