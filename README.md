# AGRF GenomeSpace data importer

A Django based GenomeSpace Tool that allows users to import files into the
GenomeSpace

<details>
    <summary>Still under development</summary>

<img src="http://www.textfiles.com/underconstruction/CoCollegeParkGym4011Construction.gif">
You have been warned!

</details>

<details>
    <summary>Notes</summary>

```bash
mkfile -n 1g ~/Desktop/LargeTestFile # Make a large file under osx
cmp --silent $old $new || echo "files are different" # Compare two files under osx
fallocate -l 10G test.txt # make a large file under linux
```

http://docs.celeryproject.org/en/3.1/tutorials/daemonizing.html

When developing, start rabbitmq & celery:

    rabbitmq-server
    
    celery -A agrf_feed worker -l info

</details>

<details>
    <summary>Installation instructions for CentOS 6.8</summary>
 
 ```bash
 # update virgin instance
sudo yum -y update

# install required python libraries
sudo yum -y install epel-release
sudo yum -y install python34 python-pip
sudo pip install --upgrade pip
sudo pip install virtualenv

# install apache & git
sudo yum -y install httpd mod_wsgi git

# now get latest mod_wsgi and compile to run with with python34, then install
wget "https://github.com/GrahamDumpleton/mod_wsgi/archive/4.5.15.tar.gz"
tar -xzf '4.5.15.tar.gz'
cd mod_wsgi-4.5.15/
sudo yum -y install httpd-devel
sudo yum -y groupinstall "Development tools"
sudo yum -y -q install zlib2-devel openssl-devel sqlite-devel bzip2-devel python-devel openssl-devel openssl-perl libjpeg-turbo libjpeg-turbo-devel zlib-devel giflib ncurses-devel gdbm-devel xz-devel tkinter readline-devel tk tk-devel kernel-headers glibc libpng gcc-c++ python34-devel
./configure -with-python=/usr/bin/python3.4
make
sudo make install

# install the application
cd ~
git clone https://github.com/MartinPaulo/agrf.git
cd agrf
virtualenv -p python3 v_agrf
source v_agrf/bin/activate
pip install django # could take from requirments.txt...
# check that it works
django-admin --version
pip install -r requirements.txt
cp agrf/local_settings_template.py agrf/local_settings.py
vi agrf/local_settings.py
# and in this file set
    SECRET_KEY = 'Some long garbage string' # http://www.miniwebtool.com/django-secret-key-generator/ - of course, this is 'known'...
    ALLOWED_HOSTS = ['115.146.95.86'] # the ip number of the host
    TRUST_ROOT = 'http://115.146.95.86/' # again, ip number of the host
    BASE_DIRECTORY = '/home/ec2-user/pictures' # where ever your files are
python manage.py migrate
# to test all is ok... Ctrl-C to kill, btw.
python manage.py runserver

# setup the admin user
./manage.py createsuperuser

# collect the static files into the static files directory
sudo mkdir /var/www/static
sudo chown ec2-user:ec2-user /var/www/static/
./manage.py collectstatic
sudo chown root:root -R  /var/www/static/

# setup the apache server
sudo vi /etc/httpd/conf.d/django.conf
# The /etc/httpd/conf.d/django.conf file contents is between the "#===" lines below
```

```
#==============================================================================
Alias /static /var/www/static
<Directory /var/www/static>
   Satisfy any
</Directory>

<Directory /home/ec2-user/agrf/agrf>
    <Files wsgi.py>
        Satisfy any
    </Files>
</Directory>

WSGISocketPrefix /var/run/wsgi
WSGIDaemonProcess agrf python-path=/home/ec2-user/agrf:/home/ec2-user/agrf/v_agrf/lib/python3.4/site-packages
WSGIProcessGroup agrf
WSGIScriptAlias / /home/ec2-user/agrf/agrf/wsgi.py
#==============================================================================
```

```bash
# set the needed groups and file permissions
sudo usermod -a -G ec2-user apache
chmod 664 db.sqlite3
sudo chown :apache db.sqlite3
sudo chown :apache ~/agrf/
chmod 774 ~/agrf
chmod 710 /home/ec2-user/

# need to give wsgi a directory it can keep its locks in
sudo mkdir /var/run/wsgi
sudo chown :apache /var/run/wsgi/

# to tell apache who it is:
sudo vi /etc/httpd/conf/httpd.conf
# and set the ServerName to be the ip number of the host.

# test the whole setup...
sudo apachectl configtest
sudo apachectl start

# to get apache to restart when vm is rebooted:
sudo chkconfig httpd on

# setup pam access
sudo groupadd agrfshadow
sudo usermod -aG agrfshadow apache
sudo chgrp agrfshadow /etc/shadow
sudo chmod g+r /etc/shadow
# and check it looks ok...
sudo stat -c "%U %G" /etc/shadow
# restart apache to pick it up
sudo apachectl restart

# to upload files in the background...
# install rabbitmq
sudo yum -y install rabbitmq-server
sudo /sbin/service rabbitmq-server start
sudo chkconfig rabbitmq-server on
sudo rabbitmqctl add_user [rabbit_user] [rabbit_user_password]
sudo rabbitmqctl add_vhost agrfvhost
sudo rabbitmqctl set_user_tags [rabbit_user] agrftag
sudo rabbitmqctl set_permissions -p agrfvhost [rabbit_user] ".*" ".*" ".*"

# to set up celery (try version 4.0?)
wget https://raw.githubusercontent.com/celery/celery/3.1/extra/generic-init.d/celeryd
sudo mv celeryd /etc/init.d/celeryd
sudo chown root:root /etc/init.d/celeryd
sudo chmod +x /etc/init.d/celeryd
# create the config file
sudo vi /etc/default/celeryd
# and put the following into it:
```

