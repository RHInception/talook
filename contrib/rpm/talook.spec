Name:           talook
Version:        1.0.0
Release:        1%{?dist}
Summary:        Single web front end for restfulstatsjson

License:        MIT
URL:            https://github.com/ashcrow/talook
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

%{?rhl5:Requires: python-simplejson}

%description
Single web front end for https://github.com/tbielawa/restfulstatsjson.

%prep
%setup -q

%pre
%{_sbindir}/useradd --no-create-home --shell %{_sbindir}/nologin --system %{name}d

%post
%{_sbindir}/chkconfig --add %{name}d

%preun
if [ $1 = 0 ]; then
    %{_sbindir}/service %{name}d stop >/dev/null 2>&1
    %{_sbindir}/chkconfig --del %{name}d
    %{_sbindir}/userdel -r %{name}d > /dev/null 2>&1
fi

%build
# Setup the default configuration
%{__sed} -i 's|"templatedir": "."|"templatedir": "/var/www/talook/"|' config.json
%{__sed} -i 's|"staticdir": "./static"|"staticdir": "/var/www/talook/static/"|' config.json
%{__sed} -i 's|"cachedir": "./cache"|"cachedir": "/var/cache/talook/"|' config.json
%{__sed} -i 's|"logdir": "./logs"|"logdir": "/var/log/talook/"|' config.json

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_bindir}/
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/cache/%{name}/
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/log/%{name}/
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/www/%{name}/
mkdir -p $RPM_BUILD_ROOT/%{_initddir}/

cp server.py $RPM_BUILD_ROOT/%{_bindir}/%{name}-server
cp config.json $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/
cp -rf static templates $RPM_BUILD_ROOT/%{_localstatedir}/www/%{name}/ 
cp contrib/init.d/%{name}d $RPM_BUILD_ROOT/%{_initddir}/

%files
%defattr(0644, root, root, -)
%doc LICENSE README.md
%attr(0755, root, root) %{_bindir}/%{name}-server
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/config.json
%dir %{_localstatedir}/cache/%{name}/
%attr(-, %{name}d, %{name}d) %dir %{_localstatedir}/log/%{name}/
%dir %{_localstatedir}/www/%{name}/
%{_localstatedir}/www/*
%attr(0755, -, -) %{_initddir}/%{name}d

%changelog
* Fri Nov 15 2013 Steve Milner <stevem@gnulinux.net>- 1.0.0-1
- Initial spec
