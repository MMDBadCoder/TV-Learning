sudo apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt-get install ffmpeg

sudo apt install ufw -y
sudo ufw allow 80
sudo ufw allow 22
sudo ufw allow 2280
sudo ufw allow 8080
for port in $(cat /etc/ssh/sshd_config | grep "^Port" | cut -d' ' -f2); do
  sudo ufw allow $port
done
echo 'y' | sudo ufw enable
