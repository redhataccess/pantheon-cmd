Name:      pantheon-cmd
Summary:   Pantheon CMD
License:   General Public License 3.0
Vendor:    Red Hat, Inc.
Group:     Applications/Accessories
Version:   1.0
Release:   0%{?dist}
BuildRoot: %{_builddir}/%{name}-buildroot
Packager:  Red Hat
BuildArch: noarch
%if 0%{!?fedora}
Requires:  python36
%endif
Requires:  python3-pygit2
Requires:  python3-pyyaml
Requires:  ruby
Source:    %{name}-%{version}.tar.gz

%description
Validates the structure of and generates previews for modular documentation.

%prep
%setup -q

%build
echo \#\!/usr/bin/bash > pcmd
echo python3 %{_libdir}/PantheonCMD/pcmd.py \"\$\@\" >> pcmd

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_libdir}
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1

install -m 0755 -d $RPM_BUILD_ROOT%{_libdir}/PantheonCMD
install -m 0755 generate-pv2-yml.sh $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/generate-pv2-yml.sh
install -m 0755 pcbuild.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcbuild.py
install -m 0755 pcchecks.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcchecks.py
install -m 0755 pcmd.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcmd.py
install -m 0755 pcprvalidator.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcprvalidator.py
install -m 0755 pcutil.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcutil.py
install -m 0755 pcvalidator.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcvalidator.py
install -m 0755 pcyamlcheck.py $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pcyamlcheck.py
install -m 0755 pv2yml-generator.sh $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/pv2yml-generator.sh
install -m 0755 pcmd $RPM_BUILD_ROOT%{_bindir}/pcmd

cp -rf fonts $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/
cp -rf haml $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/
cp -rf resources $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/
cp -rf templates $RPM_BUILD_ROOT%{_libdir}/PantheonCMD/
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
