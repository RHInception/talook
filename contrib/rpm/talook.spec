%if 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
%endif


Name:           talook
Version:        1.0.1
Release:        9%{?dist}
Summary:        Single web front end for restfulstatsjson
Group:          System Environment/Daemons

License:        MIT
URL:            https://github.com/RHInception/talook
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

%{?rhl5:Requires: python-simplejson}

%description
Single web front end for https://github.com/RHInception/talook.

%prep
%setup -q

%pre
getent passwd %{name}d >/dev/null 2>&1 || %{_sbindir}/useradd -M --shell %{_sbindir}/nologin -r %{name}d

%post
/sbin/chkconfig --add %{name}d

%preun
if [ $1 = 0 ]; then
    /sbin/service %{name}d stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}d
    %{_sbindir}/userdel -r %{name}d > /dev/null 2>&1
fi

%build
# Setup the default configuration
%{__sed} -i 's|"templatedir": "."|"templatedir": "/var/www/talook/"|' config.json
%{__sed} -i 's|"staticdir": "./static"|"staticdir": "/var/www/talook/static/"|' config.json
%{__sed} -i 's|"cachedir": "./cache"|"cachedir": "/var/cache/talook/"|' config.json
%{__sed} -i 's|"logdir": "./logs"|"logdir": "/var/log/talook/"|' config.json

%clean
rm -rf $RPM_BUILD_ROOT

%install
mkdir -p $RPM_BUILD_ROOT%{_bindir}/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/%{name}/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/%{name}/
mkdir -p $RPM_BUILD_ROOT%{_initrddir}/

cp server.py $RPM_BUILD_ROOT/%{_bindir}/%{name}-server
cp config.json $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/
cp -rf static templates $RPM_BUILD_ROOT/%{_localstatedir}/www/%{name}/
cp contrib/init.d/%{name}d $RPM_BUILD_ROOT/%{_initrddir}/
python server.py --help | sed -e "s|^|# |" > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}d.conf
echo "OPTIONS=\"--listen 0.0.0.0 --port 8080 --config /etc/talook/config.json\"" >> $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}d.conf


%files
%defattr(0644, root, root, -)
%doc LICENSE README.md
%attr(0755, root, root) %{_bindir}/%{name}-server
%attr(0755, root, root) %dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/config.json
%config(noreplace) %{_sysconfdir}/sysconfig/talookd.conf
%attr(0755, %{name}d, %{name}d) %dir %{_localstatedir}/cache/%{name}/
%attr(0755, %{name}d, %{name}d) %dir %{_localstatedir}/log/%{name}/
%attr(0755, %{name}d, %{name}d) %dir %{_localstatedir}/www/%{name}/
%attr(0755, %{name}d, %{name}d) %dir %{_localstatedir}/www/%{name}/static/
%attr(0755, %{name}d, %{name}d) %dir %{_localstatedir}/www/%{name}/templates/
%{_localstatedir}/www/*
%attr(0755, -, -) %{_initrddir}/%{name}d

%changelog
* Wed Jan 15 2014 Tim Bielawa <tbielawa@redhat.com> - 1.0.1-9
- Useful error message suggestions

* Wed Jan 15 2014 Tim Bielawa <tbielawa@redhat.com> - 1.0.1-8
- Better loading graphic behavior, highlight selected host

* Tue Jan 14 2014 Tim Bielawa <tbielawa@redhat.com> - 1.0.1-7
- Missed a 'getcode' reference

* Tue Jan 14 2014 Tim Bielawa <tbielawa@redhat.com> - 1.0.1-6
- Refactor previous get request handling enhancements

* Tue Jan 14 2014 Tim Bielawa <tbielawa@redhat.com> - 1.0.1-5
- More Ajaxy UX Enhancements
- Better handling of connecting to unresponsive hosts
- Better handling of malformatted json responses

* Mon Jan 13 2014 Tim Bielawa <tbielawa@redhat.com> - 1.0.1-4
- New style and clickables

* Wed Jan  8 2014 Tim Bielawa <tbielawa@redhat.com> - 1.0.1-3
- Use relative paths instead for site style

* Wed Dec 13 2013 Steve Milner <stevem@gnulinux.net>- 1.0.1-2
- Fix to handle directory permissions better.

* Wed Dec 12 2013 Steve Milner <stevem@gnulinux.net>- 1.0.1-1
- Update for upstream release.

* Wed Nov 20 2013 Steve Milner <stevem@gnulinux.net>- 1.0.0-4
- Changed default config.json data

* Tue Nov 19 2013 Steve Milner <stevem@gnulinux.net>- 1.0.0-3
- Fixed cache directory permission

* Tue Nov 19 2013 Steve Milner <stevem@gnulinux.net>- 1.0.0-2
- Fixed sbin issues when installing on RHEL6

* Fri Nov 15 2013 Steve Milner <stevem@gnulinux.net>- 1.0.0-1
- Initial spec
