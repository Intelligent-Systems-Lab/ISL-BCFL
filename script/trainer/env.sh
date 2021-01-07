apt-get update && apt-get -y upgrade
apt-get install -y python3-pip virtualenv
pip3 install --upgrade pip
# pip3 install jupyter

virtualenv --system-site-packages -p python3 ~/isltrainer
source ~/isltrainer/bin/activate

pip3 install -r requirements.txt


echo "pytorch version"
python -c "import torch; print(torch.__version__)"

deactivate

echo "Install Finish!!!"