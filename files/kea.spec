# Started from the spec at http://pkgs.fedoraproject.org/cgit/rpms/kea.git/tree/
#%%global VERSION %%{version}-%%{patchver}
#%%global VERSION %%{version}-%%{prever}
%global VERSION %%{version}

Summary:  DHCPv4, DHCPv6 and DDNS server from ISC
Name:     kea
Version:  1.1.0
Release:  1%{?dist}
License:  MPLv2.0 and Boost
URL:      http://kea.isc.org
Source0:  http://ftp.isc.org/isc/kea/%{VERSION}/%{name}-%{VERSION}.tar.gz
Source1:  kea-dhcp4.conf.disabled
Source2:  kea-dhcp6.conf.disabled
Source3:  kea-dhcp-ddns.conf.disabled

# autoreconf
BuildRequires: autoconf automake libtool
BuildRequires: boost-devel
# %%configure --with-openssl
BuildRequires: openssl-devel
# %%configure --with-dhcp-mysql
BuildRequires: mysql-devel
# %%configure --with-dhcp-pgsql
BuildRequires: postgresql-devel
BuildRequires: log4cplus-devel
%ifnarch s390 %{mips}
BuildRequires: valgrind-devel
%endif
# src/lib/testutils/dhcp_test_lib.sh

# %%configure --with-gtest
BuildRequires: gtest-devel

# in case you ever wanted to use %%configure --enable-generate-parser
#BuildRequires: flex bison

# in case you ever wanted to use %%configure --enable-generate-docs
#BuildRequires: elinks asciidoc plantuml

Requires: kea-libs%{?_isa} = %{version}-%{release}


%description
DHCP implementation from Internet Systems Consortium, Inc.
that features fully functional DHCPv4, DHCPv6 and Dynamic DNS servers.
Both DHCP servers fully support server discovery,
address assignment, renewal, rebinding and release. The DHCPv6
server supports prefix delegation. Both servers support DNS Update
mechanism, using stand-alone DDNS daemon.

%package libs
Summary: Shared libraries used by Kea DHCP server

%description libs
This package contains shared libraries used by Kea DHCP server.

%package devel
Summary: Development headers and libraries for Kea DHCP server
Requires: kea-libs%{?_isa} = %{version}-%{release}
# to build hooks (#1335900)
Requires: boost-devel

%description devel
Header files and API documentation.

%prep
%setup -q -n kea-%{VERSION}

# install leases db in /var/lib/kea/ not /var/kea/
# http://kea.isc.org/ticket/3523
sed -i -e 's|@localstatedir@|@sharedstatedir@|g' src/lib/dhcpsrv/Makefile.am

# to be able to build on ppc64(le)
# https://sourceforge.net/p/flex/bugs/197
# https://lists.isc.org/pipermail/kea-dev/2016-January/000599.html
sed -i -e 's|ECHO|YYECHO|g' src/lib/eval/lexer.cc

%build
autoreconf --verbose --force --install
export CXXFLAGS="%{optflags} -std=gnu++11 -Wno-deprecated-declarations"

%configure \
    --disable-dependency-tracking \
    --disable-rpath \
    --disable-silent-rules \
    --disable-static \
    --enable-debug \
    --with-dhcp-mysql \
    --with-dhcp-pgsql=/usr/pgsql-~pgVersion~/bin/pg_config \
    --with-gnu-ld \
    --with-log4cplus \
    --with-openssl \
#    --with-gtest

make %{?_smp_mflags}


%check
#make check

%install
make DESTDIR=%{buildroot} install %{?_smp_mflags}

# Get rid of .la files
find %{buildroot} -type f -name "*.la" -delete -print

# Copy Upstart configs
%{__install} -d 0755 %{buildroot}%{_sysconfdir}/init
%{__install} -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/init/
%{__install} -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/init/
%{__install} -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/init/

# Start empty lease databases
mkdir -p %{buildroot}%{_sharedstatedir}/kea/
touch %{buildroot}%{_sharedstatedir}/kea/kea-leases4.csv
touch %{buildroot}%{_sharedstatedir}/kea/kea-leases6.csv

rm -f %{buildroot}%{_pkgdocdir}/COPYING

mkdir -p %{buildroot}/run
install -d -m 0755 %{buildroot}/run/kea/


%post

%preun
[ -f /etc/init/kea-dhcp4.conf ] && initctl stop kea-dhcp4
[ -f /etc/init/kea-dhcp6.conf ] && initctl stop kea-dchp6
[ -f /etc/init/kea-dhcp-ddns.conf ] && initctl stop kea-dchp-ddns

