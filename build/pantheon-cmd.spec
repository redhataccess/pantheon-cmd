Name:      pantheon-cmd
Summary:   Pantheon CMD
License:   General Public License 3.0
Vendor:    Red Hat, Inc.
Group:     Applications/Accessories
Version:   1.0
Release:   3%{?dist}
BuildRoot: %{_builddir}/%{name}-buildroot
Packager:  Andrew Dahms
BuildArch: noarch
%if 0%{!?fedora}
Requires:  python36
%endif
Requires:  python3-pyyaml
Requires:  ruby
Source:    %{name}-%{version}.tar.gz

%description
Builds Pantheon V2 content.

%prep
%setup -q

%if 0%{?fedora}
sed -i 's|#!/usr/libexec/platform-python|#!/usr/bin/python3|' *.py
%endif

%build
echo \#\!/usr/bin/bash > pcmd
echo python3 %{_libdir}/PantheonCMD/pcmd.py \"\$\@\" >> pcmd

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_libdir}
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1

install -m 0755 -d $RPM_BUILD_ROOT%{_libdir}/PantheonCMD
install -m 0755 pcmd.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcmd.py
install -m 0755 pcbuild.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcbuild.py
install -m 0755 pcutil.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcutil.py
install -m 0755 pcmd $RPM_BUILD_ROOT%{_bindir}/pcmd

cp -rf haml $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/
cp -rf resources $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/
cp -rf utils $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/
cp -rf locales $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/
cp pcmd.1.gz $RPM_BUILD_ROOT%{_mandir}/man1/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%dir %{_libdir}/PantheonCMD
%{_libdir}/PantheonCMD/*
%{_bindir}/pcmd
%{_mandir}/man1/*
