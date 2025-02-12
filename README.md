# ec_sys-kmod

## Overview
`ec_sys-kmod` provides an RPM packaging setup for the `ec_sys` kernel module. The `ec_sys` module enables debugging and writing to the Embedded Controller (EC) through the ACPI interface. This repository contains the necessary spec files to build RPM packages for this kernel module.

## Repository Contents
- **`ec_sys-kmod-common.spec`**: Defines the common files required for the `ec_sys` kernel module, including configuration files and documentation.
- **`ec_sys-kmod.spec`**: Defines the kernel module build process, including dependencies and module-specific configurations.

## Building the RPMs
To build the RPM packages, follow these steps:

1. Clone this repository:
   ```sh
   git clone https://github.com/ferdiu/ec_sys-kmod.git
   cd ec_sys-kmod
   ```

2. Download the source archive:
   ```sh
   spectool -g -R ec_sys-kmod.spec
   ```

3. Install dependencies:
   ```sh
   sudo dnf install -y rpm-build kernel-devel koji kmodtool
   ```

4. Build the RPM packages:
   ```sh
   rpmbuild -bb ec_sys-kmod-common.spec
   rpmbuild -bb ec_sys-kmod.spec
   ```

## Installation
Once the RPMs are built, you can install them using:
```sh
sudo dnf install ./rpmbuild/RPMS/noarch/ec_sys-kmod-common-*.rpm
sudo dnf install ./rpmbuild/RPMS/x86_64/ec_sys-kmod-*.rpm
```

## Usage
After installation, load the `ec_sys` module with:
```sh
sudo modprobe ec_sys write_support=1
```

To verify the module is loaded:
```sh
lsmod | grep ec_sys
```

## License
This project is licensed under the **MIT** and **GPLv2** licenses. See the `LICENSE` file for details: the module it-self is licensed under the **GPLv2** license and the rest of the code is licensed under the **MIT** license.

## Maintainer
- [**Federico Manzella**](https://github.com/ferdiu)

## Changelog
### v1.0 (Feb 12, 2025)
- Initial release

