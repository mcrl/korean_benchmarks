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

# 언어/번역본 택1 (closed API는 로그확률 불가라 생성형 task만)
#  ko   : ko-gsm8k,ko-ifeval,ko-eqbench,ko-arc-easy-gen,ko-arc-challenge-gen,ko-winogrande-gen,ko-lambada-gen
#  deepl: ko-gsm8k-deepl,ko-eqbench-deepl,ko-arc-easy-gen-deepl,ko-arc-challenge-gen-deepl
#  en   : en-gsm8k,en-eqbench,en-arc-easy-gen,en-arc-challenge-gen,en-winogrande-gen
TASKS="ko-gsm8k,ko-ifeval,ko-eqbench,ko-arc-easy-gen,ko-arc-challenge-gen,ko-winogrande-gen,ko-lambada-gen"

# ※ Reasoning 계열 API 모델(예: gpt-5 계열) 주의:
#   내부 추론 토큰(reasoning tokens)이 응답엔 안 보이지만 출력 budget(max_tokens)에 카운트됨.
#   eqbench 처럼 max_gen_toks 가 작은 task는 추론으로 budget을 소진해 빈 응답/에러가 남.
#   → 그런 모델은 eqbench 의 max_gen_toks 를 충분히 키워서(예: 1024) 실행할 것.
#     lm_eval ... --gen_kwargs max_gen_toks=1024   (eqbench만 따로 돌릴 때)

# Evaluation with chat_template (닫힌 API는 chat 형식)
lm_eval \
    --model $BACKEND \
    --model_args model="$MODEL_NAME" \
    --include_path "$SRC_PATH" \
    --tasks "$TASKS" \
    --output_path $OUTPUT_PATH \
    --log_samples \
    --apply_chat_template \
    --fewshot_as_multiturn
