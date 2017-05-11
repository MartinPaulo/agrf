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
    ```
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
pip install django
django-admin --version
pip install -r requirements.txt
cp agrf/local_settings_template.py agrf/local_settings.py
vi agrf/local_settings.py
# and in this file set
    SECRET_KEY = 'Some long garbage string' # http://www.miniwebtool.com/django-secret-key-generator/ - of course, this is 'known'...
    ALLOWED_HOSTS = ['115.146.95.86'] # the ip number of the host
    TRUST_ROOT = 'http://115.146.95.86/' # again, ip number of the host
    CMD_ENVIRONMENT = 'source /home/ec2-user/agrf/v_agrf/bin/activate;'
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
# The /etc/httpd/conf.d/django.conf file contents is between the "#=== lines"
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

# and if you want a file to download...
mkdir ~/pictures
cd ~/pictures
wget "https://upload.wikimedia.org/wikipedia/commons/e/ef/Flickr_-_Lukjonis_-_Male_Jumping_spider_-_Evarcha_arcuata_%28Set_of_pictures%29.jpg"
mv Flickr_-_Lukjonis_-_Male_Jumping_spider_-_Evarcha_arcuata_\(Set_of_pictures\).jpg spider.jpg
```
</details>