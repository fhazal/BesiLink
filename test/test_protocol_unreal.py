import unittest

from pylinkirc.protocols import unreal

import protocol_test_fixture as ptf

class UnrealProtocolTest(ptf.BaseProtocolTest):
    proto_class = unreal.UnrealProtocol

    # Fork tests: PREFIX= handling from PROTOCTL (UnrealIRCd 6 with or without the
    # chanmodes/chanowner, chanadmin and halfop modules).

    def test_protoctl_prefix_full(self):
        self.p.handle_protoctl(None, 'PROTOCTL', ['CHANMODES=beI,fkL,lFH,cdimnprstzCDGKMNOPQRSTVZ',
                                                  'PREFIX=(qaohv)~&@%+', 'SID=0SD'])
        self.assertEqual(self.p.prefixmodes, {'q': '~', 'a': '&', 'o': '@', 'h': '%', 'v': '+'})
        for name, char in (('owner', 'q'), ('admin', 'a'), ('op', 'o'), ('halfop', 'h'), ('voice', 'v')):
            self.assertEqual(self.p.cmodes[name], char)
        self.assertEqual(self.p.uplink, '0SD')

    def test_protoctl_prefix_only_op_and_voice(self):
        # Matches a server with chanowner, chanadmin and halfop blacklisted.
        self.p.cmodes.pop('halfop', None)
        self.p.cmodes.pop('admin', None)
        self.p.cmodes.pop('owner', None)
        self.p.handle_protoctl(None, 'PROTOCTL', ['PREFIX=(ov)@+', 'SID=0SD'])
        self.assertEqual(self.p.prefixmodes, {'o': '@', 'v': '+'})
        self.assertEqual(self.p.cmodes['op'], 'o')
        self.assertEqual(self.p.cmodes['voice'], 'v')
        for missing in ('halfop', 'admin', 'owner'):
            self.assertNotIn(missing, self.p.cmodes)

    def test_protoctl_prefix_malformed_is_ignored(self):
        before = dict(self.p.prefixmodes)
        self.p.handle_protoctl(None, 'PROTOCTL', ['PREFIX=(ov)@', 'SID=0SD'])  # length mismatch
        self.assertEqual(self.p.prefixmodes, before)

if __name__ == '__main__':
    unittest.main()
