Title: Vagrant with OpenStack
Date: 2015-01-16
Tags: howto, openstack, vagrant
Slug: vagrant-openstack
Author: arnulf.heimsbakk@met.no
Modified: 2015-03-12

[Vagrant]: https://www.vagrantup.com
[OpenStack]: http://www.openstack.org
[Github]: https://github.com
[vagrant-openstack-plugin]: https://github.com/cloudbau/vagrant-openstack-plugin

If you want to use [Vagrant] with [OpenStack], you need to prepare [Vagrant] with installing the [vagrant-openstack-plugin]. I had some problems installing it directly through `vagrant plugin install`. I had to clone it from [Github] and install it manually. 

## One time configuration

### Install OpenStack plugin in Vagrant

```bash
sudo apt-get install ruby1.9.1 git virtualbox
cd /tmp
# At writing moment the latest version of Vagrant is the following version.
wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.2_x86_64.deb
sudo dpkg -i vagrant_1.7.2_x86_64.deb
git clone https://github.com/cloudbau/vagrant-openstack-plugin
cd vagrant-openstack-plugin
gem build vagrant-openstack-plugin.gemspec
vagrant plugin install vagrant-openstack-plugin-*.gem
```

Add a dummy box to [Vagrant] thats needed by the plugin.

```bash
vagrant box add dummy https://github.com/cloudbau/vagrant-openstack-plugin/raw/master/dummy.box
```

### Download OpenStack RC file 

* Log into OpenStack
* Download OpenStack API RC file
  * Go to `Project` -> `Compute` -> `Access & Security` -> `API Access` 
  * Down RC file by hitting `Download OpenStack RC File`
  * Put `$USER-openrc.sh` in your `~/` or somewhere you prefer

## Configure a Vagrant VM

### Vagrantfile

This is a default generic Vagrant file which starts a `m1.tiny` flavor image of Ubuntu Utopic. It requires that you already have added your ssh key to OpenStack. Please add your ssh key with the name `$USER_ssh_key`. 

```ruby
require 'vagrant-openstack-plugin'
                                                                               
Vagrant.configure("2") do |config|
  config.vm.box = "dummy"
  config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".git/"

  # Make sure the private key from the key pair is provided
  config.ssh.private_key_path = "~/.ssh/id_rsa"
                                                                                 
  config.vm.provider :openstack do |os|
    os.username     = "#{ENV['OS_USERNAME']}"
    os.api_key      = "#{ENV['OS_PASSWORD']}"
    os.flavor       = /m1.tiny/
    os.image        = "Ubuntu CI trusty 2014-09-22"
    os.endpoint     = "#{ENV['OS_AUTH_URL']}/tokens"
    os.keypair_name = "#{ENV['OS_USERNAME']}_ssh_key"
    os.ssh_username = "ubuntu"
    
    # The tenant have two networks, so need to specify at least one
    os.network = "vagrant"
    os.floating_ip        = :auto 
    os.floating_ip_pool   = "public"
  end

  config.vm.provision "shell", path: "bootstrap.sh"

  config.vm.provision "shell", inline: <<-SCRIPT
    # Set your country code here to get a local repositroy
    CN="no"
    grep -q repo.met.no /etc/apt/sources.list || sed -i~ "s#nova.clouds.archive.ubuntu.com#$CN.archive.ubuntu.com#g" /etc/apt/sources.list
    apt-get update
  SCRIPT

  config.vm.define "myvm" do |v|
  end
end 
```

### bootstrap.sh

Create your custom bootstrap file.

```bash
#!/bin/bash

# Your aditional bootstrap here...
```

## Running Vagrant 

Remember to source your OpenStack RC file before you run Vagrant up. You need to do that in each shell windows you are going to run Vagrant in.

```bash
source ~/$USER-openrc.sh
vagrant up --provider openstack
```

###### vim: set syn=markdown spell spl=en:

