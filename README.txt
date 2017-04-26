Usage steps:

1 - Open new terminal and execute following command.
memcached -p 11211

2 - Open another bar and execute following.
memcached -p 11212

If you are receiving "failed to listen on TCP port X: Address already in use" error, close all terminals and then start from step 1.

3 - Go to the main folder (where webserver.py located) and execute following.

export FLASK_APP=webserver.py

4 - Execute following command

flask run --host=0.0.0.0

If you are seeing "OSError: [Errno 48] Address already in use" error, close all terminals and then start from step 1.

5 - Open another terminal and run following command.

python observe_hits.py

That's the one who shows this: CACHE 1 : 266 | CACHE 2 : 287 | Diff : -21

6 - Open another terminal and execute following. THis command will show you how much index is recoded to the CACHE-1

watch "memdump --servers=127.0.0.1:11211 |wc -l"

7 - Open another terminal and execute following. THis command will show you how much index is recoded to the CACHE-2

watch "memdump --servers=127.0.0.1:11212 |wc -l"

8 - Open another Run following command. This will initiate all users and then starts threads who is sending GET requests to the /homepage.

python simulator.py

9 - Open another, as a final step execute following

python balancer.py

