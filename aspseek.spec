# TODO:
#	- split into indexer and client?
#	- running indexer from cron?
%define		apxs		/usr/sbin/apxs
Summary:	Advanced Internet search engine
Summary(pl):	Silnik zaawansowanej wyszukiwarki Internetowej
Name:		aspseek
Version:	1.2.8
Release:	6
License:	GPL
Group:		Networking/Utilities
Source0:	http://www.aspseek.org/pkg/src/1.2.8/%{name}-%{version}.tar.gz
# Source0-md5:	0660b6b0d45d37c7a53c7e1c40cae002
Source1:	%{name}-mod_aspseek.conf
Source2:	%{name}.init
Patch0:		%{name}-types.patch
URL:		http://www.aspseek.org/
BuildRequires:	apache(EAPI)-devel
BuildRequires:	openssl-devel >= 0.9.7c
BuildRequires:	mysql-devel
BuildRequires:	libstdc++-devel
BuildRequires:	zlib-devel
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/userdel
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires(post,postun):	/sbin/ldconfig
Requires:	webserver
Requires:	%{name}-db-%{version}
Obsoletes:	swish++
Obsoletes:	mnogosearch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_bindir		/home/httpd/cgi-bin
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)

%description
ASPSeek is an Internet search engine, written in C++ using the STL
library. It consists of an indexing robot, a search daemon, and a CGI
search frontend. It can index as many as a few million URLs and search
for words and phrases, use wildcards, and do a Boolean search. Search
results can be limited to time period given, site or Web space (set of
sites) and sorted by relevance (some cool techniques are used) or
date.

ASPSeek is optimized for multiple sites (threaded index, async DNS
lookups, grouping results by site, Web spaces), but can be used for
searching one site as well. ASPSeek can work with multiple
languages/encodings at once (including multibyte encodings such as
Chinese) due to Unicode storage mode. Other features include stopwords
and ispell support, a charset and language guesser, HTML templates for
search results, excerpts, and query words highlighting.

%description -l pl
ASPSeek jest silnikiem wyszukiwarki Internetowej, napisany w C++ z
u¿yciem biblioteki STL. Zawiera robota indeksuj±cego, daemon
wyszukuj±cy oraz interfejs w postaci skryptu CGI. ASPSeek mo¿e
indeksowaæ miliony adresów oraz wyszukiwaæ s³owa oraz zwroty, u¿ywaæ
znaków globalnych jak równie¿ stosowaæ operatory logiczne. Rezultaty
wyszukiwania mog± byæ ograniczane do okre¶lonego okresu czasu,
serwera, zbioru serwerów oraz sortowane wg. aktualno¶ci (okre¶lane za
pomoc± pewnych specjalnych technik) lub daty.

ASPSeek jest zoptymalizowany dla wielu serwerów (w±tkowane
indeksowanie, asynchroniczne zapytania DNS, grupowanie rezultatów wg
serwera, grupy serwerów), ale mo¿e byæ równie¿ u¿ywany do obs³ugi
jednego serwera. ASPSeek mo¿e pracowaæ z wieloma jêzykami/kodowaniami
równocze¶nie (w³±czaj±c w to wielobajtowe kodowania u¿ywane np. dla
jêzyka Chiñskiego) dziêki trybowi zapisu w Unikodzie. Inne mo¿liwo¶ci
to blokowanie okre¶lonych s³ów, wsparcie dla ispella, zgadywarka
kodowania oraz jêzyka, wzorce HTML dla rezultatów wyszukiwania,
pod¶wietlanie wyszukiwanych s³ów.

%package db-mysql
Summary:	MySQL backend driver for ASPSeek
Summary(pl):	Obs³uga MySQL dla ASPSeek
Group:		Networking/Utilities
Provides:	%{name}-db-%{version}
Requires:	%{name} = %{version}
Requires(post):	/sbin/ldconfig

%description db-mysql
This driver acts as a database backend for ASPSeek, so ASPSeek will
store its data in MySQL database.

%description db-mysql -l pl
Ten driver dzia³a jako bazodanowy backend dla ASPSeek, tak, ¿e ASPSeek
bêdzie zapisywa³ swoje dane w bazie MySQL.

