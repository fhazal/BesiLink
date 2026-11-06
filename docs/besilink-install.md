# Installing BesiLink

This guide gets a BesiLink relay running on a Linux server. BesiLink uses the same command (`pylink`), package
(`pylinkirc`) and configuration format as PyLink 3.1, so the rest of the [docs](README.md) still apply.

## Requirements

- Python 3.9 or newer (tested on 3.9 to 3.13)
- An IRC network you can link to as a server (UnrealIRCd 6, InspIRCd 3 or 4, and the other IRCds listed in the
  README), **or** a plain client connection for Clientbot mode

## 1. Install

Run BesiLink as its own unprivileged user, in a virtual environment:

```bash
sudo useradd -m -s /bin/bash pylink
sudo -u pylink -i
git clone https://github.com/fhazal/BesiLink.git
python3 -m venv ~/venv
~/venv/bin/pip install ./BesiLink
mkdir ~/run && cp BesiLink/example-conf.yml ~/run/pylink.yml
```

To pin a release, use `git clone --branch v3.2.0 ...`. Optional extras: `pip install "./BesiLink[password-hashing]"`
(hashed admin passwords, see `pylink-mkpasswd`) and `"./BesiLink[relay-unicode]"` (transliterates Unicode nicks).

## 2. Configure

Edit `~/run/pylink.yml` and keep it private (`chmod 600`), because it holds link passwords. Delete the example network
blocks you do not use.

A **server link** (remote users show up as real users in the nick list):

```yaml
servers:
    inspnet:
        ip: 127.0.0.1
        port: 7000
        sendpass: "change-me"
        recvpass: "change-me"
        hostname: "pylink.example.net"
        sid: "0PY"
        sidrange: "8##"
        protocol: inspircd
        target_version: insp4   # InspIRCd 4; use insp3 for InspIRCd 3
        netname: "Example Net"
        ssl: true
        autoconnect: 10
```

For UnrealIRCd 6 use `protocol: unreal`. The IRCd needs a matching `link` block and a `ulines` entry for PyLink's
hostname. Pick a `sidrange` that no other server on the network uses.

A **Clientbot** connection (no server access needed; remote users appear as `[net] <nick> text` lines from the bot):

```yaml
    othernet:
        ip: irc.example.org
        port: 6697
        ssl: true
        protocol: clientbot
        netname: "Other Net"
        pylink_nick: Bridge
        autoconnect: 30
        throttle_time: 0.3
```

Plugins for a relay:

```yaml
plugins:
    - commands
    - networks
    - servprotect
    - relay
    - relay_clientbot   # required if any network uses protocol: clientbot
```

Without `relay_clientbot`, messages from Clientbot networks are silently dropped.

## 3. Run as a service

`/etc/systemd/system/pylink.service`:

```ini
[Unit]
Description=BesiLink IRC relay
After=network-online.target
Wants=network-online.target

[Service]
User=pylink
WorkingDirectory=/home/pylink/run
ExecStart=/home/pylink/venv/bin/pylink -n pylink.yml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pylink
journalctl -u pylink -f
```

## 4. Relay a channel

Log in to PyLink by private message, using the account from the `login:` block:

```
/msg PyLink login <user> <password>
```

Then:

1. On a **server-linked** network, join the channel and run `/msg PyLink create #chan`. Clientbot networks cannot
   own a relay channel.
2. On each other network, from inside the channel, run `/msg PyLink link <ownernet> #chan` (`<ownernet>` is the short
   network name from the config and is case sensitive).
3. If services or ops on a linked network should be allowed to change modes, add that network to the claim list:
   `/msg PyLink claim #chan ownernet,othernet`. Mode changes from networks that are not on the list are reverted.

See [relay-quickstart.md](relay-quickstart.md) for services compatibility notes (for example, turn off clone kills in
Anope or Atheme) and for handling disputes.

## Upgrading

```bash
sudo -u pylink -i
cd BesiLink && git pull   # or: git fetch --tags && git checkout v<new version>
~/venv/bin/pip install --force-reinstall --no-deps .
exit
sudo systemctl restart pylink
```

Back up `pylink.yml` and `pylinkrelay.db` first. To upgrade from upstream PyLink 3.1, install BesiLink into the
existing venv the same way. The config and relay database stay compatible.

## Reporting problems

Open an issue at https://github.com/fhazal/BesiLink/issues with your IRCd versions, the protocol module and
`target_version` you use, and the relevant log lines (remove passwords first).
