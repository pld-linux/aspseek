# TODO:
#	- split into indexer and client?
#	- running indexer from cron?
%define		apxs		/usr/sbin/apxs
Summary:	Advanced Internet search engine
Summary(pl.UTF-8):	Silnik zaawansowanej wyszukiwarki Internetowej
Name:		aspseek
Version:	1.2.8
Release:	7
License:	GPL
Group:		Networking/Utilities
Source0:	http://www.aspseek.org/pkg/src/1.2.8/%{name}-%{version}.tar.gz
# Source0-md5:	0660b6b0d45d37c7a53c7e1c40cae002
Source1:	%{name}-mod_aspseek.conf
Source2:	%{name}.init
Patch0:		%{name}-types.patch
URL:		http://www.aspseek.org/
BuildRequires:	apache(EAPI)-devel
BuildRequires:	libstdc++-devel
BuildRequires:	mysql-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	zlib-devel
Requires(post):	fileutils
Requires(post,postun):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires:	%{name}-db-%{version}
Requires:	webserver
Provides:	user(aspseek)
Obsoletes:	mnogosearch
Obsoletes:	swish++
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_bindir		/home/httpd/cgi-bin
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)

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

%description -l pl.UTF-8
ASPSeek jest silnikiem wyszukiwarki Internetowej, napisany w C++ z
użyciem biblioteki STL. Zawiera robota indeksującego, daemon
wyszukujący oraz interfejs w postaci skryptu CGI. ASPSeek może
indeksować miliony adresów oraz wyszukiwać słowa oraz zwroty, używać
znaków globalnych jak również stosować operatory logiczne. Rezultaty
wyszukiwania mogą być ograniczane do określonego okresu czasu,
serwera, zbioru serwerów oraz sortowane wg. aktualności (określane za
pomocą pewnych specjalnych technik) lub daty.

ASPSeek jest zoptymalizowany dla wielu serwerów (wątkowane
indeksowanie, asynchroniczne zapytania DNS, grupowanie rezultatów wg
serwera, grupy serwerów), ale może być również używany do obsługi
jednego serwera. ASPSeek może pracować z wieloma językami/kodowaniami
równocześnie (włączając w to wielobajtowe kodowania używane np. dla
języka Chińskiego) dzięki trybowi zapisu w Unikodzie. Inne możliwości
to blokowanie określonych słów, wsparcie dla ispella, zgadywarka
kodowania oraz języka, wzorce HTML dla rezultatów wyszukiwania,
podświetlanie wyszukiwanych słów.

%package db-mysql
Summary:	MySQL backend driver for ASPSeek
Summary(pl.UTF-8):	Obsługa MySQL dla ASPSeek
Group:		Networking/Utilities
Requires(post):	/sbin/ldconfig
Requires:	%{name} = %{version}-%{release}
Provides:	%{name}-db-%{version}

%description db-mysql
This driver acts as a database backend for ASPSeek, so ASPSeek will
store its data in MySQL database.

%description db-mysql -l pl.UTF-8
Ten driver działa jako bazodanowy backend dla ASPSeek, tak, że ASPSeek
będzie zapisywał swoje dane w bazie MySQL.

%package -n apache-mod_aspseek
Summary:	Apache module: ASPSeek search engine
Summary(pl.UTF-8):	Moduł Apache: Silnik wyszukiwania ASPSeek
Group:		Networking/Daemons
Requires(post,preun):	%{apxs}
Requires(post,preun):	grep
Requires(preun):	fileutils
Requires:	apache(EAPI)
Requires:	aspseek

%description -n apache-mod_aspseek
ASPSeek Apache module.

%description -n apache-mod_aspseek -l pl.UTF-8
Moduł Apache ASPSeek.

%prep
%setup -q
%patch0 -p1

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
%useradd -u 50 -d /srv/aspseek -s /bin/false -c "ASPSEEK User" -g root aspseek

%post
/sbin/ldconfig
/sbin/chkconfig --add %{name}
touch /var/log/aspseek.log
chown aspseek:root /var/log/aspseek.log
# create $HOME if possible, we are not allowed to remove it later
if [ ! -d /srv/aspseek ]; then
	if mkdir /srv/aspseek; then
		chown aspseek:root /srv/aspseek
		chmod 755 /srv/aspseek
	fi
fi

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	%userremove aspseek
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
%service -q httpd restart

%preun -n apache-mod_aspseek
if [ "$1" = "0" ]; then
	%{apxs} -e -A -n aspseek %{_pkglibdir}/mod_aspseek.so 1>&2
	umask 027
	grep -v "^Include.*mod_aspseek.conf" /etc/httpd/httpd.conf > \
		/etc/httpd/httpd.conf.tmp
	mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	%service -q httpd restart
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
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.htm
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
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/httpd/mod_*.conf
