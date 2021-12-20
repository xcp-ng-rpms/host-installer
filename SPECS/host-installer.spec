Summary: XenServer Installer
Name: host-installer
Version: 10.7.5.3
Release: 1
License: GPL
Group: Applications/System

Source0: https://code.citrite.net/rest/archive/latest/projects/XS/repos/host-installer/archive?at=10.7.5.3&format=tar.gz&prefix=host-installer-10.7.5.3#/host-installer-10.7.5.3.tar.gz


Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XS/repos/host-installer/archive?at=10.7.5.3&format=tar.gz&prefix=host-installer-10.7.5.3#/host-installer-10.7.5.3.tar.gz) = 0fc00443f45a9e9298f591000942b7898c36c201

# This is where we get 'multipath.conf' from
BuildRequires: sm xenserver-multipath xenserver-lvm2

Requires: xenserver-multipath xenserver-lvm2 iscsi-initiator-utils

# partitioning tools
Requires: gdisk kpartx e2fsprogs dosfstools

# CUI interface
Requires: newt-python newt
Requires: ethtool sdparm pciutils eject net-tools xenserver-biosdevname
Requires: xcp-python-libs python-simplejson

# archives used
Requires: bzip2 tar gzip rpm

# For killall
Requires: psmisc

Requires(post): initscripts

# Strictly no byte compiling python. Python in the install
# environment is different to the dom0 chroot
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%define installer_dir /opt/xensource/installer

# TODO: 'xenserver' branding should be removed!
%define efi_dir /EFI/xenserver

%description
XenServer Installer

%package startup
Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XS/repos/host-installer/archive?at=10.7.5.3&format=tar.gz&prefix=host-installer-10.7.5.3#/host-installer-10.7.5.3.tar.gz) = 0fc00443f45a9e9298f591000942b7898c36c201
Summary: XenServer Installer
Group: Applications/System
Requires: host-installer
Requires: openssh-server
Requires(post): initscripts
%description startup
XenServer installer startup files

%package bootloader
Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XS/repos/host-installer/archive?at=10.7.5.3&format=tar.gz&prefix=host-installer-10.7.5.3#/host-installer-10.7.5.3.tar.gz) = 0fc00443f45a9e9298f591000942b7898c36c201
Summary: XenServer Installer
Group: Applications/System
Requires: host-installer

%description bootloader
XenServer installer bootloader files

%prep
%autosetup -p1

%build

%install
rm -rf %{buildroot}

# Installer files
mkdir -p %{buildroot}/usr/bin
cp support.sh %{buildroot}/usr/bin

mkdir -p %{buildroot}%{installer_dir}
cp -R \
        tui \
        init \
        keymaps \
        timezones \
        answerfile.py \
        backend.py \
        common_criteria_firewall_rules \
        constants.py \
        cpiofile.py \
        disktools.py \
        diskutil.py \
        driver.py \
        fcoeutil.py \
        generalui.py \
        hardware.py \
        init_constants.py \
        install.py \
        netinterface.py \
        netutil.py \
        product.py \
        report.py \
        repository.py \
        restore.py \
        scripts.py \
        snackutil.py \
        uicontroller.py \
        upgrade.py \
        util.py \
        xelogging.py \
    %{buildroot}%{installer_dir}/

# Startup files
mkdir -p \
    %{buildroot}/etc/init.d \
    %{buildroot}/etc/modprobe.d \
    %{buildroot}/etc/modules-load.d \
    %{buildroot}/etc/depmod.d \
    %{buildroot}/etc/dracut.conf.d \
    %{buildroot}/etc/systemd/system/systemd-udevd.d

cp startup/{interface-rename-sideway,early-blacklist} %{buildroot}/etc/init.d/
cp startup/functions %{buildroot}/etc/init.d/installer-functions

cp startup/{early-blacklist.conf,bnx2x.conf} %{buildroot}/etc/modprobe.d/
cp startup/blacklist %{buildroot}/etc/modprobe.d/installer-blacklist.conf
cp startup/modprobe.mlx4 %{buildroot}/etc/modprobe.d/mlx4.conf

cp startup/iscsi-modules %{buildroot}%{_sysconfdir}/modules-load.d/iscsi.conf

