# Website Installation Procedure #

The majority of these instructions can be found at www.drupal.org. However, this
document may contain any qwerks encountered during the first installation of
Drupal on this system.

## Download system requirements ##

* The Drupal CMS requires a webserver, a database, and PHP5.
* Download and install Apache2, MySQL and PHP5 with database extensions:
    * `sudo apt-get install apache2 mysql-server php5 php5-common php5-mysql php5-gd`

## Download and extract Drupal ##

* Download Drupal from the website:
    * `wget http://ftp.drupal.org/files/projects/drupal-x.x.tar.gz` (currently 7.33 in place of x.x)
    * `tar xzvf drupal-x.x.tar.gz`
    * `sudo mv drupal-x.x /var/www`

## Create the MySQL database ##

* Login to MySQL as the root user.
* Create the drupaladmin user and grant privileges:
    * `mysql -u root -p`
    * `CREATE USER 'drupaladmin'@'localhost' IDENTIFIED BY 'drupalpass'`;
    * `GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES ON drupal.* TO 'drupaladmin'@'localhost';`
* Login to MySQL as the drupaladmin and create the drupal database:
    * `CREATE DATABASE drupal CHARACTER SET utf8 COLLATE utf8_general_ci`;

## Create the settings.php file and files directory ##

* Copy sites/default/default.settings.php file to sites/defualt/settings.php in the same directory:
    * `cd /var/www/drupal-x.x`
    * `cp sites/default/default.settings.php sites/default/settings.php`

* Change permissions of the settings file during installation:
    * `chmod 666 sites/default/settings.php`

* Create the files directory and give the webuser permissions to write to it:
    * `mkdir sites/default/files`
    * `sudo chown www-data:www-data sites/default/files`

## Run the installation script ##

* Open up a browser and navigation to `hostname`/drupal-7.33 (Assuming a fresh Apache install)
* Select Standard install as the installation profile.
* Select English as the chosen language.
* Enter the database name, username, and password for the database you created earlier.
* Enter Search-Based Planning Lab as the Site name.
* Enter sbpl@sbpl.net as the Site e-mail address.
* Enter sbpl, sbpl@sbpl.net, and the standard password as the Site maintenance account
* Enter the Default country and time zone.
* Leave both boxes checked to check for updates automatically and receive e-mail notifications.

## Reset permissions correctly after installation ##

* Reset the permissions on settings.php:
    * `chmod 644 sites/default/settings.php`

## Set up cron ##

* This should be set up automatically during installation.
* Confirm that this was correctly set up by navigating to Adminstration > Configuration > System > Cron.

## Configure website-specific Apache configuration ##

* Create a Virtual Host configuration so that the website can be accessed at a different port number and document root:
    * Edit /etc/apache2/ports.conf to listen on port 21128 and define a virtual host. Place the following sometime after the definitions for port 80:
        * `NameVirtualHost *:21128`
        * `Listen 21128`
    * Create a configuration file for the Drupal website:
        * `sudo touch /etc/apache2/sites-available/drupal`
        * Edit /etc/apache2/sites-available/drupal and place the lines:

```
    <VirtualHost *:21128>
        ServerAdmin sbpl@sbpl.net
        ServerName sbpl.net

        DocumentRoot /var/www/drupal-x.x
        <Directory />
            Options FollowSymLinks
            AllowOverride None
        </Directory>

        <Directory /var/www/drupal-x.x/>
            Options Indexes FollowSymLinks MultiViews
            AllowOverride All
            Order allow,deny
            Allow from all
        </Directory>

        ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
        <Directory "/usr/lib/cgi-bin">
            AllowOverride None
            Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
            Order allow,deny
            Allow from all
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emergy.
        LogLevel warn

        CustomLog ${APACHE_LOG_DIR}/access.log combined

        Alias /doc/ "/usr/share/doc/"
        <Directory "/usr/share/doc/">
            Options Indexes MultiViews FollowSymLinks
            AllowOverride None
            Order deny,allow
            Deny from all
            Allow from 127.0.0.0/255.0.0.0 ::1/128
        </Directory>
    </VirtualHost>
```

        * Replace x.x with the version number of the website.
        * Add the available site to the enabled site configurations:
            * `sudo ln -s /etc/apache2/sites-avialable/drupal /etc/apache2/sites-enabled/drupal`
        * Restart Apache2:
            * `sudo service apache2 restart`

## Configure clean URLs ##

* Enable the Rewrite module for Apache and restart Apache:
    * `a2enmod rewrite`
    * `sudo service apache2 restart`
