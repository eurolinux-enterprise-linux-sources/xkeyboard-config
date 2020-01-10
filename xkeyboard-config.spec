# INFO: Package contains data-only, no binaries, so no debuginfo is needed
%define debug_package %{nil}

#global gitdate 20110415
#global gitversion 19a0026b5

Summary: X Keyboard Extension configuration data
Name: xkeyboard-config
Version: 2.11
Release: 3%{?gitdate:.%{gitdate}git%{gitversion}}%{?dist}
License: MIT
Group: User Interface/X
URL: http://www.freedesktop.org/wiki/Software/XKeyboardConfig
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%if 0%{?gitdate}
Source0:    %{name}-%{gitdate}.tar.bz2
Source1:    make-git-snapshot.sh
Source2:    commitid
%else
Source0: http://xorg.freedesktop.org/archive/individual/data/xkeyboard-config/%{name}-%{version}.tar.bz2
%endif

# Bug 923160 - Removal of /usr/share/X11/xkb/keymap.dir breaks NX
Patch01: 0001-Revert-Remove-.dir-generation.patch
# Bug 1164507 - Broken ru-phonetic layout since 2.11 -- update to 2.12
Patch02: 0001-Back-to-previous-ru-phonetic-keyboard-layout.patch

BuildArch: noarch

BuildRequires: pkgconfig
BuildRequires: xorg-x11-util-macros
BuildRequires: xkbcomp
BuildRequires: perl(XML::Parser)
BuildRequires: intltool
BuildRequires: gettext
BuildRequires: git-core
BuildRequires: automake autoconf libtool pkgconfig
BuildRequires: glib2-devel
BuildRequires: xorg-x11-proto-devel libX11-devel
BuildRequires: libxslt
# RHEL6 special: xkbcomp is required for keymap.dir generation (#923160)
BuildRequires: xorg-x11-xkb-utils

# NOTE: Any packages that need xkbdata to be installed should be using
# the following "Requires: xkbdata" virtual provide, and not directly depending
# on the specific package name that the data is part of.  This ensures
# futureproofing of packaging in the event the package name changes, which
# has happened often.
Provides: xkbdata
# NOTE: We obsolete xorg-x11-xkbdata but currently intentionally do not
# virtual-provide it.  The idea is to find out which packages have a
# dependency on xorg-x11-xkbdata currently and fix them to require "xkbdata"
# instead.  Later, if this causes a problem, which seems unlikely, we can
# add a virtual provide for the old package name for compatibility, but
# hopefully everything is using the virtual name and we can avoid that.
Obsoletes: xorg-x11-xkbdata

%description
This package contains configuration data used by the X Keyboard Extension 
(XKB), which allows selection of keyboard layouts when using a graphical 
interface. 

%package devel
Summary: Development files for %{name}
Group: User Interface/X
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig

%description devel
%{name} development package

%prep
%setup -q -n %{name}-%{?gitdate:%{gitdate}}%{!?gitdate:%{version}}

%if 0%{?gitdate}
git checkout -b fedora
sed -i 's/git/&+ssh/' .git/config
if [ -z "$GIT_COMMITTER_NAME" ]; then
    git config user.email "x@fedoraproject.org"
    git config user.name "Fedora X Ninjas"
fi
git commit -am "%{name} %{version}"
%else
git init
if [ -z "$GIT_COMMITTER_NAME" ]; then
    git config user.email "x@fedoraproject.org"
    git config user.name "Fedora X Ninjas"
fi
git add .
git commit -a -q -m "%{name} %{version} baseline."
%endif

git am -p1 %{patches} < /dev/null

%build
AUTOPOINT="intltoolize --automake --copy" autoreconf -v --force --install || exit 1
%configure \
    --enable-compat-rules \
    --with-xkb-base=%{_datadir}/X11/xkb \
    --disable-xkbcomp-symlink \
    --with-xkb-rules-symlink=xorg \
    --disable-runtime-deps

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p"

# Remove unnecessary symlink
rm -f $RPM_BUILD_ROOT%{_datadir}/X11/xkb/compiled
%find_lang %{name} 

# Bug 923160 - directory keymap/ was removed upstream in 77d09b66a so we
# don't autogenerate. For 923160, an empty file is enough
touch $RPM_BUILD_ROOT%{_datadir}/X11/xkb/keymap.dir

