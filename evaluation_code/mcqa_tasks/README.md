# Korean Benchmarks Evaluation

## SetUp
~~~bash
conda create -n mcqa python=3.11.8
conda activate mcqa

pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0 --index-url https://download.pytorch.org/whl/cu130

pip install transformers==5.6.2 datasets==4.8.4 accelerate==1.13.0 langdetect==1.0.9 immutabledict==4.3.1 einops==0.8.2 kernels==0.14.0 sentencepiece==0.2.1 tqdm==4.67.3 

python -m pip install -U pip setuptools wheel ninja packaging

export TMPDIR=$HOME/tmp
export TEMP=$HOME/tmp
export TMP=$HOME/tmp
python -m pip install --no-build-isolation causal-conv1d==1.6.2.post1
python -m pip install --no-build-isolation flash-linear-attention==0.5.0

# lm eval version: 0.4.12.dev0 -> editable mode
git clone https://github.com/EleutherAI/lm-evaluation-harness.git
cd lm-evaluation-harness

pip install -e .

# apply NPSQ to MCQA tasks
git checkout 95d58063
git apply ~/npsq.patch

~~~

# Run
~~~bash
cd ~
bash mcqa_tasks/run_eval.sh
~~~