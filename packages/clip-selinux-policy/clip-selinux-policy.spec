%define distro redhat 
%define polyinstatiate n
%define monolithic n
%define POLICYVER 24
%define libsepolver 2.0.41-1
%define POLICYCOREUTILSVER 2.0.78-1
%define CHECKPOLICYVER 2.0.21-1
Name:   %{pkgname}
Version: %{version}
Release: %{release}
Summary: Certifiable Linux Integration Platform Policy Base Configuration Data
License: GPLv2+
Group: System Environment/Base
Source: %{pkgname}-%{version}.tar.gz
Url: http://oss.tresys.com/repos/refpolicy/
BuildArch: noarch
Requires: coreutils

%description 
Certifiable Linux Integration Platform SELinux core, non-policy components. 
This package contains the base components common across policy types.  In
addition to this package, you will want to choose from:
clip-selinux-policy-mcs (an MCS policy)
clip-selinux-policy-mls (an MLS policy)

%files 
%defattr(-,root,root,-)
%{_mandir}/man*/*
# policycoreutils owns these manpage directories, we only own the files within them
%{_mandir}/ru/*/*
%dir %{_usr}/share/selinux
%dir %{_usr}/share/selinux/devel
%dir %{_usr}/share/selinux/devel/include
%dir %{_usr}/share/selinux/packages
%dir %{_sysconfdir}/selinux
%ghost %config(noreplace) %{_sysconfdir}/selinux/config
%ghost %{_sysconfdir}/sysconfig/selinux
%{_usr}/share/selinux/devel/include/*
%{_usr}/share/selinux/devel/Makefile
%{_usr}/share/selinux/devel/example.*
%{_usr}/share/selinux/devel/policy.*

%package doc
Summary: Certifiable Linux Integration Platform SELinux policy documentation
Group: System Environment/Base
Requires(pre): clip-selinux-policy = %{version}-%{release}
Requires: /usr/bin/xdg-open
BuildRequires: policycoreutils-python m4 policycoreutils python make gcc checkpolicy >= %{CHECKPOL_VERSION}

%description doc
Certifiable Linux Integration Platform SELinux policy documentation package

%files doc
%defattr(-,root,root,-)
%doc %{_usr}/share/doc/%{name}-%{version}
%attr(755,root,root) %{_usr}/share/selinux/devel/policyhelp

%global genSeparatePolRPM() \
%package %2-%1 \
Summary: Certifiable Linux Integration Platform SELinux %2 policy for %1 \
Group: System Environment/Base \
Requires(pre): clip-selinux-policy-%2 = %{version}-%{release} \
BuildRequires: policycoreutils-python m4 policycoreutils python make gcc checkpolicy >= %{CHECKPOL_VERSION} \
\
%description %2-%1  \
Certifiable Linux Integration Platform SELinux %2 policy for %1 \
\
%files %2-%1 \
%{_usr}/share/selinux/%2/%1.pp.bz2 \
\
%post %2-%1 \
echo %1.pp.bz2 >> %{_usr}/share/selinux/%2/modules.lst \
semodule -n -s %2 -i %{_usr}/share/selinux/%2/%1.pp.bz2 \
echo "NOTE: installing the %1 policy RPM *does not reload the policy*." \
echo "To reload the policy run 'semodule -R'" 

%{expand:%( for f in %{separatePkgs}; do echo "%%genSeparatePolRPM $f mcs"; done)}

%{expand:%( for f in %{separatePkgs}; do echo "%%genSeparatePolRPM $f mls"; done)}

%define installCmds() \
make %{?_smp_mflags} UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}  %{separatePkgs}" base.pp \
make %{?_smp_mflags} validate UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}  %{separatePkgs}" modules \
make %{?_smp_mflags} UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}  %{separatePkgs}" install \
make %{?_smp_mflags} UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules} %{separatePkgs}" install-appconfig \
#%{__cp} *.pp %{buildroot}/%{_usr}/share/selinux/%1/ \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/policy \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/modules/active \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/contexts/files \
touch %{buildroot}/%{_sysconfdir}/selinux/%1/modules/semanage.read.LOCK \
touch %{buildroot}/%{_sysconfdir}/selinux/%1/modules/semanage.trans.LOCK \
rm -rf %{buildroot}%{_sysconfdir}/selinux/%1/booleans \
touch %{buildroot}%{_sysconfdir}/selinux/%1/seusers \
touch %{buildroot}%{_sysconfdir}/selinux/%1/policy/policy.%{POLICYVER} \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.homedirs \
install -m0644 config/setrans.conf %{buildroot}%{_sysconfdir}/selinux/%1/setrans.conf \
find %{buildroot}/%{_usr}/share/selinux/%1/ -type f |xargs -P `/usr/bin/nproc` -n `/usr/bin/nproc`  bzip2 \
awk '$1 !~ "/^#/" && $2 == "=" && $3 == "module" { printf "%%s.pp.bz2 ", $1 }' ./policy/modules.conf > %{buildroot}/%{_usr}/share/selinux/%1/modules.lst \
[ x"%{enable_modules}" != "x" ] && for i in %{enable_modules}; do echo ${i}.pp.bz2 >> %{buildroot}/%{_usr}/share/selinux/%1/modules.lst; done \
SORTED_PKGS=`for p in %{separatePkgs}; do echo $p | awk '{ print length($0) " " $0; }'; done | sort -r -n | cut -d ' ' -f 2` \
for f in ${SORTED_PKGS}; do grep $f\.pp\.bz2 %{buildroot}/%{_usr}/share/selinux/%1/modules.lst || (echo "failed to update module.lst for module $f" && exit -1); sed -i -e "s/$f.pp.bz2//g" %{buildroot}/%{_usr}/share/selinux/%1/modules.lst; done 
%nil

%global excludes() %(for f in %{separatePkgs}; do echo "%exclude %{_usr}/share/selinux/%1/${f}.pp.bz2"; done )
 
%define fileList() \
%defattr(-,root,root) \
%dir %{_usr}/share/selinux/%1 \
%{_usr}/share/selinux/%1/*.pp.bz2 \
%{_usr}/share/selinux/%1/modules.lst \
%dir %{_sysconfdir}/selinux/%1 \
%config(noreplace) %{_sysconfdir}/selinux/%1/setrans.conf \
%ghost %{_sysconfdir}/selinux/%1/seusers \
%dir %{_sysconfdir}/selinux/%1/modules \
%verify(not mtime) %{_sysconfdir}/selinux/%1/modules/semanage.read.LOCK \
%verify(not mtime) %{_sysconfdir}/selinux/%1/modules/semanage.trans.LOCK \
%attr(700,root,root) %dir %{_sysconfdir}/selinux/%1/modules/active \
#%verify(not md5 size mtime) %attr(600,root,root) %config(noreplace) %{_sysconfdir}/selinux/%1/modules/active/seusers \
%dir %{_sysconfdir}/selinux/%1/policy/ \
%ghost %{_sysconfdir}/selinux/%1/policy/policy.* \
%dir %{_sysconfdir}/selinux/%1/contexts \
%config %{_sysconfdir}/selinux/%1/contexts/customizable_types \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/securetty_types \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/dbus_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/x_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/default_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/sepgsql_contexts \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/default_type \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/failsafe_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/initrc_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/removable_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/userhelper_context \
%dir %{_sysconfdir}/selinux/%1/contexts/files \
%ghost %{_sysconfdir}/selinux/%1/contexts/files/file_contexts \
%ghost %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.homedirs \
%config %{_sysconfdir}/selinux/%1/contexts/files/media \
%dir %{_sysconfdir}/selinux/%1/contexts/users \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/root \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/guest_u \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/xguest_u \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/user_u \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/staff_u 

%define saveFileContext() \
if [ -s /etc/selinux/config ]; then \
     . %{_sysconfdir}/selinux/config; \
     FILE_CONTEXT=%{_sysconfdir}/selinux/%1/contexts/files/file_contexts; \
     if [ "${SELINUXTYPE}" = %1 -a -f ${FILE_CONTEXT} ]; then \
        [ -f ${FILE_CONTEXT}.pre ] || cp -f ${FILE_CONTEXT} ${FILE_CONTEXT}.pre; \
     fi \
fi

%define loadpolicy() \
. %{_sysconfdir}/selinux/config; \
( cd /usr/share/selinux/%1; semodule -n -b base.pp.bz2 -i %2 -s %1 2>&1 ); \

%define relabel() \
. %{_sysconfdir}/selinux/config; \
FILE_CONTEXT=%{_sysconfdir}/selinux/%1/contexts/files/file_contexts; \
selinuxenabled; \
if [ $? = 0  -a "${SELINUXTYPE}" = %1 -a -f ${FILE_CONTEXT}.pre ]; then \
     fixfiles -C ${FILE_CONTEXT}.pre restore; \
     restorecon -R /root /var/log /var/run 2> /dev/null; \
     rm -f ${FILE_CONTEXT}.pre; \
fi; 

%description
Certifiable Linux Integration Platform SELinux Reference Policy - modular.

%build

%prep 
%setup -n %{pkgname} -q

%install
%{__rm} -fR %{buildroot}
mkdir -p %{buildroot}%{_mandir}
cp -R  man/* %{buildroot}%{_mandir}
mkdir -p %{buildroot}%{_sysconfdir}/selinux
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
touch %{buildroot}%{_sysconfdir}/selinux/config
touch %{buildroot}%{_sysconfdir}/sysconfig/selinux

# Always create policy module package directories
mkdir -p %{buildroot}%{_usr}/share/selinux/{mcs,mls,modules}/

# Install devel
make %{?_smp_mflags} clean
# installCmds NAME TYPE DIRECT_INITRC POLY UNKNOWN
%installCmds mcs mcs n y deny
%installCmds mls mls n y deny

make %{?_smp_mflags} UNK_PERMS=deny NAME=mcs TYPE=mcs DISTRO=%{distro} UBAC=y DIRECT_INITRC=n MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} PKGNAME=%{name}-%{version} POLY=y MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}" install-headers install-docs
mkdir %{buildroot}%{_usr}/share/selinux/devel/
mkdir %{buildroot}%{_usr}/share/selinux/packages/
mv %{buildroot}%{_usr}/share/selinux/mcs/include %{buildroot}%{_usr}/share/selinux/devel/include
install -m 644 config/Makefile.devel %{buildroot}%{_usr}/share/selinux/devel/Makefile
install -m 644 doc/example.* %{buildroot}%{_usr}/share/selinux/devel/
install -m 644 doc/policy.* %{buildroot}%{_usr}/share/selinux/devel/
echo  "xdg-open file:///usr/share/doc/clip-selinux-policy-%{version}/html/index.html"> %{buildroot}%{_usr}/share/selinux/devel/policyhelp
chmod +x %{buildroot}%{_usr}/share/selinux/devel/policyhelp
%clean
%{__rm} -fR %{buildroot}

%post
if [ ! -s /etc/selinux/config ]; then
#
#     New install so we will default to clip policy
#
echo "
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=%{enforcing_mode}
# SELINUXTYPE= can take one of these two values:
#     mcs - CLIP's standard Multi Category security policy,
#     mls - CLIP's Multi Level Security security policy.
SELINUXTYPE=mcs

" > /etc/selinux/config

     ln -sf /etc/selinux/config /etc/sysconfig/selinux 
     restorecon /etc/selinux/config 2> /dev/null || :
else
     . /etc/selinux/config
     # if first time update booleans.local needs to be copied to sandbox
     [ -f /etc/selinux/${SELINUXTYPE}/booleans.local ] && mv /etc/selinux/${SELINUXTYPE}/booleans.local /etc/selinux/clip/modules/active/
     [ -f /etc/selinux/${SELINUXTYPE}/seusers ] && cp -f /etc/selinux/${SELINUXTYPE}/seusers /etc/selinux/${SELINUXTYPE}/modules/active/seusers
fi
exit 0

%postun
if [ $1 = 0 ]; then
     setenforce 0 2> /dev/null
     if [ ! -s /etc/selinux/config ]; then
          echo "SELINUX=disabled" > /etc/selinux/config
     else
          sed -i 's/^SELINUX=.*/SELINUX=disabled/g' /etc/selinux/config
     fi
