import unittest

from pylinkirc.classes import Server
from pylinkirc.protocols import inspircd

import protocol_test_fixture as ptf

class InspIRCdProtocolTest(ptf.BaseProtocolTest):
    proto_class = inspircd.InspIRCdProtocol

    # Fork tests: InspIRCd 4 (protocol 1206) support.

    def _setup_uplink(self, remote_proto_ver):
        self.p.remote_proto_ver = remote_proto_ver
        self.p.servers['0S4'] = Server(self.p, None, 'remote.server', internal=False)

    def test_supported_ircds_include_insp4(self):
        self.assertIn('insp4', self.p.SUPPORTED_IRCDS)
        self.assertGreaterEqual(self.p.MAX_PROTO_VER, 1206)
        # The default must stay InspIRCd 3 so existing configs do not change behaviour.
        self.assertEqual(self.p.DEFAULT_IRCD, 'insp3')

    def test_handle_uid_1205(self):
        self._setup_uplink(1205)
        args = ['0S4AAAAAA', '1429934638', 'jlu5', '192.0.2.1', 'hidden.host', 'jlu5ident', '192.0.2.1',
                '1429934638', '+iow', '+', 'real name']
        res = self.p.handle_uid('0S4', 'UID', args)
        user = self.p.users['0S4AAAAAA']
        self.assertEqual((user.nick, user.ident, user.host, user.realhost, user.ip),
                         ('jlu5', 'jlu5ident', 'hidden.host', '192.0.2.1', '192.0.2.1'))
        self.assertEqual(res['ident'], 'jlu5ident')

    def test_handle_uid_1206_has_real_and_displayed_username(self):
        # 1206: UID uuid ts nick real-host displayed-host real-user displayed-user ip signon modes params :real
        self._setup_uplink(1206)
        args = ['0S4AAAAAA', '1429934638', 'jlu5', '192.0.2.1', 'hidden.host', 'realuser', 'shownuser',
                '192.0.2.1', '1429934638', '+iow', '+', 'real name']
        res = self.p.handle_uid('0S4', 'UID', args)
        user = self.p.users['0S4AAAAAA']
        self.assertEqual((user.nick, user.ident, user.host, user.realhost, user.ip, user.realname),
                         ('jlu5', 'shownuser', 'hidden.host', '192.0.2.1', '192.0.2.1', 'real name'))
        self.assertEqual(res['ip'], '192.0.2.1')

    def test_handle_server_uplink_1206_has_no_hops_field(self):
        self.p.serverdata = dict(self.p.serverdata or {}, recvpass='secret')
        self.p.uplink = None
        self.p.remote_proto_ver = 1206
        self.p.handle_server(None, 'SERVER', ['remote.server', 'secret', '0S4', 'Remote description'])
        self.assertEqual(self.p.uplink, '0S4')
        self.assertEqual(self.p.servers['0S4'].name, 'remote.server')

    def test_handle_server_uplink_1205_keeps_hops_field(self):
        self.p.serverdata = dict(self.p.serverdata or {}, recvpass='secret')
        self.p.uplink = None
        self.p.remote_proto_ver = 1205
        self.p.handle_server(None, 'SERVER', ['remote.server', 'secret', '0', '0S4', 'Remote description'])
        self.assertEqual(self.p.uplink, '0S4')

if __name__ == '__main__':
    unittest.main()
