---
title: Linux Kernel Module Development Guide - A Tutorial for Beginners
date: 2024-03-12T13:58:16
updated: 2024-03-12T13:58:16
categories:
  - tutorials
tags:
  - dev
  - kernel
---
Looking to dip your toes into Linux kernel module development? Well, you're in for a treat! We've got a no-frills, step-by-step guide that'll take you from zero to hero in no time. In this blog, we'll walk you through setting up your local development environment, using qemu for safe testing, and the optional (but highly recommended) integration of gdb for debugging. Perfect for beginners, this guide will simplify the seemingly complex world of kernel development into an approachable and manageable process. Ready to get started?

# Outcome
- stable local development setup  
- A **qemu** VM for safe testing  
- A **gdb** hooked to the test qemu VM for debuging (Optional, strongly advised)

# Tools
**qemu** - "open source machine emulator and virtualizer." [viz.](https://wiki.qemu.org/Main_Page)  
**gdb** (optional) - "the GNU Project debugger, allows you to see what is going on inside another program while it executes -- or what another program was doing at the moment it crashed." [viz.](https://www.sourceware.org/gdb/)

# Whom
This guide is aimed at newcomers to kernel development. It combines various components into an easy-to-follow workflow for quick and efficient start in kernel development.

_This is by no means a definitive guide or a best solution, yet it is one that has served me well._

# Technical Notes
File names used in this document are relative. Following the naming conventions provided will ease the referencing process but isn't mandatory.

# Set-up
---

## fedora dependencies

``` shell
sudo dnf group install "Development Tools"
```

```
sudo dnf install qemu-kvm qemu-img qemu-system-x86_64 gcc flex bzip2 make ccache bison openssl-devel bc elfutils-libelf-devel
```

optional:
menuconfig for modifying the kernel configuration using gui menu

``` shell
sudo dnf install ncurses-devel
```
## Qemu VM
> The following section is in based on the following qemu [fedora guide](https://developer.fedoraproject.org/tools/virtualization/installing-qemu-on-fedora-linux.html)
> _Non-fedora users should also be able to follow it._

### Steps
1. Download a ISO, server flavor(no gui) is probably all you need depending on the module's purpose
2. Create the following folder structure and move the ISO file accordingly
~~~
├── cdromimg
│   └── distro.iso
└── datadrct
~~~

3.  Create a raw image for the VM, this is a "virtual" disk
``` shell
qemu-img create -f raw datadrct/image.raw 16G
```

>_Note: if you use non-minimal system flavor or will be using a lot of disk space, increase the size accordingly._

4. **Start** the VM and complete the installation. I have chosen the username to be `devel` which will be used in rest of this tutorial.

``` shell
qemu-system-x86_64 \
    -boot menu=on \
    -m 2048 \
    -cpu max \
    -smp 4 \
    -cdrom cdromimg/distro.iso> \
    -drive file=datadrct/image.raw,format=raw \
    -accel kvm
```

### Final folder structure
Create a backup of the Image after a completing the system backup including the development tools and all you need before starting the development
~~~
├── cdromimg
│   └── distro.iso
└── datadrct
    ├── image.raw
    └── image.raw.backup
~~~

### Running the VM (Maintenance)
With this you will run in graphics mode unless you add `-nographics`, You can use it for the VM maintenance. 

``` shell
qemu-system-x86_64 \
    -boot menu=on \
    -m 2048 \
    -cpu max \
    -smp 4 \
    -s  \
    -drive file=datadrct/image.raw,format=raw \
    -accel kvm \
    -net nic \
    -net user,hostfwd=tcp::2323-:22
```
_You will need to run it at leas once to determine the root mount point e.g `/dev/sda3`. You can do so after running the VM by executing the `df` command, look for the `/` symbol in the `Mounted on` column and write it down._
### Running the VM (Development)
VM can access internet  
We can SSH to the VM using localhost and a arbitrary port (2323)

``` shell
qemu-system-x86_64 \
    -m 2048 \
    -cpu max \
    -smp 4 \
    -s \
    -kernel path/to/kernel/arch/x86_64/boot/bzImage \
    -drive file=datadrct/image.raw,format=raw \
    -accel kvm \
    -nographic \
    -append "root=/dev/sda3 nokaslr" \
    -net nic \
    -net user,hostfwd=tcp::2323-:22
```
* `root=/dev/sda3` - specify the root partition based. see previous running option
* Feel free to exclude the `-nographic`  option if you wish to have a separate gui window for the VM.
* `-kernel` specifies the path to the bzImage

### Mount the VM's image
> Don't do this when the VM is running

``` shell
sudo mount -t ext4 -o loop,offset=<1234> datadrct/image.raw /mnt/image
```
__-t \<filesystem\>__ - depends on your installation  
__offset=1234__ - ofset of the partition that we want to mount  

> To determine the offset `sudo fdisk -l <path/to/image.raw>` look for Type: Linxu File

## kernel

### Get sources

``` shell
git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
```
> _If you are developing for specific distro, then seach for the disto's sources e.g. fedora-ark_

### configure

| kernel config option      | value | description                                     |
| ------------------------- | ----- | ----------------------------------------------- |
| CONFIG\_GDB\_SCRIPTS        | Y     | Enables GDB script support for kernel debugging |
| CONFIG\_DEBUG\_INFO\_REDUCED | N     | Keeps full debug information                    |
| CONFIG\_FRAME\_POINTER      | Y     | Useful for stack traces in debugging            |

#### (Optional) Copy existing config and modify it.

``` shell
cp /boot/config-`uname -r`* .config
```

#### run configuration
_this will go through configuration options that you need to set. There shouldn't be any if you have done the previous step ^._
``` shell
make oldconfig
```
>_you can use `menuconfig` instead of `oldconfig` to use GUI version_

### build

``` shell
make bzImage
```

``` shell
make modules
```

### Install
[Mount the VM's image](# Mount the VM's image)

``` shell
sudo make modules_install INSTALL_MOD_PATH=/mnt/image
```

``` shell
sudo make headers_install INSTALL_HDR_PATH=/mnt/image/usr
```

``` shell
sudo make install INSTALL_PATH=/mnt/image/boot
```

## GDB
In the kernel source directory:

``` shell
make scripts_gdb
```

add `add-auto-load-safe-path /path/to/linux-build` to `~/.gdbinit`

# Development
---
>_This guide doesn't covert the actual module developement as there are enough reources on this toppic https://www.thegeekstuff.com/2013/07/write-linux-kernel-module/

## Rebuilding the kernel
If you modify the module files only then perform the following:

``` shell
make modules M=/path/to/module.ko
```
>_If you modify something outside of the module itself (e.g. some files in include, something in the kernel core..) then re[build](#build)  the kernel again_

## Provide the build to the VM system
The following will copy the module to the user's home directory.

``` shell
scp -P 2323 path/to/module.ko devel@localhost:
```

## Load the kernel module inside the VM

``` shell
sudo insmod path/to/module.ko
```

alternatively you can use `modprobe` but be sure that you have copied the kernel to the right directory i.e. `/lib/modules/...`

## debug the kernel
Run gdb on in the kernel sources (Not in the VM)

``` shell
gdb vmlinux
```

Connect gdb to VM
``` shell
target remote :1234
```
_The system freezes upon connecting. Use `continue` to resume._

_Feel free to interrupt at any moment to enter __gdb__ commands by pressing `CTRL+C`_

>_[Load](#load-the-kernel-module-inside-the-vm) the modules before the next step_

load kernel and module symbols

``` shell
lx-symbols
```

__continue__ as normal...

# Things to watch out for
- Avoid running the VM when the `image.raw` is mounted.
- Incrementally test your setup.
- Use version control like Git for your development.

# Scriptlets
_scripts you might find useful_

Mount the image, kill the running VM if needed

``` shell
ps -a | grep qemu && pkill qemu
sudo mount -t ext4 -o loop,offset=8592031744 datadrct/image.raw /mnt/image
```

Automatically unmounted the image before running the VM

``` shell
sudo umount /mnt/image/
qemu-system-x86_64 -boot menu=on -m 2048 -cpu max...
```

Reload module in VM

``` shell
lsmod | grep module > /dev/null && sudo rmmod --force module  
sudo insmod ~/module.ko && lsmod | grep module
```
_replace `module` with the name of your module_

# Other development notes
## Working on VM
You can use Tmux ([viz.](https://github.com/tmux/tmux/wiki/Getting-Started)) on a local machine as well as the VM for testing.
You are encouraged to try it even if you aren't familiar with it.

### Attaching remote (VM) Tmux session
First you have to create a Tmux session on the VM you would do so by running it at the system startup (adding `tmux` to startup script).

Then you attach from the local machine to the VM using:
```
ssh -p 2323 devel@localhost -t tmux attach-session
```

---
# Resources
https://docs.kernel.org/dev-tools/gdb-kernel-debugging.html  
https://developer.fedoraproject.org/tools/virtualization/installing-qemu-on-fedora-linux.html  
http://dalleau.re/post/qemu\_debugging/  
https://nickdesaulniers.github.io/blog/2018/10/24/booting-a-custom-linux-kernel-in-qemu-and-debugging-it-with-gdb/  
