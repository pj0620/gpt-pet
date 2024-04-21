from subprocess import Popen

from daemon import daemon


def start_manual_daemon():
  with daemon.DaemonContext():
    # Assuming manual.py is in the same directory as this script
    Popen(['python', 'manual.py'])
    
if __name__ == "__main__":
    start_manual_daemon()
    
    # /home/gptpetclient/launch.sh