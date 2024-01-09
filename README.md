# Financial Chatbot
## Description
* A chatbot for answering financial questions.
* It uses https://www.marketwatch.com/ articles as its source for information.
* It uses the TinyLlama-1.1B-Chat-v1.0 model from hugging face which can be found here: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0.
## How to run
Requires python 3.10 to run
### (Optional) Create Vitural Environment
#### Conda
```bash
conda create -n financial_chatbot python=3.10 -y
conda activate financial_chatbot
```

#### Venv
##### Create The environment
```bash
python3.10 -m venv financial_chatbot
```
##### Activate the environment
Windows:
```bash
financial_chatbot\Scripts\activate
```
macOs/Linux:
```bash
source financial_chatbot/bin/activate
```
### Install dependencies
```bash
pip install -r requirements.txt
```
### Run Streamlit app
```bash
streamlit run chatbot.py
```
