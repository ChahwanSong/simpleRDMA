# RDMA exmaple

A simple RDMA server client example. The source codes are located in `/src`.

### Overview
The code contains a lot of comments. Here is the high-level outline of workflow: 

Server: 
  1. setup RDMA resources 
  2. wait for a client to connect 
  3. allocate and pin a server buffer
  4. accept the incoming client connection 
  5. send information about the local server buffer to the client 
  6. wait for disconnect

Client: 
  1. setup RDMA resources   
  2. connect to the server 
  3. receive server side buffer information via send/recv exchange 
  4. do an RDMA write to the server buffer from a (first) local buffer. The content of the buffer is the string passed with the `-s` argument. 
  5. do an RDMA read to read the content of the server buffer into a second local buffer. 
  6. compare the content of the first and second buffers, and match them. 
  7. disconnect 

By default, the server runs the above workflow loop infinitely. 
One workflow gives a sample of message completion time. 
Client runs a number of samples where the number will be indicated in `rdma_client` command.


### How to build
This repository requires `CMake>=2.6`. To build, use the commands:
```shell
cmake .; make;
``` 
We provide a bash script `./clear.sh` to clean up all binary/log files.

### Preliminary 1: Crate message-file to send
You can create a dummy text file on linux using the following command:
```shell
base64 /dev/urandom | head -c 100000 > 100KB.txt
```
The option `-c` indicates the size of file to write. Later, RDMA client will send the file. 
Put the output files to the directory `/src`.

### Preliminary 2: To enable large-file transmission
Your basic linux setup would limit the stack size to 8MB (check `ulimit -a`). To resolve it, you can use the command:
```shell
ulimit -s unlimited
```
If you did not run `ulimit -s unlimited`, you may confront `Segmentation Fault` error. 


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
rdma_client: [-a <server_addr>] [-p <server_port>] [-s string (e.g., 'test') or -f filename in /src (relative dir to current))] [-l filename to record timestamp (relative dir to current, e.g., /out.dat] [-n <number to run> - optional, default 1]
(default IP is 127.0.0.1 and port is 20886)
```

Here are example commands. Suppose you have two RDMA nodes:
* client with ip `10.2.2.1`, and
* server with ip `10.2.2.2`.

First, run the RDMA server:
```shell
./bin/rdma_server -a 10.2.2.2
```

Next, run the RDMA client:
```shell
./bin/rdma_client -a 10.2.2.2 -f /src/24387B.txt -l /log/out.dat -n 100
```
which sends a message of size 24387B to the server `10.2.2.2` and repeat it 100 times, and output log is written to `log/out.dat`.

### Output format
Here is the example output:
```shell
268,15693
269,15889
270,15964
271,15933
...
```
The first column is queue-pair number, and the second column is the message completion time measured at client based on _queue completion events_.

To get the CDF of output values, run `getCDF.py -name {output log filename, e.g., log/out.dat}`. 