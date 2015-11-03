import os

# This will establish a local tunnel to our mongodb at local port 6789!!!!
bashCommand = "python -m sshtunnel -K ~/.ssh/id_rsa -U pi -L :6789 -R 127.0.0.1:27017 -p 8022 chrisfrew.in"
os.system(bashCommand)
