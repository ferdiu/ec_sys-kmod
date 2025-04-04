# (un)define the next line to either build for the newest or all current kernels
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod
%global debug_package %{nil}

%define kmod_name             ec_sys
%define kmod_path_kernel      drivers/acpi
%define kmod_version          1.0
%define kmod_release_version  6
%define repo                  rpmfusion
# The following line is only needed for those modules
# that by default are not included in the kernel configuration
# and will be later used to be built as external modules.
# This means that instead of being commented out in the kernel
# configuration file, they will be set to 'm' (module)
%define kernel_config_entry   CONFIG_ACPI_EC_DEBUGFS

Name:           %{kmod_name}-kmod
Version:        %{kmod_version}
Release:        %{kmod_release_version}%{?dist}
Summary:        Kernel module ec_sys
Group:          System Environment/Kernel
License:        GPLv2
URL:            https://github.com/ferdiu/ec_sys-kmod
Source0:        %{url}/archive/refs/tags/v%{version}-%{kmod_release_version}.tar.gz#/%{name}-v%{version}-%{kmod_release_version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  kernel-devel
BuildRequires:  koji
BuildRequires:  rustfmt
BuildRequires:  %{_bindir}/kmodtool

%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null | sed 's|extra|updates|g' | sed 's|%{kmod_name}/||g') }

# NOTE: the previous command is piped to two call to sed to substitute the destination
# path of the module to updates directory (instead of extra) because this SPEC is intended
# to be used with in-tree modules

%description
The %{kmod_name} kernel module provides support
for the EC_SYS ACPI debugging (and writing).


%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null | sed 's|extra|updates|g' | sed 's|%{kmod_name}/||g'

%setup -q -c -T -a 0

for kernel_version in %{?kernel_versions} ; do
    kernel_v=${kernel_version%%___*}                            # eg. 6.12.11-200.fc41.x86_64
    kernel_v_no_arch=${kernel_v%.*}                             # eg. 6.12.11-200.fc41
    kernel_extra=${kernel_v#*-}                                 # eg. 200.fc41.x86_64
    kernel_v_no_extra="$(echo -n ${kernel_v} | cut -d"-" -f1)"  # eg. 6.12.11
    kernel_src_dir=${kernel_version##*__}                       # eg. /usr/src/kernels/6.12.11-200.fc41.x86_64

    mkdir -p "${kernel_v_no_arch}"

    # ------------------------------------------------------------------------
    pushd "${kernel_v_no_arch}"

    # Download kernel source
    koji download-build --arch=src "kernel-${kernel_v}"

    ls

    # Unpack source and kernel.spec file
    rpm \
        --define "_sourcedir ${PWD}" \
        --define "_specdir ${PWD}" \
        --define "_builddir ${PWD}" \
        --define "_srcrpmdir ${PWD}" \
        --define "_rpmdir ${PWD}" \
        --define "_buildrootdir ${PWD}/.build" \
        -Uvh kernel-${kernel_v_no_arch}.src.rpm

    ls

    # Unpack source and apply (original) patches
    rpmbuild \
        --define "_sourcedir ${PWD}" \
        --define "_specdir ${PWD}" \
        --define "_builddir ${PWD}" \
        --define "_srcrpmdir ${PWD}" \
        --define "_rpmdir ${PWD}" \
        --define "_buildrootdir ${PWD}/.build" \
        -bp --target="$(uname -m)" kernel.spec

    if [ %{fedora} -gt 40 ]; then
        build_dir="./kernel-${kernel_v_no_extra}-build/kernel-${kernel_v_no_extra}/linux-${kernel_v}"
    else
        build_dir="./kernel-${kernel_v_no_extra}/linux-${kernel_v}"
    fi

    # Prepare build directory
    mv "$build_dir" ../_kmod_build_${kernel_v}

    popd
    # ------------------------------------------------------------------------
    rm -r "${kernel_v_no_arch}"

    # Copy essential files from kernel src directory
    cp -a ${kernel_src_dir}/{.config,Module.symvers,System.map} ./_kmod_build_${kernel_v}/

    # Set correct extra version in Makefile
    sed -i 's/^EXTRAVERSION.*$/EXTRAVERSION=-'"${kernel_extra}"'/' "./_kmod_build_${kernel_v}/Makefile"

    # Patch .config to enable the module
    sed -i -r 's/^.*\b('"%{kernel_config_entry}"')\b.*$\b/\1=m/' "./_kmod_build_${kernel_v}/.config"
done


%build
for kernel_version in %{?kernel_versions}; do
    yes "" | make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" prepare
    yes "" | make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" modules_prepare
    make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" M=%{kmod_path_kernel} modules
done


%install
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" M=%{kmod_path_kernel} INSTALL_MOD_PATH=${RPM_BUILD_ROOT} modules_install

    # Delete all modules *.ko that does not match the kmod_name
    find ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*} -name "*.ko" -type f -exec sh -c 'f="{}"; [ "$(basename "$f")" = "%{kmod_name}.ko" ] || rm -f "$f"' \;

    # Eventually delete all orphan directories
    find ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*} -type d -empty -delete

    # Delete modules.* files
    rm -f ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}/modules.*
done
%{?akmod_install}


%changelog
* Fri Apr 4 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0-6
- Fix source download problem in ec_sys-kmod.spec

* Fri Apr 4 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0-5
- Fix source download problem

* Thu Feb 13 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0-4
- Add rustfmt in ec_sys-kmod build requires

* Thu Feb 13 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0-3
- Fix: wrong path for the modprobe config file

* Thu Feb 13 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0-2
- Add autmoatic agree with default new configs during prepare step

* Wed Feb 12 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0-1
- Initial release
