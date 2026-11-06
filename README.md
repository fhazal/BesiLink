<div align="center">

# 🔗 BajuBesi Labs · BesiLink

**Link IRC networks together, so they feel like one.**<br>
A maintained fork of PyLink · UnrealIRCd 6 · InspIRCd 4 · real server links · tagged nicks

[![tests](https://github.com/fhazal/BesiLink/actions/workflows/tests.yml/badge.svg)](https://github.com/fhazal/BesiLink/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/besilink?color=3776ab&logo=pypi&logoColor=white)](https://pypi.org/project/besilink/)
![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-3776ab?logo=python&logoColor=white)
[![Release](https://img.shields.io/github/v/release/fhazal/BesiLink?color=8b5cf6)](https://github.com/fhazal/BesiLink/releases)
[![License: MPL 2.0](https://img.shields.io/badge/license-MPL--2.0-e8b04b)](LICENSE.MPL2)

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20BajuBesi-5865f2?logo=discord&logoColor=white&style=for-the-badge)](https://discord.gg/TCmm8cH3GE)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20us-ff5e5b?logo=ko-fi&logoColor=white&style=for-the-badge)](https://ko-fi.com/bajubesi)

</div>

> [!NOTE]
> BesiLink is an unofficial fork of [PyLink](https://github.com/PyLink/PyLink) by James Lu and contributors, which was archived in January 2023. It is kept up by **BajuBesi Labs** and is not affiliated with the original authors. Configs and plugins from PyLink 3.1 keep working.

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🌉 Real network relay
Share channels between networks. Remote users show up in the nick list as real users, with WHOIS, modes, kicks, topics and bans relayed both ways.

</td>
<td width="50%" valign="top">

### 🆕 Modern IRCds
Links **UnrealIRCd 6** and **InspIRCd 4** (`target_version: insp4`) as real servers, and still supports the IRCds PyLink always did.

</td>
</tr>
<tr>
<td valign="top">

### 🏷️ Tagged nicks
Pick how remote users look: `Belon[SKT]` and `Bamboo[JVN]` with short tags per network, or the classic `Belon/net`. Reserve the tags so nobody can pretend to be a relayed user.

</td>
<td valign="top">

### 🔒 Safe by default
Fixed TLS on current Python, pinned certificate fingerprints, and no U-line needed, so your channel operators keep full control over relayed users.

</td>
</tr>
<tr>
<td valign="top">

### 🗺️ Map and uptime for opers
`/msg BesiLink map` shows every linked network in one tree; `uptime` and `/STATS u` show how long each link has been up.

</td>
<td valign="top">

### 📦 Easy to run
`pip install besilink`, a systemd unit or Docker. Upgrading from PyLink 3.1 is a drop-in swap: same command, same config.

</td>
</tr>
</table>

---

## 👀 What it looks like

The same channel on two networks, linked by BesiLink:

```
#chat on UnrealIRCd                    #chat on InspIRCd
──────────────────────                 ──────────────────────
@Alice                                 @Carol
 Bob                                    Dave
@Carol[JVN]    ← from InspIRCd          @Alice[SKT]   ← from UnrealIRCd
 Dave[JVN]                               Bob[SKT]

<Carol[JVN]> hello from the other side    <Alice[SKT]> hi Carol!
```

---

## 🚀 Quick start

```bash
python3 -m venv ~/venv
~/venv/bin/pip install besilink
curl -o pylink.yml https://raw.githubusercontent.com/fhazal/BesiLink/main/example-conf.yml
~/venv/bin/pylink pylink.yml
```

Then follow the **[install guide](docs/besilink-install.md)**: configuration, systemd, Docker, relaying a channel and the [tested UnrealIRCd 6 + InspIRCd 4 setup](docs/besilink-install.md#5-tested-setup-unrealircd-6--inspircd-4-as-real-server-links).

> [!TIP]
> Coming from PyLink? Run `pip uninstall pylinkirc` first, then `pip install besilink`. Your `pylink.yml` and relay database stay as they are.

---

## 🧭 Supported IRCds

| IRCd | Module | Status |
| --- | --- | --- |
| **UnrealIRCd 6.x** | `unreal` | ✅ Tested on a live network |
| **InspIRCd 4.x** | `inspircd` + `target_version: insp4` | ✅ Tested on a live network |
| InspIRCd 2.0 / 3.x | `inspircd` (`insp20` / `insp3`) | ✅ InspIRCd 3 tested live, 2.0 inherited |
| UnrealIRCd 4.2 / 5.0 | `unreal` | 🧪 Covered by the test suite |
| charybdis, ChatIRCd, juno, ratbox, Elemental | `ts6` | 🧪 Covered by the test suite |
| Nefarious, IRCu, snircd, beware | `p10` | 🧪 Covered by the test suite |
| IRCd-Hybrid, ngIRCd | `hybrid`, `ngircd` | 📦 Inherited from PyLink |
| Any other IRCd, as a bot | `clientbot` | ✅ Tested live (relay leaf only) |

<details>
<summary><b>Notes per IRCd from the original PyLink docs</b></summary>

The detailed per-IRCd notes (KLINE `shared{}` blocks, ngIRCd settings, P10 host hiding and so on) are unchanged and live in the [original PyLink README](docs/pylink-original-readme.md#supported-ircds).

</details>

---

## 📚 Documentation

| Guide | What's inside |
| --- | --- |
| [Install guide](docs/besilink-install.md) | Install, configure, run as a service, relay a channel, upgrade |
| [Relay quick start](docs/relay-quickstart.md) | Relay commands, CLAIM, LINKACL, services compatibility |
| [Advanced relay config](docs/advanced-relay-config.md) | IP sharing, nick and server options, more relay settings |
| [Permissions reference](docs/permissions-reference.md) | Every permission node for `permissions:` |
| [FORK.md](FORK.md) · [RELNOTES.md](RELNOTES.md) | What BesiLink changed, what was tested, release notes |

---

## 🙏 Credits

- **[PyLink](https://github.com/PyLink/PyLink)** by James Lu (jlu5) and contributors, the project BesiLink is built on.
- Made and maintained by **BajuBesi Labs**. Not affiliated with the PyLink authors, UnrealIRCd or InspIRCd.
- Code under the [Mozilla Public License 2.0](LICENSE.MPL2), documentation under [CC BY-SA 4.0](LICENSE.CC-BY-SA-4.0), the same licences as PyLink.
- Found a bug? Please open an [issue](https://github.com/fhazal/BesiLink/issues).

<div align="center">

<sub>Made with ☕ by <b>BajuBesi Labs</b></sub>

</div>
