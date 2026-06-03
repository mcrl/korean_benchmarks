#!/bin/bash

source ~/.bashrc
conda activate api

export HF_TOKEN="YOUR_HF_TOKEN"
export OPENAI_API_KEY="YOUR_OPENAI_TOKEN"
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_TOKEN"

export BACKEND="which backend to use" # "openai-chat-completions" for gpt models, "anthropic-chat-completions" for anthropic models
export MODEL_NAME="Model Name"
export SRC_PATH="src/custom_tasks/benchmark-compact" # Path where task information is stored
export OUTPUT_PATH="PATH To Save Output"
TASKS="ko-gsm8k,ko-ifeval,ko-eqbench,ko-arc-easy-gen,ko-arc-challenge-gen,ko-winogrande-gen,ko-lambada-gen"

# Evaluation without chat_template
lm_eval \
    --model $BACKEND \
    --model_args model="$MODEL_NAMEODEL" \
    --include_path "$INCLUDE_PATH" \
    --tasks "$TASKS" \
    --output_path $OUTPTU_PATH \
    --log_samples

# Evaluation with chat_template
lm_eval \
    --model hf \
    --model_args model="$MODEL_NAME" \
    --include_path "$INCLUDE_PATH" \
    --tasks "$TASKS" \
    --output_path $OUTPTU_PATH \
    --log_samples \
    --apply_chat_template