cp startup/depmod.conf %{buildroot}/etc/depmod.d/

cp startup/{preinit,S05ramdisk,S06mount} %{buildroot}/%{installer_dir}/

cp startup/systemd-udevd_depmod.conf %{buildroot}/etc/systemd/system/systemd-udevd.d/installer.conf

# Generate a multipath configuration from sm's copy, removing
# the blacklist and blacklist_exception sections.
sed 's/\(^[[:space:]]*find_multipaths[[:space:]]*\)yes/\1no/' \
    < /etc/multipath.xenserver/multipath.conf \
    > %{buildroot}/etc/multipath.conf.disabled


# bootloader files
install -D -m644 bootloader/grub.cfg %{buildroot}%{efi_dir}/grub.cfg
install -D -m644 bootloader/grub.cfg %{buildroot}%{efi_dir}/grub-usb.cfg

sed -i '/^set timeout=[0-9]\+$/asearch --file --set /install.img' \
    %{buildroot}%{efi_dir}/grub-usb.cfg

install -D -m644 bootloader/isolinux.cfg %{buildroot}/boot/isolinux/isolinux.cfg

cat >%{buildroot}/etc/dracut.conf.d/installer.conf <<EOF
echo Skipping initrd creation in the installer
exit 0
EOF

%clean
rm -rf %{buildroot}

%files
%defattr(775,root,root,-)

# Executables
%{installer_dir}/init
%{installer_dir}/report.py
/usr/bin/support.sh

%defattr(664,root,root,775)
# Installer gubbins
%{installer_dir}/answerfile.py
%{installer_dir}/backend.py
%{installer_dir}/constants.py
%{installer_dir}/cpiofile.py
%{installer_dir}/disktools.py
%{installer_dir}/diskutil.py
%{installer_dir}/driver.py
%{installer_dir}/generalui.py
%{installer_dir}/hardware.py
%{installer_dir}/init_constants.py
%{installer_dir}/install.py
%{installer_dir}/netinterface.py
%{installer_dir}/netutil.py
%{installer_dir}/product.py
%{installer_dir}/repository.py
%{installer_dir}/restore.py
%{installer_dir}/scripts.py
%{installer_dir}/snackutil.py
%{installer_dir}/uicontroller.py
%{installer_dir}/upgrade.py
%{installer_dir}/util.py
%{installer_dir}/xelogging.py
%{installer_dir}/fcoeutil.py

# Installer UI
%{installer_dir}/tui/__init__.py
%{installer_dir}/tui/init.py
%{installer_dir}/tui/installer/__init__.py
%{installer_dir}/tui/installer/screens.py
%{installer_dir}/tui/network.py
%{installer_dir}/tui/progress.py
%{installer_dir}/tui/repo.py
%{installer_dir}/tui/fcoe.py

# Data
%{installer_dir}/common_criteria_firewall_rules
%{installer_dir}/keymaps
%{installer_dir}/timezones
%config /etc/multipath.conf.disabled
/etc/dracut.conf.d/installer.conf

%files startup
%defattr(775,root,root,-)

/etc/init.d/*
%{installer_dir}/preinit
%attr(755,root,root) %{installer_dir}/S05ramdisk
%attr(755,root,root) %{installer_dir}/S06mount

%defattr(664,root,root,775)
/etc/modprobe.d/*
/etc/modules-load.d/iscsi.conf
/etc/depmod.d/depmod.conf

/etc/systemd/system/*/installer.conf

%doc

%files bootloader
%defattr(444,root,root,-)
%{efi_dir}/grub.cfg
%{efi_dir}/grub-usb.cfg
/boot/isolinux/isolinux.cfg

%post
# these are started by the installer
/usr/bin/systemctl disable multipathd
/usr/bin/systemctl mask iscsi-shutdown.service
/usr/bin/systemctl mask iscsiuio.service
/usr/bin/systemctl mask iscsid.service
/usr/bin/systemctl mask iscsid.socket
/usr/bin/systemctl mask iscsiuio.socket
/usr/bin/systemctl mask iscsi.service

# avoid to lock disks
/usr/bin/systemctl disable lvm2-lvmetad
/usr/bin/systemctl disable lvm2-monitor

