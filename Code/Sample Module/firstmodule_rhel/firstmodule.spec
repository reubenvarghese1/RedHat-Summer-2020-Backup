%define kmod_headers_version	%(rpm -qa kernel-devel | sed 's/^kernel-devel-//')
%define sbindir %( if [ -d "/sbin" -a \! -h "/sbin" ]; then echo "/sbin"; else echo %{_sbindir}; fi )
%global kernel_source() /usr/src/kernels/%{kmod_headers_version}
%define kmod_kbuild_dir	.
%define kmod_driver_version	1.0
%define kmod_name firstmodule
%define kmod_rpm_release 1%{?dist}
%define findpat %( echo "%""P" )

Name:           firstmodule
Version:        1.0
Release:        1%{?dist}
Summary:        Just an RPM to test how things work

License:        GPLv2+
URL:            https://github.com/reubenvarghese1/KernelDev
Source0:        https://github.com/
reubenvarghese1/testwuu/raw/master/firstmodule.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:  gcc 
Requires(post):	%{sbindir}/weak-modules
Requires(postun):	%{sbindir}/weak-modules
Provides:	kernel-modules = %{kmod_kernel_version}.%{_target_cpu}
Provides: firstmodule = %{?epoch:%{epoch}:}%{version}-%{release}

%description
Testing module installation using rpm

%pre
# During the install, check whether firstmodule or secondmodule is loaded.  A warning here
# indicates that a previous install was not completely removed.  This message
# is purely informational to the user.

for module in firstmodule secondmodule; do
  if grep -q "^${module}" /proc/modules; then
    echo "WARNING: Found ${module} module previously loaded.  A reboot is recommended before attempting to use the newly installed module."   
  fi
done

%post
modules=( $(find /lib/modules/%{kmod_headers_version}/extra/firstmodule | grep '\.ko$') )
printf '%s\n' "${modules[@]}" | %{sbindir}/weak-modules --add-modules


%preun
rpm -ql firstmodule-%{kmod_driver_version}-%{kmod_rpm_release}%{?dist}.$(arch) | grep '\.ko$' > /var/run/rpm-firstmodule-modules
# Check whether kvdo or uds is loaded, and if so attempt to remove it.  A
# failure to unload means there is still something using the module.  To make
# sure the user is aware, we print a warning with recommended instructions.
for module in firstmodule secondmodule; do
  if grep -q "^${module}" /proc/modules; then
    warnMessage="WARNING: ${module} in use.  Changes will take effect after a reboot."
    modprobe -r ${module} 2>/dev/null || echo ${warnMessage} && /usr/bin/true
  fi
done

%postun
modules=( $(cat /var/run/rpm-kmod-%{kmod_name}-modules) )
rm /var/run/rpm-%{kmod_name}-modules
printf '%s\n' "${modules[@]}" | %{_sbindir}/weak-modules --dracut=/usr/bin/dracut --remove-modules


%build
rm -rf obj
cp -r source obj
make -C %{kernel_source} M=$PWD/obj/%{kmod_kbuild_dir} V=1
# mark modules executable so that strip-to-file can strip them
find obj/%{kmod_kbuild_dir} -name "*.ko" -type f -exec chmod u+x '{}' +
for modules in $( find obj/%{kmod_kbuild_dir} -name "*.ko" -type f -printf "%{findpat}\n" | sed 's|\.ko$||' | sort -u ) ; do
	# update depmod.conf
	module_weak_path=$(echo $modules | sed 's/[\/]*[^\/]*$//')
	if [ -z "$module_weak_path" ]; then
		module_weak_path=%{name}
	else
		module_weak_path=%{name}/$module_weak_path
	fi
	echo "override $(echo $modules | sed 's/.*\///') $(echo %{kmod_headers_version} | sed 's/\.[^\.]*$//').* weak-updates/$module_weak_path" >> source/depmod.conf
	done
done

%install
export INSTALL_MOD_PATH=$RPM_BUILD_ROOT
export INSTALL_MOD_DIR=extra/%{name}
make -C %{kernel_source} modules_install V=1
find $INSTALL_MOD_PATH/lib/modules -iname 'modules.*' -exec rm {} \;
install -m 644 -D source/depmod.conf $RPM_BUILD_ROOT/etc/depmod.d/%{kmod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
/lib/modules/%{kmod_headers_version}
/etc/depmod.d/%{kmod_name}.conf


%prep
%setup -n firstmodule
%{nil}
set -- *
mkdir source
mv "$@" source/
mkdir obj

%changelog
* Wed Jul  8 2020 Reuben Varghese
- 
