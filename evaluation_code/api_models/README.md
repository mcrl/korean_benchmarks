# Korean Benchmarks Evaluation

## SetUp
~~~bash
conda create -n api python=3.11.8
conda activate api

pip install "lm_eval[hf,api,ifeval]==0.4.11"
~~~

# Run
~~~bash
cd ~
bash api_models/run_eval.sh
~~~
