#! /usr/bin/python3

import os
import argparse
import subprocess
import paramiko

def configure_dataplane(ssh, pkt_count, reorder):
    cmd = "bash -lc \"source /home/cirlab/tools_2022-05-18/set_sde.bash; python3 /home/cirlab/mason/workspace/slb_p4/motivation/fct_recirc/cp/reorder.py --init --pkt-count {} --reorder {}\"".format(pkt_count, reorder)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    output = ssh_stdout.read().decode("utf-8")
    # print(output)
    
    with open("/tmp/run_experiment0.log", "w+") as f:
        f.write(output)
    
    # try:
    #     cmd = "ssh -t cirlab@tofino2a.d2.comp.nus.edu.sg \"source /home/cirlab/tools_2022-05-18/set_sde.bash; python3 /home/cirlab/mason/workspace/slb_p4/motivation/fct_recirc/cp/reorder.py --init --pkt-count {} --reorder {}\" > /tmp/run_experiment0.log".format(pkt_count, reorder)
    #     returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
    #     assert returned_value == 0
    # except AssertionError:
    #     with open("/tmp/run_experiment0.log") as f:
    #         data = f.read().strip()
    #     print(data)

    #     print('An error has occurred')
    #     exit(1)

def execute_client(pkt_count):
    if pkt_count == 10:
        file_to_run = '10KB.txt'
    else:
        file_to_run = '1MB.txt'

    try:
        pwd = "skychahwan"
        # cx5
        # cmd = "cd /home/mason/workspace/slb_node/simpleRDMA/; echo {} | sudo ip netns exec cwh52a bash -c \"ulimit -s unlimited; ./bin/rdma_client -a 10.4.4.9 -f /src/{} -l /log.txt -n 1\" > /tmp/run_experiment1.log && tail -n 1 log.txt > /tmp/run_experiment2.log".format(pwd, file_to_run)
        # cmd = "cd /home/mason/workspace/slb_node/simpleRDMA/; echo {} | sudo ip netns exec cwh51a bash -c \"ulimit -s unlimited; ./bin/rdma_client -a 10.4.4.15 -f /src/{} -l /log.txt -n 1\" > /tmp/run_experiment1.log && tail -n 1 log.txt > /tmp/run_experiment2.log".format(pwd, file_to_run)
        # cx6
        cmd = "cd /home/mason/workspace/slb_node/simpleRDMA/; echo {} | sudo ip netns exec cwh61a bash -c \"ulimit -s unlimited; ./bin/rdma_client -a 10.4.4.7 -f /src/{} -l /log.txt -n 1\" > /tmp/run_experiment1.log && tail -n 1 log.txt > /tmp/run_experiment2.log".format(pwd, file_to_run) 
        # cx 5 100G
        # cmd = "cd /home/mason/workspace/slb_node/simpleRDMA/; ulimit -s unlimited; ./bin/rdma_client -a 10.4.4.15 -f /src/{} -l /log.txt -n 1 > /tmp/run_experiment1.log && tail -n 1 log.txt > /tmp/run_experiment2.log".format(file_to_run) 
        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
        assert returned_value == 0
    except AssertionError:
        with open("/tmp/run_experiment0.log") as f:
            data = f.read().strip()
        print(data)

        with open("/tmp/run_experiment1.log") as f:
            data = f.read().strip()
        print(data)

        print('An error has occurred!')
        exit(1)

def extract_output(writer):
    res = []
    # read the previous rounds' packet count
    with open("/tmp/run_experiment0.log") as f:
        data = f.readlines()
    data = [ d.strip() for d in data ]
    data = [ d for d in data if '>>> ' in d ] 
    # assert len(data) == 3
    pkt_stats = [ d.split(' ')[2] for d in data ] 
    # num pkts, prev0, prev1, next0, next1
    
    with open("/tmp/run_experiment2.log") as f:
        data = f.readlines()
    lat_stats = [ d.strip() for d in data ]
    # run number, without meta, with meta

    res.extend(lat_stats)
    res.extend(pkt_stats)
    
    output = ','.join(res)
    print(output)
    writer.write(output + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--reorder', type=int, required=True, choices=[0, 1, 2],
        help='number of reorder'
    )

    parser.add_argument(
        '--pkt-count', type=int, required=True, choices=[10, 1000],
        help='pkt-count'
    )

    parser.add_argument(
        '--repeat', type=int, required=True,
        help='number of times to repeat'
    )

    args = parser.parse_args()

    reorder_count = args.reorder
    pkt_count = args.pkt_count
    repeat_count = args.repeat

    ssh = paramiko.client.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("tofino2a.d2.comp.nus.edu.sg", username="cirlab")
    
    base_file_name = 'cx6_22301004_25g_results_reorder_{}_pktCount_{}_repeat_{}.log'.format(reorder_count, pkt_count, repeat_count)
    f = open(base_file_name, 'a')

    configure_dataplane(ssh, pkt_count, reorder_count)
    for i in range(repeat_count):
        execute_client(pkt_count=pkt_count)
        configure_dataplane(ssh, pkt_count=pkt_count, reorder=reorder_count)
        extract_output(f)

    f.close()
    ssh.close()

if __name__ == '__main__':
    main()
