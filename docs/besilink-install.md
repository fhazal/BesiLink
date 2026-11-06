# Installing BesiLink

This guide gets a BesiLink relay running on a Linux server. BesiLink uses the same command (`pylink`), import package
(`pylinkirc`) and configuration format as PyLink 3.1, so the rest of the [docs](README.md) still apply. On PyPI it is
published as **`besilink`**.

## Requirements

- Python 3.10 or newer (tested on 3.10 to 3.13)
- An IRC network you can link to as a server (UnrealIRCd 6, InspIRCd 3 or 4, and the other IRCds listed in the
  README), **or** a plain client connection for Clientbot mode

## 1. Install

Run BesiLink as its own unprivileged user, in a virtual environment. From PyPI:

```bash
sudo useradd -m -s /bin/bash pylink
sudo -u pylink -i
python3 -m venv ~/venv
~/venv/bin/pip install besilink
mkdir ~/run && curl -o ~/run/pylink.yml https://raw.githubusercontent.com/fhazal/BesiLink/main/example-conf.yml
```

Or from git (to run unreleased code, or pin a tag with `git clone --branch v3.2.1 ...`):

```bash
git clone https://github.com/fhazal/BesiLink.git
~/venv/bin/pip install ./BesiLink
```

Optional extras: `pip install "besilink[password-hashing]"` (hashed admin passwords, see `pylink-mkpasswd`) and
`"besilink[relay-unicode]"` (transliterates Unicode nicks).

### Docker

```bash
git clone https://github.com/fhazal/BesiLink.git && cd BesiLink
docker build -t besilink .
docker run -d --name besilink --restart unless-stopped -v /srv/besilink:/pylink besilink
```

`/srv/besilink` holds `pylink.yml` and the relay database. The container runs as UID 10000, so give that UID write
access to the folder.

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

The service nick is `PyLink` unless you set `pylink::nick` (for example `nick: BesiLink`, then use `/msg BesiLink ...`).

## 5. Tested setup: UnrealIRCd 6 + InspIRCd 4 as real server links

This is the setup BesiLink runs in production: BesiLink on the same machine as one UnrealIRCd 6.2 server and one
InspIRCd 4.12 server, linked to both over loopback TLS, with no U-line.

**UnrealIRCd 6** (`unrealircd.conf` on the server BesiLink connects to; a TLS `serversonly` listen block must exist):

```
link besilink.example.net {
    incoming { mask 127.0.0.1; }
    password "change-me";
    class servers;
}
# No ulines entry: relayed users stay kickable and bannable by your channel operators.
```

**InspIRCd 4** (`inspircd.conf` / `links.conf`):

```
<bind address="127.0.0.1" port="17979" type="servers" sslprofile="Servers">
<link name="besilink.example.net" ipaddr="127.0.0.1" allowmask="127.0.0.1/32" port="17979"
      sendpass="change-me-1" recvpass="change-me-2" sslprofile="Servers">
```

**BesiLink** (`pylink.yml`):

```yaml
servers:
    unrealnet:
        ip: 127.0.0.1
        port: 6900                 # the Unreal TLS serversonly port
        sendpass: "change-me"
        recvpass: "change-me"
        hostname: "besilink.example.net"
        sid: "0BL"
        sidrange: "7##"
        netname: "Unreal Net"
        protocol: unreal
        maxnicklen: 30
        ssl: true
        ssl_fingerprint: "<sha256 of the Unreal server certificate>"
        relay_nick_tag: "UNR"
    inspnet:
        ip: 127.0.0.1
        port: 17979
        sendpass: "change-me-2"    # InspIRCd's recvpass
        recvpass: "change-me-1"    # InspIRCd's sendpass
        hostname: "besilink.example.net"
        sid: "0BL"
        sidrange: "7##"
        netname: "Insp Net"
        protocol: inspircd
        target_version: insp4
        maxnicklen: 30
        ssl: true
        ssl_fingerprint: "<sha256 of the InspIRCd server certificate>"
        relay_nick_tag: "INS"

relay:
    tag_style: brackets            # relay users appear as Nick[UNR] / Nick[INS]
```

BesiLink logs the uplink's fingerprint on the first connect ("Uplink's TLS/SSL certificate fingerprint ..."). Copy it
into `ssl_fingerprint`; afterwards a different certificate is refused, and the log names the mismatch. Update the
fingerprint when you replace a server certificate.

**Things to know:**

- **Nick length:** set the same, large enough nick length on every network (`maxnick="30"` in InspIRCd's `<limits>`).
  Tags count towards it; long nicks are cut before the tag.
- **Reserve the tags** for local users on every server: UnrealIRCd `ban nick { mask "*[INS]"; reason "Reserved for
  relay users"; }`, InspIRCd `<badnick nick="*[UNR]" reason="Reserved for relay users">`. These only affect local
  users, so BesiLink can still introduce relayed users.
- **Anope on InspIRCd:** relayed users carry the IP `0.0.0.0`, so `os_session` would kill them after the session limit.
  Add an exception: `/msg OperServ EXCEPTION ADD 0.0.0.0 100 BesiLink relay users`. Anope on UnrealIRCd skips users
  without an IP and needs nothing.
- **UnrealIRCd server notices** show relayed users with an empty IP (`[]`) and only announce them when they leave, so
  connection-flood scripts that key on IPs do not react to them.
- **Claim:** run `/msg BesiLink claim #chan net1,net2,net3` so operators and services on every network may set modes.
- **Network map and uptime for opers:** load the `servermaps` and `stats` plugins and grant
  `"$ircop": ["servermaps.map", "servermaps.localmap", "stats.uptime", "stats.u"]`. Keep `stats.c` / `stats.o`
  (link blocks, accounts) for admins only.

## Upgrading

```bash
sudo -u pylink /home/pylink/venv/bin/pip install --upgrade besilink
# from git instead: cd BesiLink && git pull && ~/venv/bin/pip install --force-reinstall --no-deps .
sudo systemctl restart pylink
```

Back up `pylink.yml` and `pylinkrelay.db` first.

**Coming from upstream PyLink (`pylinkirc` on PyPI) or BesiLink 3.2.0:** both installed under the PyPI name
`pylinkirc`. Remove it first, because both names install the same files:

```bash
sudo -u pylink /home/pylink/venv/bin/pip uninstall -y pylinkirc
sudo -u pylink /home/pylink/venv/bin/pip install besilink
```

The config and relay database stay compatible.

## Reporting problems

Open an issue at https://github.com/fhazal/BesiLink/issues with your IRCd versions, the protocol module and
`target_version` you use, and the relevant log lines (remove passwords first).
