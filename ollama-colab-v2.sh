# Free GPU's for everyone! Run Ollama on Google Colab by running only this script by running the curl a few lines below. 

# Execute this script by running the following command in Jupyther Notebook (Google Collab):
# !curl -fsSL https://molodetz.nl/retoor/uberlama/raw/branch/main/ollama-colab-v2.sh | sh

# Install Ollama.
curl -fsSL https://ollama.com/install.sh | sh

# Your model.
ollama pull qwen2.5-coder:14b

# Start Ollama on the background.
nohup ollama serve > ollama.log 2>&1 &

# Install the ollama molodetz client to publish your model to uberlama.
pip install aiohttp
wget https://retoor.molodetz.nl/retoor/uberlama/raw/branch/main/client.py
nohup python client.py > client.log 2>&1 &

# Keep process active. Display output in dem Jupyter Notebook.
tail -f *.log

# You can use the original Ollama / any OpenAI client (JS / Python whatever).
# All you have to do is change server to https://ollama.molodetz.nl.
# And configure it to use the model name above ofcourse!
#
# Test your model quickly by changing model name in the curl command below.
# curl https://ollama.molodetz.nl/v1/completions \
#  -H "Content-Type: application/json" \
#  -d '{
#    "model": "qwen2.5:0.5b",
#    "prompt": "What is Molodetz?"
#  }'
#
# Retoor.