%postun
[ -f /etc/init/kea-dhcp4.conf ] && mv /etc/init/kea-dhcp4.conf /etc/init/kea-dhcp4.conf.rpmsave
[ -f /etc/init/kea-dhcp6.conf ] && mv /etc/init/kea-dhcp6.conf /etc/init/kea-dhcp6.conf.rpmsave
[ -f /etc/init/kea-dhcp-ddns.conf ] && mv /etc/init/kea-dhcp-ddns.conf /etc/init/kea-dhcp-ddns.conf.rpmsave
[ -f /etc/init/kea-dhcp4.conf.disabled ] && rm -f /etc/init/kea-dhcp4.conf.disabled
[ -f /etc/init/kea-dhcp6.conf.disabled ] && rm -f /etc/init/kea-dhcp6.conf.disabled
[ -f /etc/init/kea-dhcp-ddns.conf.disabled ] && rm -f /etc/init/kea-dhcp-ddns.conf.disabled


%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files
%{_sbindir}/kea-admin
%{_sbindir}/kea-dhcp-ddns
%{_sbindir}/kea-dhcp4
%{_sbindir}/kea-dhcp6
%{_sbindir}/kea-lfc
%{_sbindir}/keactrl
%{_sbindir}/perfdhcp
%{_bindir}/kea-msg-compiler
%{_sysconfdir}/init/kea-dhcp4.conf.disabled
%{_sysconfdir}/init/kea-dhcp6.conf.disabled
%{_sysconfdir}/init/kea-dhcp-ddns.conf.disabled
%dir %{_sysconfdir}/kea/
%config(noreplace) %{_sysconfdir}/kea/kea.conf
%config(noreplace) %{_sysconfdir}/kea/keactrl.conf
%dir %{_datarootdir}/kea/
%{_datarootdir}/kea/scripts
%dir /run/kea/
%{_datarootdir}/kea/dhcp-ddns.spec
%{_datarootdir}/kea/dhcp4.spec
%{_datarootdir}/kea/dhcp6.spec
%dir %{_sharedstatedir}/kea
%config(noreplace) %{_sharedstatedir}/kea/kea-leases4.csv
%config(noreplace) %{_sharedstatedir}/kea/kea-leases6.csv
%{_docdir}/%{name}/AUTHORS
%{_docdir}/%{name}/ChangeLog
%{_docdir}/%{name}/README
%{_docdir}/%{name}/examples
%{_docdir}/%{name}/kea-guide.*
%{_docdir}/%{name}/kea-logo-100x70.png
%{_docdir}/%{name}/kea-messages.html
%{_mandir}/man8/kea-admin.8.gz
%{_mandir}/man8/kea-dhcp-ddns.8.gz
%{_mandir}/man8/kea-dhcp4.8.gz
%{_mandir}/man8/kea-dhcp6.8.gz
%{_mandir}/man8/kea-lfc.8.gz
%{_mandir}/man8/keactrl.8.gz
%{_mandir}/man8/perfdhcp.8.gz

%files libs
#%%dir %%{_pkgdocdir}/
#%%{_pkgdocdir}/COPYING
#%%{_pkgdocdir}/LICENSE_1_0.txt
%{_docdir}/%{name}/COPYING
# skipping this license because I don't feel like dealing with it
#%{_docdir}/%{name}/ext/coroutine/LICENSE_1_0.txt
%{_libdir}/libkea-asiodns.so.*
%{_libdir}/libkea-asiolink.so.*
%{_libdir}/libkea-cc.so.*
%{_libdir}/libkea-cfgclient.so.*
%{_libdir}/libkea-cryptolink.so.*
%{_libdir}/libkea-dhcp++.so.*
%{_libdir}/libkea-dhcp_ddns.so.*
%{_libdir}/libkea-dhcpsrv.so.*
%{_libdir}/libkea-dns++.so.*
%{_libdir}/libkea-eval.so.*
%{_libdir}/libkea-exceptions.so.*
%{_libdir}/libkea-hooks.so.*
%{_libdir}/libkea-log.so.*
%{_libdir}/libkea-stats.so.*
%{_libdir}/libkea-threads.so.*
%{_libdir}/libkea-util-io.so.*
%{_libdir}/libkea-util.so.*

%files devel
%{_includedir}/kea
%{_libdir}/libkea-asiodns.so
%{_libdir}/libkea-asiolink.so
%{_libdir}/libkea-cc.so
%{_libdir}/libkea-cfgclient.so
%{_libdir}/libkea-cryptolink.so
%{_libdir}/libkea-dhcp++.so
%{_libdir}/libkea-dhcp_ddns.so
%{_libdir}/libkea-dhcpsrv.so
%{_libdir}/libkea-dns++.so
%{_libdir}/libkea-eval.so
%{_libdir}/libkea-exceptions.so
%{_libdir}/libkea-hooks.so
%{_libdir}/libkea-log.so
%{_libdir}/libkea-stats.so
%{_libdir}/libkea-threads.so
%{_libdir}/libkea-util-io.so
%{_libdir}/libkea-util.so
%{_libdir}/pkgconfig/dns++.pc

%changelog
* Mon Dec 05 2016 James Sumners <james.sumners@gmail.com> - 1.1.0-1
- 1.1.0

