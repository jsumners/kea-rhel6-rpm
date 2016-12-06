# kea-rhel6-rpm

This project creates [ISC Kea][kea] RPMs for Red Hat Enterprise Linux 6.
It is based on the RPM spec for RHEL7 in the Fedora project.

To build RPMs using this project the build environment **must** meet the
following requirements (and, in turn, the system the RPMs are installed on):

* requires EPEL for the gtest and log4cplus packages
* requires [Red Hat Software Collections][rhscl] repository for C++11 compliant compiler
* requires [PostgreSQL 9.x repo][psql] (8.x will not work)

[kea]: http://kea.isc.org/wiki
[rhscl]: https://developers.redhat.com/products/softwarecollections/overview/
[psql]: https://www.postgresql.org/download/linux/redhat/

## Installed Services

The resulting RPMs install Upstart service configurations, not traditiona SysV
init scripts. However, the configurations are installed as `.disabled` files.
So if you want to enable the DHCPv4 Kea server you would do:

```
mv /etc/init/kea-dhcp4.conf.disabled /etc/init/kea-dhcp4.conf
```

See `man 8 initctl` for information on managing services this way.

## Database

These RPMs **do not** setup a database for you. After installation, if you
intend to use a database, instead of the in-memory storage, then you will
need to use the [kea-admin][kea-admin] tool to create, or even upgrade,
your database. The scripts are included in `/user/share/kea/scripts/`.

[kea-admin]: https://ftp.isc.org/isc/kea/1.1.0/doc/kea-guide.html#kea-admin

## License

[MIT License](http://jsumners.mit-license.org)
