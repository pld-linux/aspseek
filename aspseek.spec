Summary:	Advanced Internet search engine
Summary(pl):	Silnik zaawansowanej wyszukiwarki Internetowej
Name:		aspseek
Version:	1.2.8
Release:	1
License:	GPL
Group:		Networking/Utilities
Source0:	http://www.aspseek.org/pkg/src/1.2.8/%{name}-%{version}.tar.gz
URL:		http://www.aspseek.org/
Requires:	webserver
Requires:	%{name}-db-%{version}
BuildRequires:	apache-devel
BuildRequires:	openssl-devel
BuildRequires:	mysql-devel
BuildRequires:	libstdc++-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_bindir		/home/httpd/cgi-bin

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
u�yciem biblioteki STL. Zawiera robota indeksuj�cego, daemon
wyszukuj�cy oraz interfejs w postaci skryptu CGI. ASPSeek mo�e
indeksowa� miliony adres�w oraz wyszukiwa� s�owa oraz zwroty, u�ywa�
znak�w globalnych jak r�wnie� stosowa� operatory logiczne. Rezultaty
wyszukiwania mog� by� ograniczane do okre�lonego okresu czasu,
serwera, zbioru serwer�w oraz sortowane wg. aktualno�ci (okre�lane za
pomoc� pewnych specjalnych technik) lub daty.

ASPSeek jest zoptymalizowany dla wielu serwer�w (w�tkowane
indeksowanie, asynchroniczne zapytania DNS, grupowanie rezultat�w wg
serwera, grupy serwer�w), ale mo�e by� r�wnie� u�ywany do obs�ugi
jednego serwera. ASPSeek mo�e pracowa� z wieloma j�zykami/kodowaniami
r�wnocze�nie (w��czaj�c w to wielobajtowe kodowania u�ywane np. dla
j�zyka Chi�skiego) dzi�ki trybowi zapisu w Unikodzie. Inne mo�liwo�ci
to blokowanie okre�lonych s��w, wsparcie dla ispella, zgadywarka
kodowania oraz j�zyka, wzorce HTML dla rezultat�w wyszukiwania,
pod�wietlanie wyszukiwanych s��w.

%package db-mysql
Summary:	MySQL backend driver for ASPSeek
Summary(pl):	Obs�uga MySQL dla ASPSeek
Group:		Networking/Utilities
Provides:	%{name}-db-%{version}	
Requires:	%{name} = %{version}

%description db-mysql
This driver acts as a database backend for ASPSeek, so ASPSeek will
store its data in MySQL database.

%description db-mysql -l pl
Ten driver dzia�a jako bazodanowy backend dla ASPSeek, tak, �e ASPSeek
b�dzie zapisywa� swoje dane w bazie MySQL.

%packane -n apache-mod_aspseek
Summary:	Apache module: ASPSeek search engine
Summary(pl):	Modu� Apache: Silnik wyszukiwania ASPSeek
Group:		Networking/Daemons
Prereq:		/usr/sbin/apxs
Requires:	apache

%description -n apache-mod_aspseek
ASPSeek Apache module.

%description apache-mod_aspseek -l pl
Modu� Apache ASPSeek.

%prep
%setup -q

%build
%configure2_13 \
	--enable-charset-guesser \
	--enable-font-size \
	--enable-apache-module \
	--with-openssl \
	--with-mysql
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

gzip -9nf AUTHOR* FAQ* NEWS* README.gz RELEASE* THANKS* TODO* doc/*.txt

%clean
rm -rf $RPM_BUILD_ROOT

%pre
exit1
adding users missing

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

#%post db-mysql
#%{sbindir}/aspseek-mysql-postinstall

%post -n apache-mod_aspseek
if [ -f /var/lock/subsys/httpd ]; then
        /etc/rc.d/init.d/httpd restart 1>&2
else
        echo "Run \"/etc/rc.d/init.d/httpd start\" to start apache http daemon."
fi

%preun -n apache-mod_aspseek
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/httpd ]; then
                /etc/rc.d/init.d/httpd restart 1>&2
        fi
fi

%files
%defattr(644,root,root,755)
%doc AUTHOR* FAQ* NEWS* README.gz RELEASE* THANKS* TODO* doc/*.gz
%attr(755,root,root) %{_bindir}/s.cgi
%attr(755,root,root) %{sbindir}/index 
%attr(755,root,root) %{sbindir}/searchd
%attr(755,root,root) %{_libdir}/libaspseek*.so
%{_mandir}/man5/aspseek.conf*
%{_mandir}/man5/s*
%{_mandir}/man1/*
%{_mandir}/man7/*
# CONFIGS

%files db-mysql
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/aspseek-mysql-postinstall
%attr(755,root,root) %{_libdir}/libmysql*.so
%{sysconfdir}/sql/mysql
%{_mandir}/man5/aspseek-sql*

%files -n apache-mod_aspseek
%defattr(644,root,root,755)
%doc README.APACHE_MODULE.gz
%attr(755,root,root) %{_libdir}/apache/*.so
