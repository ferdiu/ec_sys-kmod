# (un)define the next line to either build for the newest or all current kernels

%define kmod_name             ec_sys
%define kmod_version          1.0
%define kmod_release_version  1
%define kmod_path_kernel      drivers/acpi

Name:           %{kmod_name}-kmod-common

Version:        %{kmod_version}
Release:        %{kmod_release_version}%{?dist}
Summary:        Common files for kernel module ec_sys

Group:          System Environment/Kernel

License:        MIT
URL:            https://github.com/ferdiu/ec_sys-kmod
Source0:        %{url}/archive/refs/tags/v%{version}-%{kmod_release_version}.tar.gz#/%{kmod_name}-kmod-v%{version}.tar.gz
BuildArch:	    noarch

%description
The %{kmod_name} kernel module provides support
for the EC_SYS ACPI debugging (and writing).

This package provides common files for the module.

%prep
%setup -q -n %{kmod_name}-kmod-%{version}-%{kmod_release_version}

%install
install -Dm 644 ./%{_lib}/modprobe.d/%{kmod_name}.conf %{buildroot}%{_libdir}/modprobe.d/%{kmod_name}.conf

%files
%attr(644,root,root) %{_libdir}/modprobe.d/%{kmod_name}.conf
%doc README.md
%license LICENSE

%changelog
* Wed Feb 12 2025 Federico Manzella <ferdiu.manzella@gmail.com> - 1.0-1
- Initial release