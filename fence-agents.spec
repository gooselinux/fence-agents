###############################################################################
###############################################################################
##
##  Copyright (C) 2004-2010 Red Hat, Inc.  All rights reserved.
##
##  This copyrighted material is made available to anyone wishing to use,
##  modify, copy, or redistribute it subject to the terms and conditions
##  of the GNU General Public License v.2.
##
###############################################################################
###############################################################################

# keep around ready for later user
## global alphatag git0a6184070

Name: fence-agents
Summary: Fence Agents for Red Hat Cluster
Version: 3.0.12
Release: 8%{?alphatag:.%{alphatag}}%{?dist}
License: GPLv2+ and LGPLv2+
Group: System Environment/Base
URL: http://sources.redhat.com/cluster/wiki/
Source0: https://fedorahosted.org/releases/c/l/cluster/%{name}-%{version}.tar.bz2

Patch0: add_direct_support_for_wti_vmr.patch
Patch1: add_ipport_to_wti.patch
Patch2: fence_apc_fails_for_some_port_numbers.patch
Patch3: fence_scsi_do_not_truncate_log_file.patch
Patch4: fence_rsb_raise_exceptions.patch
Patch5: fence_ilo_will_throw_exception_if_user_has_no_power_privs.patch
Patch6: fence_rename_ibmblade_to_bladecenter_snmp_part1.patch
Patch7: fence_rename_ibmblade_to_bladecenter_snmp_part2.patch
Patch8: fix_syntax_error_in_code_that_opens_logfile.patch

ExclusiveArch: i686 x86_64

# shipped agents
%global supportedagents apc apc_snmp bladecenter bladecenter_snmp cisco_mds drac drac5 eps ibmblade ifmib ilo ilo_mp intelmodular ipmilan manual rsb scsi wti
%global deprecated ibmblade rsa sanbox2
%global testagents virsh vmware
%global requiresthirdparty egenera

## Runtime deps
Requires: sg3_utils telnet openssh-clients
Requires: pexpect net-snmp-utils
Requires: perl-Net-Telnet

# This is required by fence_virsh. Per discussion on fedora-devel
# switching from package to file based require.
Requires: /usr/bin/virsh

# This is required by fence_ipmilan. it appears that the packages
# have changed Requires around. Make sure to get the right one.
Requires: /usr/bin/ipmitool

## Setup/build bits

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

# Build dependencies
BuildRequires: perl python
BuildRequires: glibc-devel
BuildRequires: nss-devel nspr-devel
BuildRequires: libxml2-devel libvirt-devel
BuildRequires: libxslt pexpect
BuildRequires: clusterlib-devel >= 3.0.0
BuildRequires: corosynclib-devel >= 1.2.0-1
BuildRequires: openaislib-devel >= 1.1.1-1

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1 -b .add_direct_support_for_wti_vmr
%patch1 -p1 -b .add_ipport_to_wti
%patch2 -p1 -b .fence_apc_fails_for_some_port_numbers
%patch3 -p1 -b .fence_scsi_do_not_truncate_log_file
%patch4 -p1 -b .fence_rsb_raise_exceptions
%patch5 -p1 -b .fence_ilo_will_throw_exception_if_user_has_no_power_privs
%patch6 -p1 -b .fence_rename_ibmblade_to_bladecenter_snmp_part1
%patch7 -p1 -b .fence_rename_ibmblade_to_bladecenter_snmp_part2
%patch8 -p1 -b .fix_syntax_error_in_code_that_opens_logfile

# we inherit configure from cluster project. Configure it for vars we need.
# building from source directly without those parameters will NOT work.
# See http://www.redhat.com/archives/cluster-devel/2009-February/msg00003.html
%build
./configure \
  --sbindir=%{_sbindir} \
  --initddir=%{_sysconfdir}/rc.d/init.d \
  --libdir=%{_libdir} \
  --fence_agents='%{supportedagents} %{deprecated} %{testagents} %{requiresthirdparty}' \
  --disable_kernel_check

