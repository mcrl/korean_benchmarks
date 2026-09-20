#!/bin/bash
# Generative-MCQA: 객관식 정답 라벨(A/B/C/D)을 "생성"으로 출력 → exact_match.
# 닫힌 API 모델(로그확률 접근 불가)과 동일한 형식으로 열린 모델을 비교하기 위함.

source ~/.bashrc
conda activate generation

export HF_TOKEN=YOUR_HF_TOKEN
export PYTORCH_ALLOC_CONF=expandable_segments:True

export BACKEND="hf"
export MODEL="Model Name"
export SRC_PATH="src/custom_tasks/benchmark-compact" # Path where task information is stored
export OUTPUT_PATH="PATH To Save Output"

# 언어/번역본 택1: benchmark-ko-genmcqa / benchmark-deepl-genmcqa / benchmark-en-genmcqa
export TASKS="benchmark-ko-genmcqa"

# Evaluation with chat_template (닫힌 API와 동일 비교라 chat 사용)
lm_eval \
    --model $BACKEND \
    --model_args pretrained=$MODEL,trust_remote_code=True,max_length=4096 \
    --include_path $SRC_PATH \
    --tasks $TASKS \
    --output_path $OUTPUT_PATH \
    --log_samples \
    --batch_size 16 \
    --apply_chat_template \
    --fewshot_as_multiturn

# ───────────────────────────────────────────────────────────────────────────
# (Reasoning 모델 변형) Qwen 등 thinking 모델은 chat에서 "<think>/Thinking Process:"
# 머리말을 먼저 출력하다 stop sequence("\n")에 잘려 라벨을 못 내고 0점이 됨.
# enable_thinking=False 로 추론을 끄면 라벨을 바로 출력 → 정상 점수.
# (결과는 thinking-on 과 구분되게 별도 OUTPUT_PATH 권장)
# ───────────────────────────────────────────────────────────────────────────
lm_eval \
    --model $BACKEND \
    --model_args pretrained=$MODEL,trust_remote_code=True,max_length=4096,enable_thinking=False \
    --include_path $SRC_PATH \
    --tasks $TASKS \
    --output_path $OUTPUT_PATH \
    --log_samples \
    --batch_size 16 \
    --apply_chat_template \
    --fewshot_as_multiturn
