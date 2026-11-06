"""
BesiLink addition: tests for relay nick tagging (classic nick/net and bracket tags like Belon[SKT]).
"""
import tempfile
import unittest

from pylinkirc import conf, world

# Importing relay creates its DataStore; save_delay 0 keeps it from starting a save timer thread,
# and data_dir points at a temp folder so no database is written into the source tree.
conf.conf.setdefault('pylink', {})
conf.conf['pylink']['save_delay'] = 0
conf.conf['pylink']['data_dir'] = tempfile.mkdtemp(prefix='besilink-test-')
conf.conf.setdefault('relay', {})

from pylinkirc.plugins import relay  # noqa: E402


class FakeIrc:
    def __init__(self, name, serverdata=None, maxnicklen=30, caps=('slash-in-nicks',), taken=()):
        self.name = name
        self.serverdata = serverdata or {}
        self.maxnicklen = maxnicklen
        self.casemapping = 'rfc1459'
        self._caps = set(caps)
        self._taken = {n.lower(): 'UID-' + n for n in taken}

    def has_cap(self, cap):
        return cap in self._caps

    def nick_to_uid(self, nick):
        return self._taken.get(nick.lower())

    def match_text(self, glob, text):
        return False


class RelayNickTagTest(unittest.TestCase):
    def setUp(self):
        self._old_relay = dict(conf.conf['relay'])
        self._old_nets = dict(world.networkobjects)
        world.networkobjects.clear()
        world.networkobjects['skinternet'] = FakeIrc('skinternet', {'relay_nick_tag': 'SKT'})
        world.networkobjects['besinet'] = FakeIrc('besinet', {'relay_nick_tag': 'JVN'})
        world.networkobjects['untagged'] = FakeIrc('untagged')

    def tearDown(self):
        conf.conf['relay'].clear()
        conf.conf['relay'].update(self._old_relay)
        world.networkobjects.clear()
        world.networkobjects.update(self._old_nets)

    def test_classic_separator_unchanged(self):
        conf.conf['relay']['separator'] = '/'
        target = FakeIrc('besinet')
        self.assertEqual(relay.normalize_nick(target, 'skinternet', 'Belon'), 'Belon/skinternet')

    def test_brackets_global_option(self):
        conf.conf['relay']['tag_style'] = 'brackets'
        self.assertEqual(relay.normalize_nick(FakeIrc('besinet'), 'skinternet', 'Belon'), 'Belon[SKT]')
        self.assertEqual(relay.normalize_nick(FakeIrc('skinternet'), 'besinet', 'Bamboo'), 'Bamboo[JVN]')

    def test_brackets_per_target_network(self):
        target = FakeIrc('besinet', {'relay_tag_style': 'brackets'})
        self.assertEqual(relay.normalize_nick(target, 'skinternet', 'Belon'), 'Belon[SKT]')

    def test_brackets_falls_back_to_network_name(self):
        conf.conf['relay']['tag_style'] = 'brackets'
        self.assertEqual(relay.normalize_nick(FakeIrc('besinet'), 'untagged', 'Joe'), 'Joe[untagged]')

    def test_brackets_truncate_keeps_tag(self):
        conf.conf['relay']['tag_style'] = 'brackets'
        target = FakeIrc('besinet', maxnicklen=15)
        nick = relay.normalize_nick(target, 'skinternet', 'AVeryLongNickname')
        self.assertEqual(nick, 'AVeryLongN[SKT]')
        self.assertEqual(len(nick), 15)

    def test_brackets_collision_adds_underscore(self):
        conf.conf['relay']['tag_style'] = 'brackets'
        target = FakeIrc('besinet', taken=('Belon[SKT]',))
        self.assertEqual(relay.normalize_nick(target, 'skinternet', 'Belon'), 'Belon_[SKT]')
        target = FakeIrc('besinet', taken=('Belon[SKT]', 'Belon_[SKT]'))
        self.assertEqual(relay.normalize_nick(target, 'skinternet', 'Belon'), 'Belon__[SKT]')

    def test_brackets_tag_is_sanitised(self):
        conf.conf['relay']['tag_style'] = 'brackets'
        world.networkobjects['weird'] = FakeIrc('weird', {'relay_nick_tag': 'S K!T'})
        self.assertEqual(relay.normalize_nick(FakeIrc('besinet'), 'weird', 'Joe'), 'Joe[SKT]')

    def test_brackets_with_untagged_style_still_tags_on_collision(self):
        conf.conf['relay']['tag_style'] = 'brackets'
        conf.conf['relay']['tag_nicks'] = False
        target = FakeIrc('besinet', taken=('Belon',))
        self.assertEqual(relay.normalize_nick(target, 'skinternet', 'Belon'), 'Belon[SKT]')


if __name__ == '__main__':
    unittest.main()
