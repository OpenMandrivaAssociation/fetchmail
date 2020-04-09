Summary: A remote mail retrieval and forwarding utility
Name: fetchmail
Version: 6.4.3
Release: 1
Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.xz
Source1: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.xz.asc
# systemd service file
Source2: fetchmail.service
# example configuration file
Source3: fetchmailrc.example
# Improves SSL related options
#Patch0: fetchmail-6.3.26-ssl-backport.patch
# Minor fixes of inacurracies in options, usage message and man page (accepted upstream)
#Patch1: fetchmail-6.3.26-options-usage-manpage.patch
Patch2: fetchmail-6.3.24-sslv3-in-ssllib-check.patch
# Set SNI, see bz#1611815 (backported from upstream)
Patch3: fetchmail-6.3.26-ssl-set-sni.patch
URL: http://www.fetchmail.info/
# For a breakdown of the licensing, see COPYING
License: GPL+ and Public Domain
BuildRequires: gettext-devel krb5-devel openssl-devel systemd
BuildRequires: pkgconfig(libxcrypt)

%description
Fetchmail is a remote mail retrieval and forwarding utility intended
for use over on-demand TCP/IP links, like SLIP or PPP connections.
Fetchmail supports every remote-mail protocol currently in use on the
Internet (POP2, POP3, RPOP, APOP, KPOP, all IMAPs, ESMTP ETRN, IPv6,
and IPSEC) for retrieval. Then Fetchmail forwards the mail through
SMTP so you can read it through your favorite mail client.

Install fetchmail if you need to retrieve mail over SLIP or PPP
connections.

%prep
%setup -q
#patch0 -p1 -b .ssl-backport
#patch1 -p1 -b .options-usage-manpage
%patch2 -p1 -b .sslv3-in-ssllib-check
%patch3 -p1 -b .ssl-set-sni

%build
%configure --enable-POP3 --enable-IMAP --with-ssl --without-hesiod \
	--enable-ETRN --enable-NTLM --enable-SDPS --enable-RPA \
	--enable-nls --with-kerberos5 --with-gssapi \
	--enable-fallback=no
make

%install
make install DESTDIR=$RPM_BUILD_ROOT

# install example systemd unit
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/fetchmail.service

# install example config file
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
install -p -m 600 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/fetchmailrc.example

# remove fetchmailconf stuff
rm -f $RPM_BUILD_ROOT%{_bindir}/fetchmailconf*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/fetchmailconf.1*

%find_lang %name

%files -f %{name}.lang
%doc COPYING FAQ FEATURES NEWS NOTES README README.SSL TODO
%{_bindir}/fetchmail
%{_mandir}/man1/fetchmail.1*
%{_unitdir}/fetchmail.service
%{python_sitelib}/fetchmailconf.py
%config(noreplace) %attr(0600, mail, mail) %{_sysconfdir}/fetchmailrc.example
