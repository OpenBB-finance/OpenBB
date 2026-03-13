# OBB Dataflow Sample

This is a sample on how to invoke OBB fetchers in an Apache Beam pipeline. (GCP Dataflow is built on Apache Beam)

Pre-requisites
- You need to create a Conda environment (or a virtual env) using `requirements.txt` in this directory
- The script exercises three OBB endpoints, all of which require no credentials
- Run the test from this directory:
  cd examples/openbb-apachebeam
  python -m unittest tests/test_obb_pipeline.py

The script will run a pipeline consisting of three tasks which will fetch an AAPL quote, profile, and news.
This is just a very basic sample which can be used as a building block to create more complex scenarios
