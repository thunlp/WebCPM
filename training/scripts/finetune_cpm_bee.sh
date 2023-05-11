#! /bin/bash

export CUDA_VISIBLE_DEVICES=1,3
GPUS_PER_NODE=$(echo $CUDA_VISIBLE_DEVICES | tr ',' '\n' | wc -l | xargs)
echo "Number of visible devices: $GPUS_PER_NODE, should be the same as visible devices"

set -ex

MASTER_ADDR=localhost
MASTER_PORT=3239
NNODES=1
NODE_RANK=0

OPTS=""
OPTS+=" --model-config config/cpm-bee-10b.json"
OPTS+=" --dataset dataset/train_data"
OPTS+=" --dataseteval dataset/dev_data"
OPTS+=" --epoch 5"
OPTS+=" --batch-size 1"
OPTS+=" --train-iters 100"
OPTS+=" --save-name cpm_bee_action_new"
OPTS+=" --max-length 2048"
OPTS+=" --save results/"
OPTS+=" --lr 0.0001"
OPTS+=" --inspect-iters 100"
OPTS+=" --warmup-iters 1"
OPTS+=" --save-epochs 1"
OPTS+=" --lr-decay-style noam"
OPTS+=" --weight-decay 0.01"
OPTS+=" --clip-grad 1.0"
OPTS+=" --loss-scale 32768"
OPTS+=" --start-step 0"
OPTS+=" --load ../../pretrained_models/cpm_live_checkpoint-602000.pt"

CMD="torchrun --nnodes=${NNODES} --nproc_per_node=${GPUS_PER_NODE} --rdzv_id=1 --rdzv_backend=c10d --rdzv_endpoint=${MASTER_ADDR}:${MASTER_PORT} finetune_cpm_bee.py ${OPTS}"

echo ${CMD}
$CMD