<div align="center">

<h1>WebCPM</h1>

</div>

✨ This is the implementation of ACL 2023 paper [Interactive Web Search for Chinese Long-form Question Answering](https://arxiv.org/abs/2305.06849)

![paper](./assets/paper.png)

*Read this in [中文](README_zh.md).*

---


## Quick links

- [Quick links](#quick-links)
- [Overview](#overview)
- [Requirements](#requirements)
- [Preparation](#preparation)
  - [Prepare the Data](#prepare-the-data)
  - [Prepare the model](#prepare-the-model)
- [Train WebCPM](#train-webcpm)
  - [A brief Introduction of Pipeline-based Web Search](#a-brief-introduction-of-pipeline-based-web-search)
  - [Data Preprocessing](#data-preprocessing)
    - [Training Data Generation of Interactive Web Search](#training-data-generation-of-interactive-web-search)
    - [Training Data Generation of Pipeline-based Web Search](#training-data-generation-of-pipeline-based-web-search)
  - [Training](#training)
- [Single-task Evaluation](#single-task-evaluation)
- [Run WebCPM for New Questions](#run-webcpm-for-new-questions)
  - [Interactive Web Search](#interactive-web-search)
  - [Pipeline-based Web Search](#pipeline-based-web-search)
- [Platform Building for Data Annotation](#platform-building-for-data-annotation)
- [Bugs or questions?](#bugs-or-questions)
- [Resources of Tool Learning](#resources-of-tool-learning)
- [Citation](#citation)


## Overview
![platform](./assets/platform.png)

In this work we present WebCPM, a project for interactive Web search using Chinese Pre-trained Models. We develop a web search interface which both humans and collect human web search behaviors. Then we fine-tune PLMs with up to 10B parameters to imitate human behaviors of web search and to generate answers based on the collected facts. We open source the web search interface, dataset, implementation, and model parameters.


## Requirements

To run our code, please install all the dependency packages by using the following command:

```
pip install -r requirements.txt
```

**NOTE**: Different versions of packages (e.g., `pytorch`) may lead to different results from the paper. However, the trend should still hold no matter what versions of packages you use.

## Preparation

### Prepare the Data

First download the data from [Google Drive](https://drive.google.com/drive/folders/1IQBOCwhcMUnkxevv9wVFVLIFT3o8f7HX?usp=sharing), and put the files `interactive_data` and `pipeline_data` to `./data`, or run the following commands:

The downloaded files contain the following:

`interactive_data/data.json` is the dataset used in the experiments of the paper (**5500** instances in total).
`interactive_data/data_zhihu.json` is additional dataset collected alongside this paper (~**900** instances), with the question sourcing from [Zhihu](https://www.zhihu.com/people/71-26-1-50), you can use this for data augmentation.

Please use the following codes to split the above data into train, dev, and test set (setting --add_zhihu will add data_zhihu.json).

```bash
cd data/interactive_data
python split.py --add_zhihu
```

In addition to the interactive web search data, we also provide the dataset needed for training the pipeline-based web search: `pipeline_data` (**110k** instances in total). All the data is created by prompting text-davinci-003 and then manually filtered by human annotators. (**Note** This part is not included in the paper, and you don't need to split it into train / dev / test.)


### Prepare the model

WebCPM is based on [CPM-bee](https://github.com/OpenBMB/CPM-Live) with up to **10 billion** parameters, which is one of the largest Chinese pre-trained language model in the community. We use an early version of CPM-bee, which is denoted as cpm_10b_webcpm_exp.pt. The latest version of CPM-bee will be open-source soon. **Note the model checkpoint has not been fine-tuned towards any downstream task**. To access cpm_10b_webcpm_exp.pt, you can download the model parameters at [Tsinghua Cloud](https://cloud.tsinghua.edu.cn/d/a02ae00b11434c9c8560/), or run the following script:

```
cd models
bash download_model_initial_model.sh
```

The above codes will download the 10B (non-finetuned) model at `models`, for the finetuned pipeline model, please refer to `download_model_pipeline_finetuned.sh`, or download it manually from [Tsinghua Cloud](https://cloud.tsinghua.edu.cn/d/3dc39eccc6c64bb58671/).

## Train WebCPM

![platform](./assets/framework.png)

We provide two versions of WebCPM: (1) interactive web search (the method proposed in the ACL paper) and (2) pipeline-based web search, which is easier to deploy (this method is not reported in the paper). Both versions use different scripts for training data generation and the same codes for model training.

### A brief Introduction of Pipeline-based Web Search

The workflow follows four stages: (1) first, generate possible search queries based on the original question; (2) then for each search query, call Bing search and visit top-K web pages; (3) for each web page, extract the important information; (4) based on all the recorded information, generate a coherent and nuanced answer. All these things are trained in a multi-task way, please refer to `run_web_browsing/run_pipeline.py`. For details of the interactive web search, please refer to our original paper.

### Data Preprocessing

Before you start, run the following codes:

```bash
export PYTHONPATH=/**your-base-path**/webcpm
```

The training data generation is as follows (we differentiate between interactive web search and pipeline-based method). The following codes will generate `train_data`, `dev_data`, and `test_data` in the corresponding folder, which will be loaded during training.

#### Training Data Generation of Interactive Web Search

First, construct the data for the synthesis model using the following codes:

```bash
cd dataset_interactive
python make_data_synthesis_model.py --data_path ../../data/interactive_data  --augment_qa_data --augment_data_path ../../data/pipeline_data
```

We explain some of the arguments as follows:

* `data_path`: The source data path.
* `augment_qa_data`: Whether to augment the training data with qa data automatically generated by text-davinci. (To replicate the results in our paper, do not add this argument)
* `augment_data_path`: The data path to the augmented training data.

The training data generation of the search model is as follows:

```bash
python make_data_search_model.py --add_query --add_action --add_abstract --abstract_all_tokens
```

We explain some of the arguments as follows:

* `data_path`: The source data path.
* `add_query`: If True, will add the query generation data.
* `add_abstract`: If True, will add the generate supporting fact extraction data.
* `abstract_all_tokens`: If True, supporting fact extraction module will generate all the tokens, instead of only the first / last few tokens.
* `add_action`: If True, will add the action prediction data.
* `add_synthesis`: If True, will load local data for the synthesis model. **Note You must first run python make_data_synthesis_model.py to obtain the synthesis data then add this argument here**.
  
If you want to train all sub-tasks in a multi-task way, just add all the above arguments; otherwise only add one argument (e.g., `--add_query`) for single-task testing.

#### Training Data Generation of Pipeline-based Web Search

Please run the following codes:

```bash
cd dataset_pipeline
python make_data.py
```

### Training

To train WebCPM, run the following codes:

```bash
cd training
export PYTHONPATH=/**your-base-path**/webcpm
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
GPUS_PER_NODE=$(echo $CUDA_VISIBLE_DEVICES | tr ',' '\n' | wc -l | xargs)
echo "Number of visible devices: $GPUS_PER_NODE, should be the same as visible devices"

set -ex

MASTER_ADDR=localhost
MASTER_PORT=3239
NNODES=1
NODE_RANK=0

OPTS=""
OPTS+=" --model-config config/cpm-bee-10b.json"
OPTS+=" --dataset ../data/dataset_interactive/train_data"
OPTS+=" --dataseteval ../data/dataset_interactive/dev_data"
OPTS+=" --epoch 5"
OPTS+=" --batch-size 8"
OPTS+=" --train-iters 100"
OPTS+=" --save-name webcpm_finetuned"
OPTS+=" --max-length 2560"
OPTS+=" --save ../models/"
OPTS+=" --lr 0.0001"
OPTS+=" --inspect-iters 100"
OPTS+=" --warmup-iters 1"
OPTS+=" --save-epochs 1"
OPTS+=" --lr-decay-style noam"
OPTS+=" --weight-decay 0.01"
OPTS+=" --clip-grad 1.0"
OPTS+=" --loss-scale 32768"
OPTS+=" --start-step 0"
OPTS+=" --load ../models/cpm_10b_webcpm_exp.pt"

CMD="torchrun --nnodes=${NNODES} --nproc_per_node=${GPUS_PER_NODE} --rdzv_id=1 --rdzv_backend=c10d --rdzv_endpoint=${MASTER_ADDR}:${MASTER_PORT} finetune_cpm_bee.py ${OPTS}"

echo ${CMD}
$CMD
```

We explain some of the arguments as follows:

* `dataset` and `dataseteval`: The path to the processed file. For interactive web search, it is dataset_interactive, while for pipeline-based method, it is dataset_pipeline.
* `batch-size`: The batch size of a single GPU, the real batch size will be #GPUs x batch-size per GPU.
* `max-length`: The maximum sequence length of the data (not the model), those longer training instances will be dropped.
* `save-name` and `save`: The path to save the fine-tuned model and the name of the saved model checkpoint.
* `epoch`: The number of training epochs.
* `load`: The path to the pre-trained model checkpoint (cpmb in this case).

Note no matter which module you are training (or the multi-task setting), you can use the above codes. We are training on 8x80G A100, you can change the batch size according to your GPU devices, the performance is not sensitive to the hyper-parameters.

## Single-task Evaluation

To evaluate different sub-tasks, you can first run the following codes to get the prediction of your fine-tuned model on the test data:

```bash
cd inference
python inference.py --test_file ../training/dataset_interactive/test.txt --output_file output/test_predictions.json --ckpt_path **your_finetuned_checkpoint.pt
```

We explain some of the arguments as follows:

* `test_file`: The path to the test file, it should have been generated during data preprocessing.
* `output_file`: The path you want to write your predictions.
* `ckpt_path`: The path to your fine-tuned model.

After obtaining the predictions on the test file, you can run the following codes for single-task evaluation:

```bash
python evaluate.py --input_file output/test_predictions.txt --evaluate_action
```

We explain some of the arguments as follows:

* `input_file`: The path you write your predictions of the test file.
* `evaluate_action`: Whether you want to evaluate the action prediction task (F1).
* `evaluate_query`: Whether you want to evaluate the search query generation task (Rougel-L).
* `evaluate_abstract`: Whether you want to evaluate the supporting fact extraction task (Rougel-L).
* `abstract_all_tokens`: Which mode do you train your model for supporting fact extraction, if you generate all the tokens, add this argument (Rougel-L).
* `evaluate_answer`: Whether you want to evaluate the answer synthesis task (Rougel-L).
* `beam_size`: Setting beam size to 1 would significantly accelerate inference, but hurt the performance a little bit.


## Run WebCPM for New Questions

This is the implementation for the whole pipeline evaluation. You can use the following codes to generate answers for new questions. Note this requires you to first get a Bing search API key from [here](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api) and run the following codes:

```bash
cd run_web_browsing
export PYTHONPATH=/**base-path**/webcpm
export BING_SEARCH_KEY="**Your Bing Search API Key**"
```

### Interactive Web Search

Coming soon.

### Pipeline-based Web Search

```bash
python run_pipeline.py --data_path predictions/test.json --ckpt_path **your-checkpoint**
```

We explain some of the arguments as follows:

* `data_path`: The path you write your predictions.
* `ckpt_path`: The path to the checkpoint where you have trained using the pipeline-based method.


## Platform Building for Data Annotation

![platform](./assets/annotation.png)

We open source our web search interface, you can use it for data annotation. Please refer to [Annotation](./annotation_platform/README.md). The codes are a bit messy currently, we will soon upload a cleaner version.


## Bugs or questions?

If you have any questions related to the codes or the paper, please contact Yujia (`qyj20@mails.tsinghua.edu.cn`) or open an issue.

## Resources of Tool Learning

With the powerful capabilities of foundation models, we are eager to see their applications in manipulating various tools. WebCPM is one typical research attempts. For more resources, please refer to the following:

- **BMTools**. [[Project](https://github.com/OpenBMB/BMTools)]

- **Tool Learning**. [[Paper](https://arxiv.org/abs/2304.08354)]
  
- **Tool Learning Paper List**. [[Project](https://github.com/thunlp/ToolLearningPapers)]

## Citation

If you find our WebCPM useful, please use the following citation: 

```bibtex
@inproceedings{qin2023webcpm,
    title = "WebCPM: Interactive Web Search for Chinese Long-form Question Answering",
    author={Yujia Qin and Zihan Cai and Dian Jin and Lan Yan and Shihao Liang and Kunlun Zhu and Yankai Lin and Xu Han and Ning Ding and Huadong Wang and Ruobing Xie and Fanchao Qi and Zhiyuan Liu and Maosong Sun and Jie Zhou},
    booktitle = "Proceedings of ACL 2023",
    year = "2023",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/2305.06849",
}
```
