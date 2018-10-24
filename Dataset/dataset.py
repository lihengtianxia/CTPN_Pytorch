import torch
from torch.utils.data import Dataset
import lmdb
import six
from PIL import Image


class LmdbDataset(Dataset):
    def __init__(self, root, transformer=None):
        self.env = lmdb.open(root, max_readers=1, readonly=True, lock=False, readahead=False, meminit=False)
        if not self.env:
            print("Cannot create lmdb from root {0}.".format(root))
        with self.env.begin(write=False) as e:
            self.data_num = int(e.get('num'))
        self.transformer = transformer

    def __len__(self):
        return self.data_num

    def __getitem__(self, index):
        assert index <= len(self), 'Index out of range.'
        index += 1
        with self.env.begin(write=False) as e:
            img_key = 'image-%09d' % index
            img_buf = e.get(img_key)
            buf = six.BytesIO()
            buf.write(img_buf)
            buf.seek(0)
            try:
                img = Image.open(buf).convert('RGB')
            except IOError:
                print('Corrupted image for {0}'.format(index))
                return self[index + 1]
            gt_key = 'gt-%09d' % index
            gt = str(e.get(gt_key))
        return img, gt
