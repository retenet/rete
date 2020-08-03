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