%post startup
/sbin/chkconfig --add early-blacklist
/sbin/chkconfig --add interface-rename-sideway

%triggerin -- kernel
rm -rf /boot/*
rm -rf /usr/lib/modules/*/kernel/{drivers/infiniband,fs/{autofs4,btrfs,cramfs,exofs,gfs2,jfs,nfsd,ntfs,ocfs2,reiserfs,ufs,xfs}}

%triggerin -- xen-hypervisor
rm -rf /boot/*

%triggerin -- linux-firmware
basename -a $(find /lib/modules -type f -name '*.ko' | xargs modinfo --field firmware) | sort -u >/tmp/firmware-used.$$
for f in $(find /lib/firmware/ -type f); do
   b=$(basename $f)
   # keep files referenced by modinfo
   grep -q $b /tmp/firmware-used.$$ && continue
   # keep files referenced by modules
   grep -qr $b /lib/modules && continue
   rm -f $f
done
rm -f /tmp/firmware-used.$$

%changelog
* Tue Sep 7 2021 Lin Liu <lin.liu@citrix.com> - 10.7.5.3-1
- CP-37663: Backport winbind to Yangtze

* Mon Aug 16 2021 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.7.5.2-1
- CP-37784: Add common-criteria-prep menu entry to GRUB config

* Thu Jul 08 2021 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.7.5.1-1
- CA-343729: Log exceptions from iSCSI setup
- CA-349118: Create modprobe files during upgrade

* Fri May 29 2020 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.7.5-1
- CA-337001: Prompt the user to re-init the disk if needed

* Thu Mar 26 2020 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.7.4-1
- CA-336696: Handle errors when copying ownership
- CA-336693: Pass the correct parameters to setEfiBootEntry()
- CA-336693: Mount the ESP before restoring files
- CA-336693: Fix UEFI restore when there is no storage partition

* Wed Feb 05 2020 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.7.3-1
- CP-31090: Add network-init as a must-run service

* Thu Jan 23 2020 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.7.2-1
- CA-332901: Fix sshd service enable with cc-preparations
- CP-31092: Use different pool token generation in CC mode

* Thu Dec 12 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.7.1-1
- CP-32298: Don't expect firstboot state to exist

* Fri Dec 06 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.7.0-1
- Unbreak "safe" boot option on x2APIC machines
- CP-31092: Move CC preparations from firstboot script to the installer
- Remove outdated logrotate code
- CP-32298: Reimplement 95-legacy-logrotate in the installer

* Thu Nov 14 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.10-1
- CA-327217: Log efibootmgr failures when updating

* Thu Oct 31 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.9-1
- CP-32365: Remove bugtool.py
- CP-32365: Avoid logging ftp username/password in report.py
- Restore username/passwords in URL dialog
- Quote credentials correctly when saving reports
- CA-329747: Fix url-encoding issues with username/passwords
- CA-329747: Remove splitNetloc
- CA-329192: Don't reveal if username doesn't have a password
- CA-329837: Don't log the pool token

* Thu Oct 24 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.8-1
- CA-329192: Don't leak HTTP/FTP credentials

* Thu Aug 22 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.7-1
- CP-30221 / CA-325143: Switch to use chronyd for NTP
- CP-25099: Remove timeutil
- CP-25099: Set time before installation is started
- CA-293794: Prefer NTP servers from DHCP
- CP-30221: Use chrony.conf during upgrades

* Mon Aug 12 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.6-1
- CA-310853: Add check to TUI call to prevent erroneous backward jumps
- CA-322208: Ignore errors raised by deactivateAll()
- CP-32019: Rework FCoE setup code to match post-installation

* Thu Jul 18 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.5-1
- CA-322144: Dump iBFT state for debugging
- CA-323227: Fix interactive installation with multipath
- CA-322479: Prevent iSCSI session(s) getting logged out during shutdown
- CA-317858: Re-enable job control for bash-shell
- Remove xencons kernel parameter
- CA-323599: Use full "com" parameter after installation

* Mon Jun 10 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.4-1
- Improve "Installing ..." text
- CA-319463: Don't restore certain files after upgrade

* Tue May 28 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.3-1
- CA-317754: Drop unneeded legacy disk/by-id symlink handling
- CA-317755: Fix installation when iBFT has no gateway
- CA-260176: Use new DNS format for management interface config
- CA-317642: Move repo length check earlier
- Code style improvements and modernization

* Wed May 08 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.2-1
- CA-296436: Disable mcelog on unsupported processors

* Fri Apr 12 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.1-1
- CA-311401: Handle the upgrade of disks from aacraid to smartpqi

* Wed Mar 27 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.6.0-1
- CP-30566: Add support for VirtIO Blk devices
- CA-312390: Fix agetty parametrs, treat all ttys equally, fixing serial handling.
- CA-313248 Match old branding EFI boot entries

* Thu Mar 07 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.5.3-1
- CA-311773: Keep order of updates specified in the answerfile
- CA-311543: Add serial support to ISOLINUX

* Wed Feb 27 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.5.2-1
- CA-311306: Bump crash kernel memory to 256M

* Fri Feb 22 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.5.1-2
- CA-301159: Drop dependency on xenserver-systemd-networkd

* Thu Feb 14 2019 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.5.1-1
- CA-310736: iscsi: Don't use gateway if target is on the same subnet

* Wed Feb 06 2019 jenniferhe <jennifer.herbert@citrix.com> - 10.5.0-1
- CA-306058: Don't try to restart iscsid
- CA-306058: Fix setting up routing for iSCSI NICs
- CP-30205: Remove legacy toolstack db references
- CP-29627: Increase dom0 memory for the installer
- CP-30557: Update installer to use new default_memory_for_version() function.
- CA-309041: Apply updated dom0 memory size during upgrade

* Tue Jan 15 2019 rossla <ross.lagerwall@citrix.com> - 10.4.1-1
- CP-30205: Remove legacy 6.x upgrade/restore code
- CP-30232: Remove dead code in product._readSettings()

* Thu Dec 06 2018 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.4.0-1
- CA-299191: write Dom0 uuid into /etc/sysconfig/xencommons
- CA-304547: Rewrite iSCSI code
- CA-304341: Prevent upgrades from versions of XS prior to 7
- CA-304341: Prevent restores to versions of XS prior to 7
- CP-30152: Use up to 16 vCPUs for installation
- CP-30232: Add an option to use the legacy partition layout

* Fri Nov 23 2018 Simon Rowe <simon.rowe@citrix.com> - 10.3.3-1
- CA-296524: retain any domain part of the hostname
- CA-294300: Removed XenCenter.iso entry from fstab.

* Fri Oct 12 2018 Simon Rowe <simon.rowe@citrix.com> - 10.3.2-1
- CP-29241: hide CC UEFI menu entry for master
- CP-29685: Switch network stack to Linux Bridge when in CC mode

* Fri Sep 28 2018 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.3.1-1
- CP-29085: transform to cc-preparations
- CP-29091: parse service tag in answer file
- CA-298702: COMPANY_PRODUCT_BRAND missing in /etc/xensource-inventory

* Thu Aug 30 2018 Simon Rowe <simon.rowe@citrix.com> - 10.3.0-1
- CA-293743: wipe log system before mkfs
- CA-290899: use file system tree rooted directory for rpm query
- CA-295381: all packages should be upgraded

* Fri Jul 27 2018 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.2.9-1
- CA-294085: log management config alternatives

* Wed Jul 18 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.8-1
- CP-28832: Host installer should tolerate indexes on PCI bus locations

* Tue Jul 17 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.7-1
- CP-28858: add extension to systemd-udevd.service

* Mon Jun 25 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.6-1
- CA-290859 - Use `1-$MAX` syntax for dom0's vcpus
- CA-291084: fix make-ramdisk option for update packaging format
- CA-291084: restore S06mount
- CA-291084: prevent multiple runs of subordinate scripts
- Fixup whitespace

* Wed May 30 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.5-1
- CA-289215: drop new format build from visual_version

* Tue May 15 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.4-1
- CA-289278: Preserve xapi-clusterd db config after reboot

* Mon Apr 23 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.3-1
- CA-288312: prefer hostname from /etc/hostname
- CA-288312: do not write hostname to /etc/sysconfig/network

* Mon Apr 16 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.2-1
- CA-283258: Ensure swap partition gets mounted during boot

* Thu Feb 01 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.1-1
- CA-280682: Capture stderr rather than leaking to the console

* Wed Jan 10 2018 Simon Rowe <simon.rowe@citrix.com> - 10.2.0-1
- CA-259657: determine timezone from /etc/localtime
- CA-259657: extract keyboard map from /etc/vconsole.conf in preference
- CA-259657: do not create obsolete files
- CA-259657: hoist writei18n() to initial seq definition
- CA-259657: always write /etc/hostname

* Tue Nov 14 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.6-1
- CA-273150: Add missing import

* Mon Oct 16 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.5-1
- CA-267428: Remove leftover logging
- CA-267428: Use splitlines() rather than split()

* Tue Oct 03 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.4-3
- CA-267961: delete unwanted firmware

* Mon Oct 02 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.4-2
- CA-267877: inhibit creation of the initrd and cleanup /boot

* Wed Sep 20 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.4-1
- CA-265171: Install bootloader to partition if needed
- CA-263790: Don't remove the wrong volume group during upgrade
- CA-266760: Allow upgrading packages from a driver disk
- CA-266760: Fix progress calculation when upgrading packages

* Tue Sep 05 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.3-1
- CA-261633: Add a helper function for multipath root
- CA-261633: Fix restoring when using a multipath root
- CA-263669: Don't hardcode the product name for upgrades
- CA-263669: Fix upgrade with incorrect product names

* Tue Aug 15 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.2-1
- CP-22698: drop package properties from inventory
- Complete removal of BUILD_NUMBER
- CA-260649: Use the default LVM directory
- Change crash kernel to 192M somewhere below 4G

* Wed Jun 28 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.1-1
- CA-257937: Ensure enough free space is available on the log partition
- Remove some obsolete files

* Wed Jun 14 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.0-2
- CP-22732: remove unwanted kernel files

* Mon Jun 05 2017 Simon Rowe <simon.rowe@citrix.com> - 10.1.0-1
- CP-22508: extend branding with build number
- Replace tabs with spaces.  Python, being whitespace delimited, is sensitive to this being correct.
- CA-255453: Add /var/lib/xcp/blobs to the restore list

- CA-255453: Speed up restoring files
- CP-17277, CP-17273: Enable tagged vlan support for host installer network.
- CP-17274, CP-17275: Adding VLAN support for XenServer management interface
- CP-17508: setting MANAGEMENT_INTERFACE in xensource_inventory is not needed during fresh install.
- CP-17702: Parsing of existing management interface when VLAN is present.
- CP-17703: 'more info' on 'use existing network' shows ip on vlan networks also.

* Fri Apr 28 2017 Ross Lagerwall <ross.lagerwall@citrix.com> - 10.0.7-1
- CA-250911: write BRAND_CONSOLE_URL to /etc/xensource-inventory

* Thu Apr 20 2017 Simon Rowe <simon.rowe@citrix.com> - 10.0.6-1
- remove build number from welcome message
- CA-250335: Update results dict in place
- CA-250869: Check fcoeadm contains VLAN id before parsing it

* Tue Apr 11 2017 Simon Rowe <simon.rowe@citrix.com> - 10.0.5-1
- Remove unused module loading functions from hardware.py
- CA-247345: Preserve log partition during upgrade (take 2)
- CA-249629: Fix partitionsOnDisk() to handle multipath devices
- CA-249629: Match sfdisk output lines containing a colon correctly

* Mon Apr 03 2017 Simon Rowe <simon.rowe@citrix.com> - 10.0.4-1
- Revert "CA-247345: Preserve log partition during upgrade"

* Mon Mar 27 2017 Simon Rowe <simon.rowe@citrix.com> - 10.0.3-1
- CA-247345: Preserve log partition during upgrade

* Wed Mar 15 2017 Simon Rowe <simon.rowe@citrix.com> - 10.0.2-1
- tui: Fix appearance of build identifier

* Thu Mar 09 2017 Simon Rowe <simon.rowe@citrix.com> - 10.0.1-1
- CA-246294: Don't hard-code the list of devices for local media

