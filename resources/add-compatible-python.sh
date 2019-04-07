#! /bin/bash

# Lil' script to get compatible python version on CITC
# (which is max 3.4 by default and Nornir needs at least 3.6)

curl https://pyenv.run | bash
echo 'export PATH="~/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
sudo apt-get update; sudo apt-get install -y \ 
  make build-essential libssl-dev zlib1g-dev \ 
  libbz2-dev libreadline-dev libsqlite3-dev wget \ 
  curl llvm libncurses5-dev xz-utils tk-dev \ 
  libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
pyenv install 3.7.3
git clone https://github.com/jpmondet/norniring-bgpfabric
cd norniring-bgpfabric
pyenv local 3.7.3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
