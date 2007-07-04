# current = mdv2007.0
%define build_current	1
%define build_80	0
%define build_7x	0

Name:		fetchmail
Version:	6.3.8
Release:	%mkrel 2
Group:		Networking/Mail
BuildRequires:	bison flex gettext-devel openssl-devel
Summary: 	Full-featured POP/IMAP mail retrieval daemon
Source:		http://download.berlios.de/fetchmail/%name-%version.tar.bz2
Source2:	http://download.berlios.de/fetchmail/%name-%version.tar.bz2.asc
Source3:	fetchmailconf.desktop.bz2
Source4:	fetchmail.sysconfig.bz2
Source5:	fetchmail.bz2
Source6:	fetchmail.gif
Patch0:		fetchmail-5.7.0-nlsfix.patch
Patch4:		fetchmail-6.3.6-verbose.patch
Patch7:		fetchmail-6.3.4-stripnul.patch
Patch8:		fetchmail-6.3.6-nonewline.patch
Patch9:		fetchmail-6.3.2-norootwarning.patch

License: 	GPL
URL: 		http://www.fetchmail.info

%if %{build_current}
Requires: 	MailTransportAgent
%endif
%if %{build_80}
Requires:	MailTransportAgent smtpdaemon
%endif
%if %{build_7x}
Requires:	smtpdaemon
%endif
BuildRequires: emacs-bin
BuildRequires: gettext
BuildRequires: python
BuildRoot: 	%_tmppath/%name-%version-buildroot


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
%patch0 -p1
%patch4 -p1
%patch7 -p1 -b .stripnul
%patch8 -p1 -b .nonewline
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
bzcat %SOURCE5 > $RPM_BUILD_ROOT%_initrddir/fetchmail

echo -e "# Put here each user config\n" > $RPM_BUILD_ROOT/etc/fetchmailrc

rm -rf contrib/RCS
chmod 644 contrib/*
find -name \*.xpm -exec chmod 644 '{}' \;

# Mandrake menu entry
mkdir -p $RPM_BUILD_ROOT/{%_liconsdir,%_miconsdir,%_menudir}
cat << EOF >$RPM_BUILD_ROOT%_menudir/%{name}conf
?package(%{name}conf): command="%{name}conf" \
icon="other_configuration.png" \
needs="x11" \
title="Fetchmailconf" \
longtitle="Configuration of fetchmail" \
%if %{mdkversion} >= 200610
xdg=true \
%endif
section="System/Configuration/Other"
EOF


mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Fetchmailconf
Comment=%{summary}
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

# emacs, I use it, I want it
# yves 5.9.5-2mdk
mkdir -p $RPM_BUILD_ROOT%_datadir/emacs/site-lisp
install -m 644 contrib/fetchmail-mode.el $RPM_BUILD_ROOT%_datadir/emacs/site-lisp
emacs -batch -f batch-byte-compile $RPM_BUILD_ROOT%_datadir/emacs/site-lisp/fetchmail-mode.el

install -d $RPM_BUILD_ROOT%_sysconfdir/emacs/site-start.d
cat <<EOF >$RPM_BUILD_ROOT%_sysconfdir/emacs/site-start.d/%name.el
(setq auto-mode-alist (append '(("\..fetchmailrc$" . fetchmail-mode)) auto-mode-alist))
(autoload 'fetchmail-mode "fetchmail-mode.el" "Mode for editing .fetchmailrc files" t)
EOF

%clean
rm -rf $RPM_BUILD_ROOT


%post -n fetchmailconf
%update_menus

%postun -n fetchmailconf
%clean_menus

%post -n fetchmail-daemon
%_post_service fetchmail

%preun -n fetchmail-daemon
%_preun_service fetchmail

%files -f %name.lang
%defattr (-, root, root)
%doc COPYING FAQ FEATURES INSTALL NEWS NOTES README
%doc contrib fetchmail-features.html fetchmail-FAQ.html design-notes.html
%_bindir/fetchmail
%_datadir/emacs/site-lisp/fetchmail-mode.el
%config(noreplace) %_sysconfdir/emacs/site-start.d/%name.el
%_mandir/man1/fetchmail.1*
%_datadir/emacs/site-lisp/fetchmail-mode.elc

%files -n fetchmailconf
%defattr(-,root,root)
%doc README.fetchmail-conf
%_menudir/fetchmailconf
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


