# OBB Dataflow Sample


This is a sample how to  invoke OBB fetchers in an Apache Beam pipeline. (GCP dataflow is build on Apache Beam)
Pre-requisites
- You need to create a Conda environment (or a virtual env) using requirements.txt in this directory
- The script exercise 3 OBB endpoints, all of which require no credentials
- Run the test from the main directory
  python -m unittest .\tests\test_obb_pipeline.py

The script will run a pipeline consisting of 3 task which will fetch AAPL quote, profile and news
This is just a very basic sample which can be used as building block to create more complex scenarios