%package -n apache-mod_aspseek
Summary:	Apache module: ASPSeek search engine
Summary(pl):	Modu³ Apache: Silnik wyszukiwania ASPSeek
Group:		Networking/Daemons
PreReq:		aspseek
Requires(post,preun):	%{apxs}
Requires(post,preun):	grep
Requires(preun):	fileutils
Requires:	apache(EAPI)

%description -n apache-mod_aspseek
ASPSeek Apache module.

%description -n apache-mod_aspseek -l pl
Modu³ Apache ASPSeek.

%prep
%setup -q
%patch -p1

%build
%configure2_13 \
	--enable-charset-guesser \
	--enable-font-size \
	--enable-apache-module \
	--with-openssl \
	--with-mysql \
	--enable-unicode \
	--localstatedir=/var/spool
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{httpd,rc.d/init.d},/home/httpd/icons}
install -d $RPM_BUILD_ROOT/var/{spool/aspseek,log}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/img/* $RPM_BUILD_ROOT/home/httpd/icons
install %{SOURCE1} $RPM_BUILD_ROOT/etc/httpd/mod_aspseek.conf
sed -e "s#/img/#/icons/#g" $RPM_BUILD_ROOT%{_sysconfdir}/s.htm-dist > \
	$RPM_BUILD_ROOT%{_sysconfdir}/s.htm
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
touch $RPM_BUILD_ROOT/var/log/aspseek.log

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`id -u aspseek 2>/dev/null`" ]; then
	if [ "`id -u aspseek`" != "50" ]; then
		echo "Error: user aspseek doesn't have uid=50. Correct this before installing aspseek." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 50 -r -d /home/services/aspseek -s /bin/false -c "ASPSEEK User" -g root aspseek 1>&2
fi

%post
/sbin/ldconfig
/sbin/chkconfig --add %{name}
touch /var/log/aspseek.log
chown aspseek:root /var/log/aspseek.log

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi
	/sbin/chkconfig --del %{name}
fi

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	/usr/sbin/userdel aspseek
fi

%post db-mysql
/sbin/ldconfig
echo "Remember to run %{_sbindir}/aspseek-mysql-postinstall."

%postun db-mysql -p /sbin/ldconfig

%post -n apache-mod_aspseek
%{apxs} -e -a -n aspseek %{_pkglibdir}/mod_aspseek.so 1>&2
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*mod_aspseek.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/mod_aspseek.conf" >> /etc/httpd/httpd.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi

%preun -n apache-mod_aspseek
if [ "$1" = "0" ]; then
	%{apxs} -e -A -n aspseek %{_pkglibdir}/mod_aspseek.so 1>&2
	umask 027
	grep -v "^Include.*mod_aspseek.conf" /etc/httpd/httpd.conf > \
		/etc/httpd/httpd.conf.tmp
	mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc AUTHOR* FAQ* NEWS* README* RELEASE* THANKS* TODO* doc/*.txt
%attr(755,root,root) %{_bindir}/s.cgi
%attr(755,root,root) %{_sbindir}/index
%attr(755,root,root) %{_sbindir}/searchd
%attr(755,root,root) %{_libdir}/libaspseek*.so.*
/home/httpd/icons/*.*
%{_mandir}/man5/aspseek.conf*
%{_mandir}/man5/s*
%{_mandir}/man1/*
%{_mandir}/man7/*
%dir %{_sysconfdir}
%{_sysconfdir}/langmap
%dir %{_sysconfdir}/sql
%{_sysconfdir}/stopwords
%{_sysconfdir}/tables
%attr(754,root,root) /etc/rc.d/init.d/aspseek
%attr(750,aspseek,root) %dir /var/spool/aspseek
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/*.htm
%ghost /var/log/aspseek.log

%files db-mysql
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/aspseek-mysql-postinstall
%attr(755,root,root) %{_libdir}/libmysql*.so*
%{_sysconfdir}/sql/mysql
%{_mandir}/man5/aspseek-sql*

%files -n apache-mod_aspseek
%defattr(644,root,root,755)
%doc README.APACHE_MODULE
%attr(755,root,root) %{_pkglibdir}/*.so
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/httpd/mod_*.conf
