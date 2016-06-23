import paramiko
import sys
import paramikoWrapper as wrapper

miners_farm1 = [1,3,4,5,6,7,8]
miners_farm2 = [i for i in range(14,39)]
miners_all = miners_farm1 + miners_farm2

def command_one(num, command):
  res = None
  # res = command_ssh("onther.iptime.org", 50000+int(num), "miner"+str(num) ,"rlagnlrud", command)
  cli = wrapper.SSHClient("onther.iptime.org", 50000+int(num), "miner"+str(num), password="rlagnlrud")
  if command.startswith("sudo"):
    res = cli.execute(command, sudo=True)
    cli.close()
    print num, [result.strip("\n") for result in res["out"]]
    return [result.strip("\n") for result in res["out"]]
  res = cli.execute(command)
  cli.close()
  print num, [result.strip("\n") for result in res["out"]]
  return [result.strip("\n") for result in res["out"]]


if __name__ == "__main__":
  miner_num = sys.argv[1]
  command = sys.argv[2]
  command_one(miner_num , command)
