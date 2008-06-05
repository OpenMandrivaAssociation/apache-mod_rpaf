#Module-Specific definitions
%define mod_name mod_rpaf
%define mod_conf 19_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	0.6
Release:	%mkrel 2
Group:		System/Servers
License:	Apache License
URL:		http://stderr.net/apache/rpaf/
Source0:	http://stderr.net/apache/rpaf/download/%{mod_name}-%{version}.tar.gz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
rpaf is for backend Apache servers what mod_proxy_add_forward is
for frontend Apache servers. It does excactly the opposite of
mod_proxy_add_forward written by Ask Bjrn Hansen. It will also
work with mod_proxy in Apache starting with release 1.3.25 and
mod_proxy that is distributed with Apache from version 2.0.36.

It changes the remote address of the client visible to other
Apache modules when two conditions are satisfied. First condition
is that the remote client is actually a proxy that is defined in
httpd.conf. Secondly if there is an incoming X-Forwarded-For
header and the proxy is in it's list of known proxies it takes
the last IP from the incoming X-Forwarded-For header and changes
the remote address of the client in the request structure. It also
takes the incoming X-Host header and updates the virtualhost
settings accordingly. For Apache mod_proxy it takes the
X-Forwared-Host header and updates the virtualhosts.

%prep

%setup -q -n %{mod_name}-%{version}

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
rm -f mod_rpaf.c 
cp mod_rpaf-2.0.c mod_rpaf.c 

%{_sbindir}/apxs -c mod_rpaf.c 

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
