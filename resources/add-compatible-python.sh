#! /bin/bash

# Lil' script to get compatible python version on CITC
# (which is max 3.4 by default and Nornir needs at least 3.6)

curl https://pyenv.run | bash
wait
echo 'export PATH="~/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
. ~/.bashrc
wait
if grep -q "stable" /etc/apt/apt.conf.d/00local
then
  sed -i 's/stable/jessie/g' /etc/apt/apt.conf.d/00local
fi
wait
sudo apt-get update; sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev python-openssl python3-openssl
wait
pyenv install 3.7.3
wait
git clone https://github.com/jpmondet/norniring-bgpfabric
wait
cd norniring-bgpfabric
wait
pyenv local 3.7.3
wait
python -m venv venv
wait
. venv/bin/activate
wait
git checkout upgrade_to_nornir3
wait
pip install -r requirements.txt