##CFLAGS="$(echo '%{optflags}')" make %{_smp_mflags}
# %{_smp_mflags} is broken upstream
CFLAGS="$(echo '%{optflags}')" make -C fence/agents

%install
rm -rf %{buildroot}
make -C fence/agents install DESTDIR=%{buildroot}

## tree fix up
# fix libfence permissions
chmod 0755 %{buildroot}%{_datadir}/fence/*.py

%clean
rm -rf %{buildroot}

%description
Red Hat Fence Agents is a collection of scripts to handle remote
power management for several devices.

%files 
%defattr(-,root,root,-)
%doc doc/COPYING.* doc/COPYRIGHT doc/README.licence
%{_sbindir}/fence*
%{_datadir}/fence
%{_mandir}/man8/fence*

%changelog
* Tue Aug 10 2010 Lon Hohberger <lhh@redhat.com> - Version: 3.0.12-8
- Fix syntax error in code that opens logfile.
  (fix_syntax_error_in_code_that_opens_logfile.patch)
  Resolves: rhbz#608887

* Wed Jul 21 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.12-7
- fence_rsb: Raise exceptions not strings with python 2.6
  (fence_rsb_raise_exceptions.patch)
  Resolves: rhbz#612941
- fence_ilo: will throw exception if user does not have power priviledges
  (fence_ilo_will_throw_exception_if_user_has_no_power_privs.patch)
  Resolves: rhbz#615255
- fence agents support clean up:
  drop support for baytech, brocade, mcdata, rackswitch and bullpap
  deprecate rsa and sanbox2
  rename ibmblade to bladecenter_snmp and add compatibility symlink
  (fence_rename_ibmblade_to_bladecenter_snmp_part1.patch)
  (fence_rename_ibmblade_to_bladecenter_snmp_part2.patch)
  Resolves: rhbz#616559
- spec file changelog cleanup for older releases
- rename Patch0 to be consistent with the others

* Mon Jun 28 2010 Lon Hohberger <lhh@redhat.com> - 3.0.12-6
- Don't truncate fence_scsi log files
  (fence_scsi_do_not_truncate_log_file.patch)
  Resolves: rhbz#608887

* Wed Jun 23 2010 Marek Grac <mgrac@redhat.com> - 3.0.12-4
- fence_apc fails for some port numbers
  (fence_apc_fails_for_some_port_numbers.patch)
- Resolves: rhbz#606297

* Fri Jun 18 2010 Marek Grac <mgrac@redhat.com> - 3.0.12-3
- Add support for non-default TCP ports for WTI fence agent
  (add_ipport_to_wti.patch)
- Resolves: rhbz#579059

* Wed May 19 2010 Lon Hohberger <lhh@redhat.com> - 3.0.12-2
- Add direct support for WTI VMR
  (add_direct_support_for_wti_vmr.patch)
  Resolves: rhbz#578617
- Fix changelog for 3.0.12-1 release (add missing bugzilla entries)

* Mon May 10 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.12-1
- Rebase on top of new upstream bug fix only release:
  * drop all bug fix patches.
  * Addresses the follwing issues:
    from 3.0.11 release:
  Resolves: rhbz#583019, rhbz#583017, rhbz#583948, rhbz#584003
  * Rebase:
  Resolves: rhbz#582351
- Stop build on ppc and ppc64.
  Resolves: rhbz#590985
- Update list of supported agents.

* Wed Apr  7 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.9-3
- Remove 'ipport' option from WTI fence agent
  (remove_ipport_option_from_wti_fence_agent.patch)
  Resolves: rhbz#579059

* Tue Mar 23 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.9-2
- Add workaround to broken snmp return codes
  (workaround_broken_snmp_return_codes.patch)
  Resolves: rhbz#574027

* Tue Mar  2 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.9-1
- new upstream release:
  Resolves: rhbz#557349, rhbz#564471
- spec file update:
  * update spec file copyright date
  * use bz2 tarball
  * bump minimum requirements for corosync/openais
  * fence-agents should not Requires fence-virt directly
  * stop shipping fence_xvmd

* Thu Feb 25 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.7-4
- Resolves: rhbz#568002
- Do not build fence-agents on s390 and s390x.

* Mon Feb  8 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.7-3
- Fix build of several agents (fix-build-with-man-page.patch)
- Resolves: rhbz#562806

* Thu Jan 14 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.7-2
- Stop shipping unsupported agents
- Add patch to fix man page shipping (man-page-cleanup.patch)

* Tue Jan 12 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.7-1
- New upstream release

* Mon Dec  7 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.6-2
- Use the correct tarball from upstream

* Mon Dec  7 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.6-1
- New upstream release (drop fence_head.diff)
- spec file updates:
  * use new Source0 url
  * use file based Requires for ipmitools (rhbz: 545237)

* Fri Dec  4 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.5-2.git0a6184070
- Drop fence_xvm from upstream (fence_head.diff)
- spec file updates:
  * Drop unrequired comments
  * Readd alpha tag and clean it's usage around
  * Requires: fence-virt in sufficient version to provide fence_xvm

* Fri Nov 20 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.5-1
- New upstream release

* Tue Oct 27 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.4-3
- Switch to file based Requires for virsh

* Tue Oct 27 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.4-2
- Fix Requires: on libvirt/libvirt-client

* Wed Oct 21 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.4-1
- New upstream release
- BuildRequire libxslt and pexpect for automatic man page generation

* Wed Sep 23 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.3-1
- New upstream release

* Mon Aug 24 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.2-2
- Fix changelog.

* Mon Aug 24 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.2-1
- New upstream release
- spec file updates:
  * remove dust from runtime dependencies

* Thu Aug 20 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.1-1
- New upstream release

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.0-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul  8 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-14
- New upstream release
- spec file updates:
  * Update copyright header
  * final release.. undefine alphatag
  * BuildRequires and Requires corosync/openais 1.0.0-1 final.

* Thu Jul  2 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-13.rc4
- New upstream release.
- spec file updates:
  * BuildRequires / Requires: latest corosync and openais
  * Drop --enable_virt. Now default upstream

* Sat Jun 20 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-12.rc3
- New upstream release.
- spec file updates:
  * BuildRequires / Requires: latest corosync and openais

* Wed Jun 10 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-11.rc2
- New upstream release  + git94df30ca63e49afb1e8aeede65df8a3e5bcd0970
- spec file updates:
  * BuildRequires / Requires: latest corosync and openais
  * Build fence_xvm unconditionally now that libvirt is everywhere
  * Drop telnet_ssl wrapper in favour of nss version

* Tue Mar 24 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-10.rc1
- New upstream release.
- Cleanup BuildRequires to avoid to pull in tons of stuff when it's not
  required.
- Update BuildRoot usage to preferred versions/names.
- Stop shipping powermib. Those are not required for operations anymore.

* Thu Mar 12 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-9.beta1
- Fix arch check for virt support.
- Drop unrequired BuildRequires.
- Drop unrequired Requires: on perl.

* Mon Mar  9 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-8.beta1
- New upstream release.
- Update corosync/openais BuildRequires and Requires.

* Fri Mar  6 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-7.alpha7
- New upstream release.
- Drop fence_scsi init stuff that's not required anylonger.

* Tue Mar  3 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-6.alpha6
- New upstream release.

* Tue Feb 24 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-5.alpha5
- Fix directory ownership.

* Tue Feb 24 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-4.alpha5
- Drop Conflicts with cman.

* Mon Feb 23 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-3.alpha5
- New upstream release. Also address comments from first package review.

* Thu Feb 19 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-2.alpha4
- Add comments on how to build this package.
- Update build depends on new corosynclib and openaislib.

* Thu Feb  5 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-1.alpha4
- New upstream release.
- Fix datadir/fence directory ownership.
- Update BuildRequires: to reflect changes in corosync/openais/cluster
  library split.

* Tue Jan 27 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 3.0.0-1.alpha3
- Initial packaging
