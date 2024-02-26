source venv/bin/activate
sudo python3 server.py

Here's the steps to get this project running on your local machine.

1 - make sure you have Python3 installed with pip.

2 - pip install the following packages:

pip install flask <br />
pip install flask-restful <br />
pip install flask-cors <br />
pip install mysql-connector-python <br />

3 - install MySQL client and server.

4 - create a MySQL database using the createWordDB.sql file. <br />
(if you are having trouble with this part, check creating database with python below)

5 - run the MySQL server with user=root, no password, localhost

6 - on your terminal go to the project folder and run this command: <br />
sudo run python3 server.py

7 - on your browser go to http://localhost:5000/

Python NOTES:

You can (optionally) pass 3 database arguments when calling server.py. <br />
sudo run python3 user password host server.py <br />
ex: sudo run python3 root somePassword localhost server.py

Aditionally you can also pass 2 arguments arguments to change the server address. <br />
If you do so you HAVE to pass the 3 database aguments. <br />
sudo run python3 user password host ip host server.py <br />
ex: sudo run python3 root somePassword localhost 192.168.86.78 5000 server.py

MySQL NOTES:

You might need to install mysql on your Linux system, try: <br />
sudo apt-get install -y mysql-server mysql-client

You also might need to set your mysql password. <br />
If you do so, make sure to pass your new password as an argument to server.py

To start mysql: <br />
sudo service mysql start

CREATING DATABASE WITH PYTHON

You can try using the database_setup.py if you don't know how to use createWordDB.sql file. <br />
first, make sure mysql is running, then run this command: <br />
python3 database_setup.py user password host <br />
make sure you replace user, password and host with the ones from mysql.