fi
exit 0

%package mcs
Summary: Certifiable Linux Integration Platform SELinux clip base policy
Provides: selinux-policy-base = %{version}-%{release}
Group: System Environment/Base
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(pre): coreutils
Requires(pre): clip-selinux-policy = %{version}-%{release}
Requires: clip-selinux-policy = %{version}-%{release}
Conflicts:  audispd-plugins <= 1.7.7-1
Conflicts:  seedit

%description mcs 
Certifiable Linux Integration Platform policy.
Based off of reference policy refpolicy-2.20110726.tar.bz2

%pre mcs
%saveFileContext mcs

%post mcs
packages=`cat /usr/share/selinux/mcs/modules.lst`
if [ $1 -eq 1 ]; then
   %loadpolicy mcs $packages
   restorecon -R /root /var/log /var/run 2> /dev/null
else
#   semodule -n -s mcs 2>/dev/null
   %loadpolicy mcs $packages
   %relabel mcs
fi
touch /.autorelabel
exit 0

%files mcs 
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/selinux/mcs/contexts/users/unconfined_u
%fileList mcs

%excludes mcs

%package mls 
Summary: Certifiable Linux Integration Platform SELinux mls base policy
Group: System Environment/Base
Provides: selinux-policy-base = %{version}-%{release}
Requires: policycoreutils-newrole >= %{POLICYCOREUTILSVER} setransd
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(pre): coreutils
Requires(pre): clip-selinux-policy = %{version}-%{release}
Requires: clip-selinux-policy = %{version}-%{release}
Conflicts:  seedit

%description mls 
Certifiable Linux Integration Platform policy mls base module.
Based off of reference policy refpolicy-2.20110726.tar.bz2

%pre mls 
%saveFileContext mls

%post mls 
#semodule -n -s mls 2>/dev/null
packages=`cat /usr/share/selinux/mls/modules.lst`
%loadpolicy mls $packages

if [ $1 -eq 1 ]; then
   restorecon -R /root /var/log /var/run 2> /dev/null
else
%relabel mls
fi
exit 0

%files mls
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/selinux/mls/contexts/users/unconfined_u
%fileList mls

%excludes  mls


%changelog
