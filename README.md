# Korean Benchmarks

## Summary
**SNU Thunder Korean Benchmarks** is a collection of Korean benchmark datasets designed to evaluate language models in a wide range of tasks. 
It includes datasets that are either translated or newly constructed to align with Korean language and cultural context.

The datasets were constructed through task-specific routes, including expert-reviewed translation and localization, direct Korean construction, and hybrid Korean-specific redesign.

--- 

## Dataset Construction Process

### 1. Initial Translation / Data Generation
- Used [DeepL API](https://www.deepl.com/ko/products/api) to translate English datasets (ARC, GSM8K, Winogrande, EQ-Bench, IFEval).
- For LAMBADA, Korean data was newly created from public literary works in [공유마당](https://gongu.copyright.or.kr/gongu/main/main.do).

### 2. Correction
- Domain experts corrected:
  - Errors in the original datasets (e.g., typos, label errors, duplicates).
  - Awkward or literal translations.
  - Inconsistencies in tone and formatting.
  - Unnatural or ambiguous expressions.

### 3. Localization
- Replaced foreign names, units, and concepts with Korean equivalents.
  - e.g., “Jessica” → “지희”, feet → 미터, dollars → 원
- Modified cultural scenarios (e.g., lawn mowing → shoe shining) where necessary.

### 4. Cross-review
- A separate reviewer validated the entire dataset for logical coherence and fluency.

For more information about each dataset, please refer to its dedicated Hugging Face page.

---

## Datasets Composition

| Benchmark         | Evaluation Task                                  | Data Size                                       | Creation Method       | Columns                                           | Available at                                                                 |
|-------------------|---------------------------------------------------|--------------------------------------------------|------------------------|---------------------------------------------------|------------------------------------------------------------------------------|
| SNU Ko-ARC        | Science Knowledge Q&A                            | 3,543 (easy: 2,376, challenge: 1,167)            | Translated + Refined            | `id`, `question`, `choices`, `answerKey`          | [link](https://huggingface.co/datasets/thunder-research-group/SNU_Ko-ARC)                   |
| SNU Ko-GSM8K      | Math Problem Solving                              | 1,319                                            | Translated + Refined            | `question`, `answer`                              | [link](https://huggingface.co/datasets/thunder-research-group/SNU_Ko-GSM8K)                 |
| SNU Ko-EQ-Bench   | Dialogue Sentiment Analysis                       | 171                                              | Translated + Refined            | `prompt`, `reference_answer`, `reference_answer_fullscale` | [link](https://huggingface.co/datasets/thunder-research-group/SNU_Ko-EQ-Bench)              |
| SNU Ko-WinoGrande | Logical/Contextual Reasoning and Word Prediction | 1,267                                            | Translated + Refined            | `sentence`, `option1`, `option2`, `answer`        | [link](https://huggingface.co/datasets/thunder-research-group/SNU_Ko-WinoGrande)           |
| SNU Ko-LAMBADA    | Literary Context Understanding and Word Prediction| 2,255                                            | Newly Constructed            | `index`, `text`, `answer`, `candidate`            | [link](https://huggingface.co/datasets/thunder-research-group/SNU_Ko-LAMBADA)             |
| SNU Ko-IFEval     | Instruction Following                             | 841 (Translation: 541, Development: 300)         | Translated + Newly Constructed | `key`, `prompt`, `instruction_id_list`, `kwargs` | [link](https://huggingface.co/datasets/thunder-research-group/SNU_Ko-IFEval)               |
| **Total**         |                                                   | **9,396**                                        |                        |                                                   |                                                                              |

You can find examples in the `samples` folder.

---

## How to Use (via Hugging Face `datasets`)

```python
from datasets import load_dataset

# SNU Ko-IFEval
snu_ifeval = load_dataset("thunder-research-group/SNU_Ko-IFEval")

# SNU Ko-ARC
snu_arc_c = load_dataset("thunder-research-group/SNU_Ko-ARC", "challenge")
snu_arc_e= load_dataset("thunder-research-group/SNU_Ko-ARC", "easy")

# SNU Ko-GSM8K
snu_gsm8k = load_dataset("thunder-research-group/SNU_Ko-GSM8K")

# SNU Ko-EQ-Bench
snu_eqbench = load_dataset("thunder-research-group/SNU_Ko-EQ-Bench")

# SNU Ko-WinoGrande
snu_winogrande = load_dataset("thunder-research-group/SNU_Ko-WinoGrande")

# SNU Ko-LAMBADA
snu_lambada = load_dataset("thunder-research-group/SNU_Ko-LAMBADA")
```

---

## Additional Information

### Cite as
```
@inproceedings{
so2026constructing,
title={Constructing Korean Benchmark Suite for Reliable Evaluation of Foundation Models},
author={Yeonkyoung So and Jongmin Kim and Sungmok Jung and Gyuseong Lee and Sangho Kim and Jongyeon Park and Joonhak Lee and Seho Pyo and Gyeongje Cho and Seorin Kim and Jisoo Kim and Suyoung Park and Hyunji M. Park and Yelim Ahn and Yeongho Seo and Jaejin Lee},
booktitle={ICML 2026 Workshop on Combining Theory and Benchmarks: Towards A Virtuous Cycle to Understand and Guarantee Foundation Model Performance},
year={2026},
url={https://openreview.net/forum?id=oJ3rhISSqO}
}
```


### Original Dataset Citation Information
```
@article{allenai:arc,
      author    = {Peter Clark  and Isaac Cowhey and Oren Etzioni and Tushar Khot and
                    Ashish Sabharwal and Carissa Schoenick and Oyvind Tafjord},
      title     = {Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge},
      journal   = {arXiv:1803.05457v1},
      year      = {2018},
}
```
```
@article{cobbe2021gsm8k,
  title={Training Verifiers to Solve Math Word Problems},
  author={Cobbe, Karl and Kosaraju, Vineet and Bavarian, Mohammad and Chen, Mark and Jun, Heewoo and Kaiser, Lukasz and Plappert, Matthias and Tworek, Jerry and Hilton, Jacob and Nakano, Reiichiro and Hesse, Christopher and Schulman, John},
  journal={arXiv preprint arXiv:2110.14168},
  year={2021}
}
```
```
@misc{paech2023eqbench,
    title={EQ-Bench: An Emotional Intelligence Benchmark for Large Language Models},
    author={Samuel J. Paech},
    year={2023},
    eprint={2312.06281},
    archivePrefix={arXiv},
    primaryClass={cs.CL}
}
```
```
@article{sakaguchi2021winogrande,
  title={Winogrande: An adversarial winograd schema challenge at scale},
  author={Sakaguchi, Keisuke and Bras, Ronan Le and Bhagavatula, Chandra and Choi, Yejin},
  journal={Communications of the ACM},
  volume={64},
  number={9},
  pages={99--106},
  year={2021},
  publisher={ACM New York, NY, USA}
}
```
```
@misc{zhou2023instructionfollowingevaluationlargelanguage,
      title={Instruction-Following Evaluation for Large Language Models}, 
      author={Jeffrey Zhou and Tianjian Lu and Swaroop Mishra and Siddhartha Brahma and Sujoy Basu and Yi Luan and Denny Zhou and Le Hou},
      year={2023},
      eprint={2311.07911},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2311.07911}, 
}
```

### Contact Information
If you find something wrong or have a question about the dataset, contact snullm@aces.snu.ac.kr.
