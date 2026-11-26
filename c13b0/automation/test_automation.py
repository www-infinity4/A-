import json, sqlite3, tempfile, unittest
from pathlib import Path
from automation import transform, untransform, digest, index_tree, record_runs, open_db, classify, observe

SEQ=';46&&&#)?$_jduuhf/+3&&5_+8;&'
class Tests(unittest.TestCase):
    def test_exact_positions_and_inverse(self):
        data=bytes(range(200)); out=transform(data, SEQ)
        self.assertEqual([i for i in range(200) if data[i]!=out[i]], [3,49,95,141,187])
        self.assertEqual(out[3], ((3^59^5)+8)%256)
        self.assertEqual(untransform(out, SEQ),data)
    def test_bad_sequence(self):
        with self.assertRaises(ValueError): transform(b'abc',SEQ+'x')
    def test_sha256(self):
        self.assertEqual(digest(b'abc'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
    def test_index_actual_tree(self):
        tree={'truncated':False,'tree':[{'path':'README.md','type':'blob','mode':'100644'},{'path':'x.py','type':'blob','mode':'100644'},{'path':'link.py','type':'blob','mode':'120000'}]}
        self.assertEqual(index_tree(tree),['x.py'])
    def test_truncated_is_not_complete(self):
        with self.assertRaises(ValueError): index_tree({'truncated':True,'tree':[]})
    def test_dedup_and_retry(self):
        with tempfile.TemporaryDirectory() as d:
            db=open_db(Path(d)/'db'); r={'databaseId':5,'headSha':'abc','attempt':1,'status':'completed','conclusion':'failure','url':'https://github.com/example','workflowName':'CI'}
            record_runs(db,'a',[r]); record_runs(db,'a',[r]); self.assertEqual(db.execute('select count(*) from runs').fetchone()[0],1)
            record_runs(db,'a',[dict(r,attempt=2,conclusion='success')]); self.assertEqual(db.execute('select count(*) from runs').fetchone()[0],2)
    def test_unknown_is_not_green(self):
        self.assertEqual(classify([]),'no_runs_observed'); self.assertEqual(classify([{'status':'in_progress'}]),'pending'); self.assertEqual(classify([{'status':'completed','conclusion':'failure'}]),'failure_observed')
    def test_remote_error_is_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            db=open_db(Path(d)/'db')
            def broken(*args): raise RuntimeError('network')
            self.assertFalse(observe(db,'www-infinity4/A-',broken))
            self.assertEqual(db.execute('select state from checks').fetchone()[0],'unknown')
if __name__=='__main__': unittest.main()
