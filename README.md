# RDMA exmaple

A simple RDMA server client example. The code contains a lot of comments. Here is the workflow that happens in the example: 

Client: 
  1. setup RDMA resources   
  2. connect to the server 
  3. receive server side buffer information via send/recv exchange 
  4. do an RDMA write to the server buffer from a (first) local buffer. The content of the buffer is the string passed with the `-s` argument. 
  5. do an RDMA read to read the content of the server buffer into a second local buffer. 
  6. compare the content of the first and second buffers, and match them. 
  7. disconnect 

Server: 
  1. setup RDMA resources 
  2. wait for a client to connect 
  3. allocate and pin a server buffer
  4. accept the incoming client connection 
  5. send information about the local server buffer to the client 
  6. wait for disconnect

###### How to build     
```shell
git clone https://github.com/ChahwanSong/simpleRDMA.git
cd ./simpleRDMA
cmake .
make
``` 
 
#### Create 100KB dummy text file on linux
```shell
base64 /dev/urandom | head -c 100000 > 100KB.txt
```

## IMPORTANT: Enable large-file transmission
Your basic linux setup would limit the stack size to 8MB (check `ulimit -a`). To resolve it, you can use the command:
```shell
ulimit -s unlimited
```

## Running server and client
Server:
```shell
./bin/rdma_server --h
*** Start server running (infinite loop) ***

./bin/rdma_server: invalid option -- '-'
Usage:
rdma_server: [-a <server_addr>] [-p <server_port>]
(default port is 20886)
```

Client:
```shell
./bin/rdma_client --h
---Start parsing...
./bin/rdma_client: invalid option -- '-'
Usage:
rdma_client: [-a <server_addr>] [-p <server_port>] [-s string (e.g., 'test') or -f filename in /src (relative dir to current))] [-l filename to record timestamp (relative dir to current, e.g., /log.txt] [-n <number to run> - optional, default 1]
(default IP is 127.0.0.1 and port is 20886)
```

If you did not run `ulimit -s unlimited`, you may confront `Segmentation Fault` error. 

## Bash script of client
```shell
#!/bin/bash

flow_size=$1
log_filename=$2
n_run=1000

ulimit -s unlimited

/home/mason/workspace/slb_node/simpleRDMA/bin/rdma_client -a 10.2.2.2 -f "/workspace/slb_node/simpleRDMA/src/${flow_size}B.txt" -l "/workspace/slb_node/simpleRDMA/log/${flow_size}/${log_filename}" -n "${n_run}"
```

Separately, we use the following command
```shell
./bin/rdma_client -a 10.10.10.2 -f /src/100KB.txt -l /out.log -n 1
```

## Using `ib_send_bw` to test bandwidth (TODO: irrelevant with this repository)
Server runs
```shell
ib_send_bw -F -d mlx5_1 --report_gbits -D 10 -s 1000000000
```
Client runs
```shell
ib_send_bw 10.2.2.2 -F -d mlx5_1 --report_gbits -D 10 -s 1000000000
```
where the server's ip address is `10.2.2.2`. Other options are `-q` to increase throughput with more queue pairs, and `-m` for MTU size.

## Using n2disk to dump packets (TODO: irrelevant with this repository)
Before running n2disk with performance-mode, you need to set up the hugepage:
```shell
echo "[Check] ulimit -s unlimited"
ulimit -s unlimited

echo "[Check] check shared memory"
ipcs -lm

echo "[Check] hugepage setup"
sudo bash -c "echo 2048 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages"

echo "[Check] check hugepage"
numastat -cm | egrep 'Node|Huge'

echo "[Check] mounting"
sudo mkdir /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge
```

Then, you can run the following code (`/tmp` is used just to avoid permission issue)

```
sudo n2disk -i ens1f1 -o /home/mason/pcap/throughput --snaplen 90 --max-file-len 8192 --buffer-len 8192 --time-pulse 8 --reader-threads 9,10 --writer-cpu-affinity 11 --capture-direction 0
```

