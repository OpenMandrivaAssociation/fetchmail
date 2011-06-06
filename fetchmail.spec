Summary: 	Full-featured POP/IMAP mail retrieval daemon
Name:		fetchmail
Version:	6.3.20
Release:	%mkrel 1
License: 	GPL
Group:		Networking/Mail
URL: 		http://www.fetchmail.info
Source:		http://download.berlios.de/fetchmail/%name-%version.tar.bz2
Source2:	http://download.berlios.de/fetchmail/%name-%version.tar.bz2.asc
Source3:	fetchmailconf.desktop.bz2
Source4:	fetchmail.sysconfig.bz2
Source5:	fetchmail.init
Source6:	fetchmail.gif
Patch0:		fetchmail-5.7.0-nlsfix.patch
Patch9:		fetchmail-6.3.2-norootwarning.patch
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gettext
BuildRequires:	gettext-devel
BuildRequires:	openssl-devel
BuildRequires:	python
Requires: 	MailTransportAgent
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Fetchmail is a free, full-featured, robust, and well-documented remote mail
retrieval and forwarding utility intended to be used over on-demand TCP/IP
links (such as SLIP or PPP connections).

It retrieves mail from remote mail servers and forwards it to your local
(client) machine's delivery system, so it can then be read by normal
mail user agents such as Mutt, Elm, Pine, (X)Emacs/Gnus or Mailx.

It comes with an interactive GUI configurator suitable for end-users.

Fetchmail supports every remote-mail protocol currently in use on the
Internet (POP2, POP3, RPOP, APOP, KPOP, all IMAPs, ESMTP ETRN) for
retrieval.  Then Fetchmail forwards the mail through SMTP, so you can
read it through your normal mail client.

%package -n fetchmailconf
Summary: 	A utility for graphically configuring your fetchmail preferences
Group: 		System/Configuration/Networking
Requires: 	tkinter
Requires: 	%name = %version


%description -n fetchmailconf
Fetchmailconf is a TCL/TK application for graphically configuring
your ~/.fetchmailrc preferences file.

Fetchmail has many options which can be daunting to the new user.

This utility takes some of the guesswork and hassle out of setting up
fetchmail.

%package daemon
Summary:	SySV init script for demonize fetchmail for retrieving emails
Group:		System/Base
Requires:	%name = %version
Requires(preun): rpm-helper
Requires(post): rpm-helper

%description daemon
SySV init script for demonize fetchmail for sucking emails.

%prep
%setup -q
%patch0 -p0
%patch9 -p0 -b .norootwarn

%build
%serverbuild
export CFLAGS="$CFLAGS -g"
%configure2_5x  \
	--with-ssl=%_prefix	\
	--enable-RPA		\
	--enable-NTLM		\
	--enable-SDPS

# (tv) do not use %%make in order to workaround buggy parallel build:
make all

%install
rm -fr $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT{%_libdir/rhs/control-panel,%_datadir/applets/Administration} \
	$RPM_BUILD_ROOT{%_sysconfdir/{X11/wmconfig,sysconfig},%_mandir/man1,%_initrddir}

%makeinstall

install rh-config/*.{xpm,init} $RPM_BUILD_ROOT%_libdir/rhs/control-panel

%if %{mdkversion} < 200610
bzcat %SOURCE3 > $RPM_BUILD_ROOT%_datadir/applets/Administration/fetchmailconf.desktop
%endif
bzcat %SOURCE4 > $RPM_BUILD_ROOT%_sysconfdir/sysconfig/fetchmail
install -m0755 %SOURCE5 $RPM_BUILD_ROOT%_initrddir/fetchmail

echo -e "# Put here each user config\n" > $RPM_BUILD_ROOT/etc/fetchmailrc

rm -rf contrib/RCS
chmod 644 contrib/*
find -name \*.xpm -exec chmod 644 '{}' \;

# Mandriva menu entry
mkdir -p $RPM_BUILD_ROOT/{%_liconsdir,%_miconsdir,%_menudir}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Fetchmailconf
Comment=Full-featured POP/IMAP mail retrieval daemon
Exec=%{_bindir}/%{name}
Icon=%{name}
Terminal=false
Type=Application
Categories=X-MandrivaLinux-System-Configuration-Other;Settings;
EOF

%find_lang %name

cat > README.fetchmail-conf <<EOF
Fetchmailconf is a TCL/TK application for graphically configuring your
~/.fetchmailrc preferences file.

Fetchmail has many options which can be daunting to the new user.


This utility takes some of the guesswork and hassle out of setting up
fetchmail.
EOF

echo 'SySV init script for demonize fetchmail for sucking emails.'>README.fetchmail-daemon

%clean
rm -rf $RPM_BUILD_ROOT


%if %mdkversion < 200900
%post -n fetchmailconf
%update_menus
%endif

%if %mdkversion < 200900
%postun -n fetchmailconf
%clean_menus
%endif

%post -n fetchmail-daemon
%_post_service fetchmail

%preun -n fetchmail-daemon
%_preun_service fetchmail

%postun -n fetchmail-daemon
if [ "$1" -ge "1" ]; then
    /sbin/service fetchmail condrestart > /dev/null 2>/dev/null || :
fi

%files -f %name.lang
%defattr (-, root, root)
%doc COPYING FAQ FEATURES INSTALL NEWS NOTES README
%doc contrib fetchmail-features.html fetchmail-FAQ.html design-notes.html
%_bindir/fetchmail
%_mandir/man1/fetchmail.1*

%files -n fetchmailconf
%defattr(-,root,root)
%doc README.fetchmail-conf
%_libdir/rhs/control-panel/*
%_bindir/fetchmailconf
%_mandir/man1/fetchmailconf.1*
%if %{mdkversion} < 200610
%_datadir/applets/Administration/fetchmailconf.desktop
%_libdir/python*/site-packages/*
%else
%{_datadir}/applications/
%py_purelibdir/site-packages/*
%endif

%files daemon
%defattr(-,root,root)
%doc README.fetchmail-daemon
%attr(600,root,root) %config(noreplace,missingok) %_sysconfdir/fetchmailrc
%config(noreplace) %{_sysconfdir}/sysconfig/fetchmail
%attr(755,root,root) %config(noreplace) %_initrddir/fetchmail
