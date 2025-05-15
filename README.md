# korean_benchmarks
## Translation Process of the Dataset

The translation process consisted of four key stages:

### 1. Initial Translation
- Used **DeepL API** to machine-translate English benchmark datasets into Korean.

### 2. Correction
Domain experts corrected machine translation errors, including:
- Fixing original English data errors (e.g., typos, duplicate questions, mislabeled answers).
- Refining unnatural literal translations and correcting mistranslations.
- Ensuring consistent tone and style within each item.
- Standardizing translated terminology  

### 3. Localization
Adjusted content to reflect Korean cultural context:
- Replaced foreign names, units, and cultural concepts with Korean equivalents  

### 4. Cross-review
- An independent reviewer, not involved in steps 2 or 3, validated and refined the corrected content to ensure high quality.
## Dataset Instance Examples

## Development Process of the Dataset

### LAMBADA

The LAMBADA dataset was developed to assess models’ contextual understanding using Korean literary texts.  
Due to linguistic and stylistic differences, it was created from scratch rather than translating English sources.

#### 1. Data Collection & Preprocessing
- Collected copyright-free Korean literary works and speeches from public sources (from [공유마당](https://gongu.copyright.or.kr/gongu/main/main.do)).
- Automatically selected candidate passages that:
  - Were sufficiently long.
  - Contained keywords repeated more than once.

#### 2. Initial Data Generation
- Removed a repeated noun from the final sentence of each selected passage to create a blank.
- Marked the removed word as the **answer**, and listed other words in context as **candidates**.

#### 3. Editing & Correction
- Ensured natural grammar around the blank (e.g., handling postpositions).
- Modified or removed questions with multiple valid answers or unclear context.

#### 4. Cross-review
- A second reviewer verified and corrected remaining issues for quality assurance.

### IFEval

The IFEval dataset was designed to evaluate instruction-following in Korean, with both translated and newly created tasks.

#### 1. Data Collection & Preprocessing
- Collected diverse text sources including presidential speeches.
- Categorized instruction types (e.g., forbidden words, structure constraints).

#### 2. Initial Data Generation
- Created prompts in Korean aligned with instruction-following evaluation formats.
- Carefully designed constraints using Korean syntax and cultural norms (e.g., avoiding certain words or using specific syllables).

#### 3. Editing & Correction
- Unified tone, formality, and formatting.
- Refined ambiguous or contradictory prompts.

#### 4. Cross-review
- Conducted peer review to ensure consistency and eliminate residual issues.



## 📊 Table 1. Datasets Composition

| Benchmark         | Evaluation Task                                  | Data Size                                       | Creation Method       | Columns                                           | Available at                                                                 |
|-------------------|---------------------------------------------------|--------------------------------------------------|------------------------|---------------------------------------------------|------------------------------------------------------------------------------|
| Korean ARC        | Science Knowledge Q&A                            | 3,543 (easy: 2,376, challenge: 1,167)            | Translation            | `id`, `question`, `choices`, `answerKey`          | [link](https://huggingface.co/datasets/Yeonkyoung/ko_arc)                   |
| Korean GSM8K      | Math Problem Solving                              | 1,319                                            | Translation            | `question`, `answer`                              | [link](https://huggingface.co/datasets/Yeonkyoung/ko_gsm8k)                 |
| Korean EQ-Bench   | Dialogue Sentiment Analysis                       | 171                                              | Translation            | `prompt`, `reference_answer`, `reference_answer_fullscale` | [link](https://huggingface.co/datasets/Yeonkyoung/ko_eqbench)              |
| Korean Winogrande | Logical/Contextual Reasoning and Word Prediction | 1,267                                            | Translation            | `sentence`, `option1`, `option2`, `answer`        | [link](https://huggingface.co/datasets/Yeonkyoung/ko_winogrande)           |
| Korean LAMBADA    | Literary Context Understanding and Word Prediction| 2,255                                            | Development            | `index`, `text`, `answer`, `candidate`            | [link](https://huggingface.co/datasets/Yeonkyoung/snu_lambada)             |
| Korean IFEval     | Instruction Following                             | 841 (Translation: 541, Development: 300)         | Translation, Development | `key`, `prompt`, `instruction_id_list`, `kwargs` | [link](https://huggingface.co/datasets/Yeonkyoung/ko_ifeval)               |
| **Total**         |                                                   | **9,396**                                        |                        |                                                   |                                                                              |

You can find examples in the `samples` folder.

## Additional Information
### Access to the Dataset

To access the dataset, you will need to submit an access request via huggingface.   
This is to prevent the evaluation set—currently the only portion in this page—from being used for training, as open datasets are often scraped indiscriminately.

> We are preparing the access form and it will be available soon. Please bear with us a little longer.

### Upcoming Paper

A detailed paper describing the dataset construction process and benchmark results is **coming soon**.  
Stay tuned for the publication!

### To Cite this Github Repository
```
@misc{mcrlkorean2025,
  title        = {Korean Benchmarks},
  author       = {Thunder Research Group},
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
