# Korean Benchmarks

## Summary
**Snu-Benchmarks** is a collection of Korean benchmark datasets designed to evaluate language models in a wide range of tasks. 
It includes six datasets that are either translated or newly constructed to align with Korean language and cultural context.

All datasets underwent a four-step construction process to ensure high linguistic and logical quality:  
1. **Initial Translation or Generation**  
2. **Expert Correction**  
3. **Localization**  
4. **Independent Cross-review**

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
| Snu-ARC        | Science Knowledge Q&A                            | 3,543 (easy: 2,376, challenge: 1,167)            | Translation            | `id`, `question`, `choices`, `answerKey`          | [link](https://huggingface.co/datasets/thunder-research-group/snu_arc)                   |
| Snu-GSM8K      | Math Problem Solving                              | 1,319                                            | Translation            | `question`, `answer`                              | [link](https://huggingface.co/datasets/thunder-research-group/snu_gsm8k)                 |
| Snu-EQ-Bench   | Dialogue Sentiment Analysis                       | 171                                              | Translation            | `prompt`, `reference_answer`, `reference_answer_fullscale` | [link](https://huggingface.co/datasets/thunder-research-group/snu_eqbench)              |
| Snu-WinoGrande | Logical/Contextual Reasoning and Word Prediction | 1,267                                            | Translation            | `sentence`, `option1`, `option2`, `answer`        | [link](https://huggingface.co/datasets/thunder-research-group/snu_winogrande)           |
| Snu-LAMBADA    | Literary Context Understanding and Word Prediction| 2,255                                            | Development            | `index`, `text`, `answer`, `candidate`            | [link](https://huggingface.co/datasets/thunder-research-group/snu_lambada)             |
| Snu-IFEval     | Instruction Following                             | 841 (Translation: 541, Development: 300)         | Translation, Development | `key`, `prompt`, `instruction_id_list`, `kwargs` | [link](https://huggingface.co/datasets/thunder-research-group/snu_ifeval)               |
| **Total**         |                                                   | **9,396**                                        |                        |                                                   |                                                                              |

You can find examples in the `samples` folder.

---

## How to Use (via Hugging Face `datasets`)

```python
from datasets import load_dataset

# Snu-IFEval
snu_ifeval = load_dataset("Yeonkyoung/ko_ifeval")

# Snu-ARC
snu_arc_c = load_dataset("thunder-research-group/snu_arc", "challenge")
snu_arc_e= load_dataset("thunder-research-group/snu_arc", "easy")

# Snu-GSM8K
snu_gsm8k = load_dataset("thunder-research-group/snu_gsm8k")

# Snu-EQ-Bench
snu_eqbench = load_dataset("thunder-research-group/snu_eqbench")

# Snu-Winogrande
snu_winogrande = load_dataset("thunder-research-group/snu_winogrande")

# Snu-LAMBADA
snu_lambada = load_dataset("thunder-research-group/snu_lambada")
```

---

## Additional Information

### Cite as
```
@misc{mcrlkorean2025,
  title        = {Korean Benchmarks},
  author       = {{Thunder Research Group}},
  howpublished = {\url{https://github.com/mcrl/korean_benchmarks}},
  year         = {2025},
  note         = {GitHub repository}
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
@InProceedings{ai2:winogrande,
title = {WinoGrande: An Adversarial Winograd Schema Challenge at Scale},
authors={Keisuke, Sakaguchi and Ronan, Le Bras and Chandra, Bhagavatula and Yejin, Choi
},
year={2019}
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
If you find something wrong or have question about the dataset, contact snullm@aces.snu.ac.kr.
