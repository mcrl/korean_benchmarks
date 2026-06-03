#!/bin/bash

source ~/.bashrc
conda activate generation

export HF_TOKEN=YOUR_HF_TOKEN
export PYTORCH_ALLOC_CONF=expandable_segments:True

export BACKEND="hf"
export MODEL="Model Name"
export SRC_PATH="src/custom_tasks/benchmark-compact" # Path where task information is stored
export OUTPUT_PATH="PATH To Save Output"

# Evaluation without chat_template
lm_eval \
    --model $BACKEND \
    --model_args pretrained=$MODEL,trust_remote_code=True,max_length=4096 \
    --include_path $SRC_PATH \
    --tasks benchmark-ko-gen \
    --output_path $OUTPTU_PATH \
    --log_samples \
    --batch_size 1

# Evaluation with chat_template
lm_eval \
    --model $BACKEND \
    --model_args pretrained=$MODEL,trust_remote_code=True \
    --include_path $SRC_PATH \
    --tasks benchmark-ko-gen \
    --output_path $OUTPTU_PATH \
    --log_samples \
    --batch_size 1 \
    --apply_chat_template \
    --fewshot_as_multiturn