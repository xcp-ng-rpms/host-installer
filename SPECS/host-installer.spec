Summary: XenServer Installer
Name: host-installer
Version: 10.2.9
Release: 1
License: GPL
Group: Applications/System
Source0: https://code.citrite.net/rest/archive/latest/projects/XS/repos/%{name}/archive?at=%{version}&format=tar.gz&prefix=%{name}-%{version}#/%{name}-%{version}.tar.gz
# This is where we get 'multipath.conf' from
BuildRequires: sm xenserver-multipath xenserver-lvm2

Requires: xenserver-multipath xenserver-lvm2 xenserver-systemd-networkd iscsi-initiator-utils

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
Summary: XenServer Installer
Group: Applications/System
Requires: host-installer
Requires: openssh-server
Requires(post): initscripts
%description startup
XenServer installer startup files

%package bootloader
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
cp timeutil support.sh %{buildroot}/usr/bin

mkdir -p %{buildroot}%{installer_dir}
cp -R \
        tui \
        init \
        keymaps \
        timezones \
        answerfile.py \
        backend.py \
        bugtool.py \
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
    %{buildroot}/etc/depmod.d \
    %{buildroot}/etc/dracut.conf.d \
    %{buildroot}/etc/systemd/system/systemd-udevd.d \
    %{buildroot}/etc/udev/rules.d \
    %{buildroot}/usr/lib/udev

cp startup/{interface-rename-sideway,early-blacklist} %{buildroot}/etc/init.d/
cp startup/functions %{buildroot}/etc/init.d/installer-functions

cp startup/{early-blacklist.conf,bnx2x.conf} %{buildroot}/etc/modprobe.d/
cp startup/blacklist %{buildroot}/etc/modprobe.d/installer-blacklist.conf
cp startup/modprobe.mlx4 %{buildroot}/etc/modprobe.d/mlx4.conf

cp startup/depmod.conf %{buildroot}/etc/depmod.d/

cp startup/61-xenrt.rules %{buildroot}/etc/udev/rules.d/

cp startup/{id_serial.sh,scsi_id.old,cciss_id} %{buildroot}/usr/lib/udev/

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
%{installer_dir}/bugtool.py
/usr/bin/support.sh
/usr/bin/timeutil

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
/etc/depmod.d/depmod.conf

/etc/udev/rules.d/61-xenrt.rules
%attr(775,root,root) /usr/lib/udev/id_serial.sh
%attr(775,root,root) /usr/lib/udev/scsi_id.old
%attr(775,root,root) /usr/lib/udev/cciss_id

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