```bash
# Names of nodes to start
#   most people will only start one node:
CELERYD_NODES="worker1"
#   but you can also start multiple and configure settings
#   for each in CELERYD_OPTS
#CELERYD_NODES="worker1 worker2 worker3"
#   alternatively, you can specify the number of nodes to start:
#CELERYD_NODES=10

# Absolute or relative path to the 'celery' command:
#CELERY_BIN="/usr/local/bin/celery"
CELERY_BIN="/home/ec2-user/agrf/v_agrf/bin/celery"

# App instance to use
# comment out this line if you don't use an app
CELERY_APP="agrf_feed"
# or fully qualified:
#CELERY_APP="proj.tasks:app"

# Where to chdir at start.
CELERYD_CHDIR="/home/ec2-user/agrf"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8"
# Configure node-specific settings by appending node name to arguments:
#CELERYD_OPTS="--time-limit=300 -c 8 -c:worker2 4 -c:worker3 2 -Ofair:worker1"

# Set logging level to DEBUG
CELERYD_LOG_LEVEL="DEBUG"

# %n will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"

# Workers should run as an unprivileged user.
#   You need to create this user manually (or you can choose
#   a user/group combination that already exists (e.g., nobody).
CELERYD_USER="ec2-user"
CELERYD_GROUP="ec2-user"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1
```

```bash
# to run celery in the background
sudo chkconfig --add celeryd
# start celery
sudo /etc/init.d/celeryd start
# to check the status of celery...
sudo /etc/init.d/celeryd status

# and if you want a file to download...
mkdir ~/pictures
cd ~/pictures
wget "https://upload.wikimedia.org/wikipedia/commons/e/ef/Flickr_-_Lukjonis_-_Male_Jumping_spider_-_Evarcha_arcuata_%28Set_of_pictures%29.jpg"
mv Flickr_-_Lukjonis_-_Male_Jumping_spider_-_Evarcha_arcuata_\(Set_of_pictures\).jpg spider.jpg
```

To set up a self signed certificate follow:

* https://www.digitalocean.com/community/tutorials/how-to-create-a-ssl-certificate-on-apache-for-centos-6

Then, to get apache to redirect to https, add the following lines to the end of
`/etc/httpd/conf/httpd.conf`:

```
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI}
```

Possibly want to make the `%{REQUEST_URI}` be `%{REQUEST_URI} [R=302,L,QSA]`
</details>


<details>
    <summary>SELinux</summary>
    
The following might be handy if selinux is in use:

```bash
# enable apache to read the application files and default files directory
semanage fcontext -a -t httpd_sys_content_t "/home/noisyroom/agrf(/.*)?" 
semanage fcontext -a -t httpd_sys_content_t "/home/noisyroom/default(/.*)?"
restorecon -r -v /home/noisyroom

# enable apache to read the users home directories
semanage fcontext -a -t httpd_sys_content_t "/ftp-home(/.*)?"
restorecon -r -v /ftp-home

# https://www.centos.org/docs/5/html/5.2/Deployment_Guide/sec-sel-enable-disable-enforcement.html
sestatus | grep -i mode
setenforce 0    # make permissive
setenforce 1    # make enforcing
ls -Z   /somedirectory # see the selinux labels
sestatus -b | grep httpd # see the values of the boolean flags for httpd

setsebool -P httpd_tmp_exec 1 # allow apache to access the tmp directory
setsebool -P allow_httpd_mod_auth_pam 1 # allow apache to use pam
setsebool -P httpd_can_network_connect 1 # not needed as following line is better
semanage port -m -t http_port_t -p tcp 5672 # allow apache to connect to rabbit

semodule -DB # to disable dontaudit settings
semodule -B # to reenable dontaudit settings
```

</details>

<details>
    <summary>Todo after handover</summary>

* Use the actual production versions of python-genomespaceclient and 
  cloudbridge. We are currently downloading and using custom versions of these
  libraries, as they hadn't been released with the features we needed.
* Switch the database from being an sqlite one in the same directory as the 
  application to either being in a separate directory, or a properly installed
  database such as mysql.
* Improve the logging: currently we write to the apache log files, and we don't
  do things such as rotating the logs etc... We should manage them all a little
  better - and be able to set the log levels.
* Change the password reset process...
* Possibly add 403.html and 400.html error pages.
* Sort out the genomespace deleting of large files (doesn't work for our 
  uploads...)
* Test harness needs to be built...

</details>
