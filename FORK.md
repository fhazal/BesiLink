# PyLink fork notice

This is an unofficial fork of [PyLink](https://github.com/PyLink/PyLink) by James Lu (jlu5) and contributors.
The upstream project was archived on 2023-01-04 and is no longer maintained. This fork starts from upstream
commit `43e41cd` ("PyLink 3.1.0") and keeps its licenses unchanged:

- code: Mozilla Public License 2.0 (`LICENSE.MPL2`)
- documentation: CC BY-SA 4.0 (`LICENSE.CC-BY-SA-4.0`)

Changed files carry their original headers. Changes made in this fork are marked in the code with
"Fork change" or "Fork addition" comments.

## Changes so far

| Area | Change |
| --- | --- |
| `classes.py` | Fixed `SSL: BAD_RECORD_MAC` / "Connection lost" on TLS connections with Python 3.12 and TLS 1.3. The select thread (reads) and the queue thread (writes) used one SSL socket at the same time, which OpenSSL does not allow. Every socket operation now takes a per-connection lock. The send retry loop no longer spins a CPU core, partial writes are completed, and the queue thread always releases the shutdown event. |
| `protocols/unreal.py` | Reads `PREFIX=` from `PROTOCTL` and only enables the prefix modes the uplink really has. Works on UnrealIRCd 6 with `chanmodes/chanowner`, `chanadmin` and `halfop` blacklisted (`PREFIX=(ov)@+`). |
| `protocols/inspircd.py` | New `target_version: insp4` (InspIRCd 4, protocol 1206): `SERVER` without the hops field, `UID` with real and displayed username, two-parameter `FHOST` and `FIDENT`. `insp3` stays the default and keeps working against InspIRCd 4 through its compatibility layer. |
| `utils.py` | `clear_persistent_channels(None, namespace)` no longer raises `KeyError` when the namespace is empty (seen on every shutdown with no relay channels). |
| `test/` | New tests for the prefix handling and for the InspIRCd 4 `UID` / `SERVER` parsing. |

## Tested

- UnrealIRCd 6.2.7 and InspIRCd 4.12.1 linked as real servers through PyLink on isolated loopback sandboxes,
  with a relayed channel between them: join, part, quit, messages, nick changes, topics, modes, kicks, away, extban
  translation, oper status, CHGHOST, CHGIDENT and CHGNAME in both directions.
- TLS Clientbot connections: 0 of 5 starts failed with the fix, against 4 of 5 without it.
- `python -m unittest` for the protocol and utility test modules.
- Burst: 120 users on UnrealIRCd 6.2.7 and 120 on InspIRCd 4.12.1 joining one relayed channel within seconds:
  every user appears on both sides, no errors.
- Ban lists: 60 bans set on UnrealIRCd are mirrored on InspIRCd and removed again correctly.
- Split and relink: stopping either server makes PyLink reconnect on its own after the autoconnect delay, the channel
  membership is rebuilt on both sides and messages flow both ways again.
- UnrealIRCd 6 only: its own channel flood protection can set `+b ~time:10:~security-group:unknown-users`.
  PyLink does not copy that Unreal-specific ban to servers that cannot represent it (this is intended).

## Not tested yet

SASL and services accounts, Anope, bursts far beyond a few hundred users, and more than two networks at once.

## Requirements and use

Same as upstream (Python 3.7 or newer, PyYAML, cachetools). The relay plugin additionally needs `relay_clientbot` to be
enabled on Clientbot networks.

Maintained by BajuBesi Labs.
