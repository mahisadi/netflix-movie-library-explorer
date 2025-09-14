
# netflix-movie-library-connector

This module fetch content from source google_drive. Can be leveraged into fetch from different sources such as servicenow, git, dynamodb, s3, wiki as we needed.


It containerized and run for the specific source.



## Prepare

Set up a virtual environment (using latest Python 3 + `venv` module):

```shell
# for root project
python -m venv .venv

Install project dependencies:

```shell
# for root project
source .venv/bin/activate
pip install -r requirements.txt