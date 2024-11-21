sudo systemctl start ank-server
nohup ank-agent -k --name agent_A --server-url http://192.168.1.99:25551 &
