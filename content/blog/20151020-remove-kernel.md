Title: Remove unused kernels
Date: 2015-01-20
Category: blog
Tags: bash,oneliner,precise,kernel
Slug: remove-kernel
Author: arnulf.heimsbakk@met.no

Removes all but current kernel and headers for freeing up disk space. This is a note for internal use and tested for Ubuntu Precise. Use at your own risk :) 
 
```bash
dpkg-query -f '${Package}\n' -W |  egrep 'linux-(headers|image)-[[:digit:]].*(|-generic)' | grep -v $(uname -r | sed 's/-generic//') | sudo xargs apt-get -q -q -yy --purge remove
```

## Breakdown

 1. List all packages.
 2. Find only linux-image and linux-header packages with version number, not the two main meta packages.
 3. Remove the linux-image and linux-header for running kernel from the list.
 4. Purge all listed packages from system without asking any questions.

###### vim: set syn=markdown spell spl=en:

