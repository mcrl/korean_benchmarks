"""
모든 평가 결과를 하나의 tidy CSV(results_all.csv)로 모으는 집계 스크립트.

한 줄 = (source, model, version, eval_type, task, prompt_format, metric, value)
  - source       : open / closed   (모델명으로 판별)
  - version       : ko / deepl / en (task명으로 판별)
  - eval_type    : logprob-mcqa / generative-mcqa / generation
  - prompt_format: plain / chat / chat_nothink (enable_thinking=False)

기대하는 출력 디렉토리 구조 (각 run_eval.sh의 OUTPUT_PATH 아래, lm-eval 기본 레이아웃):
    <OUTPUT_ROOT>/<eval_type_dir>/<prompt_format>/<model>/.../results_*.json
SCANS 의 (상대경로, prompt_format)를 자신의 레이아웃에 맞게 수정해서 사용한다.

우선순위: SCANS 뒤쪽이 중복 키를 덮어씀(같은 모델/version/eval_type/task/format/metric).
한 디렉토리 안에서는 타임스탬프 늦은 JSON이 이김.

값 스케일: acc/acc_norm/acc_npsq/exact_match 류는 ×100, eqbench·percent_parseable는 원본(0~100).
"""
import argparse, csv, json
from pathlib import Path

# ▼▼ 자신의 결과 루트로 교체 ▼▼
OUTPUT_ROOT = Path("PATH/To/Your/Outputs")

# (OUTPUT_ROOT 기준 상대경로, prompt_format) — 뒤쪽이 우선순위 높음
SCANS = [
    ("mcqa/plain",          "plain"),
    ("mcqa/chat",           "chat"),
    ("generation/plain",    "plain"),
    ("generation/chat",     "chat"),
    ("genmcqa/chat",        "chat"),
    ("genmcqa/chat_nothink", "chat_nothink"),   # enable_thinking=False
    ("api/chat",            "chat"),             # 닫힌 API
]

KNOWN = {"arc-easy", "arc-challenge", "winogrande", "lambada", "gsm8k", "eqbench", "ifeval"}
# 닫힌 API 모델 풀네임(자신의 모델로 교체) — source=closed 판별용
API_MODELS = {"<openai-model-id>", "<anthropic-model-id>"}


def version_of(task: str) -> str:
    if task.startswith("en-"):
        return "en"
    if task.endswith("-deepl") or "-deepl" in task:
        return "deepl"
    return "ko"


def eval_type_of(task: str) -> str:
    if "-gen" in task:
        return "generative-mcqa"
    if any(k in task for k in ("gsm8k", "eqbench", "ifeval")):
        return "generation"
    return "logprob-mcqa"


def base_task(task: str) -> str:
    t = task
    for suf in ("-gen-deepl", "-deepl", "-gen"):   # 접미사 긴 것부터(앵커)
        if t.endswith(suf):
            t = t[: -len(suf)]
            break
    for pre in ("ko-", "en-"):
        if t.startswith(pre):
            t = t[len(pre):]
    return t


def model_of(r: dict) -> str:
    cfg = r.get("config", {}) or {}
    ma = cfg.get("model_args")
    d = ma if isinstance(ma, dict) else {}
    if isinstance(ma, str):
        d = {k: v for k, v in (kv.split("=", 1) for kv in ma.split(",") if "=" in kv)}
    return d.get("pretrained") or d.get("model") or cfg.get("model") or "unknown"


def source_of(model: str) -> str:
    return "closed" if model in API_MODELS else "open"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results_all.csv")
    args = ap.parse_args()

    data = {}  # key=(model,version,eval_type,task,prompt_format,metric) -> value
    for rel, fmt in SCANS:
        base = OUTPUT_ROOT / rel
        if not base.exists():
            continue
        for jpath in sorted(base.glob("**/results_*.json")):
            try:
                r = json.load(open(jpath))
            except Exception:
                continue
            model = model_of(r)
            for task, metrics in (r.get("results") or {}).items():
                if task.startswith("benchmark"):       # 그룹 집계행 스킵
                    continue
                bt = base_task(task)
                if bt not in KNOWN:
                    continue
                ver, et = version_of(task), eval_type_of(task)
                for metric, val in (metrics or {}).items():
                    if not isinstance(val, (int, float)) or "alias" in metric:
                        continue
                    if "_stderr" in metric or metric in ("sample_len", "samples"):
                        continue
                    val_pct = val if bt == "eqbench" else val * 100
                    data[(model, ver, et, bt, fmt, metric)] = val_pct

    rows = [{
        "source": source_of(m), "model": m, "version": ver, "eval_type": et,
        "task": bt, "prompt_format": fmt, "metric": metric, "value": f"{v:.2f}",
    } for (m, ver, et, bt, fmt, metric), v in data.items()]
    rows.sort(key=lambda x: (x["source"], x["model"], x["version"], x["eval_type"],
                             x["task"], x["prompt_format"], x["metric"]))

    cols = ["source", "model", "version", "eval_type", "task", "prompt_format", "metric", "value"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
