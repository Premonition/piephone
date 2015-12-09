IP='192.168.86.166'
scp phone.py dialtone.mp3 *press.mp3 ring.mp3 phone.service pi@$IP:
ssh pi@$IP 'sudo cp phone.service /etc/systemd/system/phone.service; sudo systemctl daemon-reload; sudo systemctl restart phone'
