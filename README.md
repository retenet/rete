# rete
Containerized Web Browsing for Added Protection 

##  Install

```bash
python3 -m pip install rete
```

**NOTE** : Install requires `$USER` to be in the docker group, or sudo permissions.


## Usage

```bash
➜ rete -h      
usage: rete version 1.0.2 [-h] [-p PROFILE] [-t] [--config | --rm | --update]
                          [{brave,chromium,firefox,opera,tbb}]

positional arguments:
  {brave,chromium,firefox,opera,tbb}
                        Supported Browsers

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        Profile Name
  -t                    Temporary Profile
  --config              Open Config for Editing
  --rm                  Stop and Remove ALL Browsers
  --update              Check for Upates

```

## Config
```bash
➜ cat ~/.config/rete/rete.yml
browser:
  name: firefox
  #proxy:
  #dns:
  #  ip: 
  #  host:
  #  doh: false

profile:
  default: personal
  list: [htb, lan, media, personal, shopping, work]

#vpn:
#  provider:
#  user:
#  pass:
#  config: 
```

### proxy
  Currently the expected value is an HTTP/HTTPS/SOCKS proxy value in the form of: PROTO://IP:PORT </br>
  Proxy also supports BurpSuite by passing the value `burpsuite`.

### dns
  ip: as the name implies, the ip of the dns server you want to use.</br>
  host: the appropriate hostname and is the value used when DoH is enabled</br>
  doh: enabled or disabled DNS over HTTP

### profile
default: the profile to load by default on browser start</br>
list: the list of available profiles to use, feel free to add/remove any of them</br>
 the lan profile is a special restricted profile that only has access to RFC1918 IPs

### vpn
 See retenet/tunle for more detailed documentation.</br>
 
 provider: one of the supported providers</br>
 user: username for login</br>
 pass: password for login</br>
 config: this is used for custom openvpn configs. It **must** be fullpath</br>
 Typical args would be provider with user/pass, or simply just a config</br>

### Example configs

Standard Usage
```
browser:
  name: firefox
  dns:
    ip: 1.1.1.1
    host: cloudflare-dns.com
    doh: true

profile:
  default: personal
  list: [htb, lan, media, personal, shopping, work]
```

Burpsuite
```
browser:
  name: firefox
  proxy: burpsuite

profile:
  default: personal
  list: [htb, lan, media, personal, shopping, work]
```

OpenVPN
```
browser:
  name: firefox

profile:
  default: personal
  list: [htb, lan, media, personal, shopping, work]

vpn:
  config: /home/user/ovpn/wh1tf3fox.ovpn
```

Tor Transparent Proxy
```
browser:
  name: firefox

profile:
  default: personal
  list: [htb, lan, media, personal, shopping, work]

vpn:
  provider: tor
```

Pia
```
browser:
  name: firefox

profile:
  default: personal
  list: [htb, lan, media, personal, shopping, work]

vpn:
  provider: pia
  user: abcdef
  pass: abcdef
```

**NOTE**: if OpenVPN fails to load try adding:
```
pull-filter ignore "ifconfig-ipv6 "
pull-filter ignore "route-ipv6 "
```
to your ovpn config