# Create filelist
{
   FILESLIST=${PWD}/files.list
   pushd $RPM_BUILD_ROOT
   find .%{_datadir}/X11/xkb -type d | sed -e "s/^\./%dir /g" > $FILESLIST
   find .%{_datadir}/X11/xkb -type f | sed -e "s/^\.//g" >> $FILESLIST
   popd
}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f files.list -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS README NEWS TODO COPYING docs/README.* docs/HOWTO.*
%{_datadir}/X11/xkb/rules/xorg
%{_datadir}/X11/xkb/rules/xorg.lst
%{_datadir}/X11/xkb/rules/xorg.xml
%{_mandir}/man7/xkeyboard-config.*

%files devel
%defattr(-,root,root,-)
%{_datadir}/pkgconfig/xkeyboard-config.pc

%changelog
* Fri Jan 16 2015 Peter Hutterer <peter.hutterer@redhat.com> 2.11-3
- Install the keymap.dir file as well (#923160)

* Tue Dec 16 2014 Peter Hutterer <peter.hutterer@redhat.com> 2.11-2
- Reinstate generation of *.dir files (#923160)
- Revert to previous ru(phonetic) layout (#1164507)

* Thu Apr 24 2014 Adam Jackson <ajax@redhat.com> 2.11-1
- xkeyboard-config 2.11

* Fri Nov 02 2012 Peter Hutterer <peter.hutterer@redhat.com> 2.6-6
- Rebuild with patched xkbcomp (related #872057)

* Thu Nov 01 2012 Peter Hutterer <peter.hutterer@redhat.com> - 2.6-5
- Fix {?dist} tag (#871460)

* Tue Aug 28 2012 Peter Hutterer <peter.hutterer@redhat.com> 2.6-4
- Merge from F18 (#835284)

* Wed Jun 29 2011 Peter Hutterer <peter.hutterer@redhat.com> 2.3-1
- xkeyboard-config 2.3 (#713863)
- Revert 2.3 Sinhala (lk) changes, they require newer x11proto/libX11
  updates
- update Source0 line to ftp.x.org

* Wed May 04 2011 Peter Hutterer <peter.hutterer@redhat.com> 1.6-8
- Add Rupee sumbol (#651774)

* Wed Mar 03 2010 Peter Hutterer <peter.hutterer@redhat.com> 1.6-7
- Only package files in /usr/share/X11/xkb to avoid wrong directory
  ownership.

* Tue Feb 16 2010 Peter Hutterer <peter.hutterer@redhat.com> 1.6-6
- Package the translations too (#565714)

* Wed Jan 06 2010 Peter Hutterer <peter.hutterer@redhat.com> 1.6-5
- Apply patches manually instead of requiring git.

* Tue Nov 24 2009 Peter Hutterer <peter.hutterer@redhat.com> 1.6-4
- xkeyboard-config-1.6-abnt2-dot.patch: fix KP dot on abnt2 (#470153)

* Tue Aug 18 2009 Peter Hutterer <peter.hutterer@redhat.com> 1.6-3
- xkeyboard-config-1.6-caps-super.patch: add caps:super option (#505187)
- xkeyboard-config-1.6-caps-hyper.patch: add caps:hyper option (#505187)

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri May 29 2009 Peter Hutterer <peter.hutterer@redhat.com> - 1.6-1
- xkeyboard-config 1.6
- Dropping all patches, merged upstream.

* Tue Apr 07 2009 Peter Hutterer <peter.hutterer@redhat.com> - 1.5-5
- xkeyboard-config-1.5-terminate.patch: remove Terminate_Server from default
  pc symbols, add terminate:ctrl_alt_bksp.

* Thu Mar 05 2009 Peter Hutterer <peter.hutterer@redhat.com> - 1.5-4
- xkeyboard-config-1.5-suspend-hibernate.patch: Map I213 to XF86Suspend, and
  I255 to XF86Hibernate.

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 02 2009 Peter Hutterer <peter.hutterer@redhat.com> 1.5-2
- xkeyboard-config-1.5-evdevkbds.patch: include model-specifics when using
  evdev.

* Mon Feb 02 2009 Peter Hutterer <peter.hutterer@redhat.com> 
- purge obsolete patches.

* Wed Jan 28 2009 Peter Hutterer <peter.hutterer@redhat.com> 1.5-1
- xkeyboard-config 1.5
