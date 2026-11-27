import unittest
from rooted.concepts import calculate

class ConceptTests(unittest.TestCase):
    def test_permissions(self):
        r=calculate(dict(tool='permissions',mode='600'))
        self.assertEqual(r['rows'][0][1],'-rw-------')
        with self.assertRaises(ValueError):calculate(dict(tool='permissions',mode='999'))
    def test_network_normalization_and_small_subnets(self):
        r=calculate(dict(tool='subnet',network='192.0.2.10/24'));rows=dict(r['rows'])
        self.assertEqual(rows['Network'],'192.0.2.0/24');self.assertEqual(rows['Conventional host count'],'254')
        self.assertEqual(dict(calculate(dict(tool='subnet',network='192.0.2.0/31'))['rows'])['Conventional host count'],'2')
    def test_large_ipv6_uses_arithmetic_not_enumeration(self):
        r=calculate(dict(tool='subnet',network='2001:db8::/32'))
        self.assertEqual(dict(r['rows'])['Total addresses'],str(2**96))
    def test_real_hash_bytes(self):
        r=calculate(dict(tool='hash',original='hello',changed='hello\n'))
        rows=dict(r['rows']);self.assertEqual(rows['Original UTF-8 bytes'],'5');self.assertEqual(rows['Edited UTF-8 bytes'],'6')
        self.assertNotEqual(rows['Original SHA-256'],rows['Edited SHA-256'])
    def test_lexical_paths_and_commands(self):
        r=calculate(dict(tool='paths',cwd='/home/learner/case',path='../notes.txt'))
        self.assertEqual(dict(r['rows'])['Normalized result'],'/home/learner/notes.txt')
        r=calculate(dict(tool='command',command='cat "my notes.txt" | wc -l'))
        self.assertEqual(r['rows'][1][1],'my notes.txt');self.assertIn('shell operator',r['rows'][2][0])
        with self.assertRaises(ValueError):calculate(dict(tool='command',command='cat "unterminated'))

if __name__=='__main__':unittest.main()
