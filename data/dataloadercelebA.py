import torch
import torchvision.transforms as transforms
import torch.utils.data as data
import os
import pickle
import numpy as np
import nltk
from PIL import Image
import cv2
import linecache as lc
from skimage import io
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import re

class NormalizeImageDict(object):
    def __init__(self, image_keys, normalizeRange=True):
        self.image_keys = image_keys
        self.normalizeRange = normalizeRange
        #self.normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#        self.normalize = transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
	self.normalize = transforms.Compose([
					    transforms.ToPILImage(),
				 	    transforms.Scale((256, 256)),
					    transforms.ToTensor(),
					    transforms.Normalize( mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
					    ])
    def __call__(self, sample):
        for key in self.image_keys:
            # if self.normalizeRange:
                # sample[key] /= 255
            sample[key] = self.normalize(sample[key])
        return sample

def getlinenumber(imgfile):
    with open(imgfile) as lmfile:
        lineNum = sum(1 for _ in lmfile)
        return lineNum-1

class MyDataSet(data.Dataset):
    NumFileList = 0
    def __init__(self, filelist, transform=None):
        self.filelist = filelist
        self.transform = transform
        with open(filelist) as lmfile:
            self.NumFileList = sum(1 for _ in lmfile)
    def __len__(self):
        #return getlinenumber(self.filelist) # too slow
        return self.NumFileList # one time calc
    def __getitem__(self, idx):
        # print(idx)
        line = lc.getline(self.filelist, idx+1)
        line = ' '.join(line.split())
        line = line.rstrip('\n')
        file = line.split(' ')
        ImgName = file[0]
        attrName = file[1:]
        input = io.imread(ImgName)
        # print(ImgName)
        if input.ndim < 3:
            input = cv2.cvtColor(input, cv2.COLOR_GRAY2RGB)
        # inp = cv2.resize(input, (256, 256))
        inp = input
        attr = np.asarray(attrName, dtype = int)
        # attr[attr == -1] = 0
        # print(attr)
        # print(attr.shape)
        sample = {'image': inp, 'attributes': attr}
        if self.transform:
            sample = self.transform(sample)
        return sample


class ToTensorDict(object):
    #Convert ndarrays in sample to Tensors.
    def __call__(self, sample):
        # print(sample)
        image, attributes = sample['image'], sample['attributes']
        # swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W
        image = image.transpose((2, 0, 1))
        img = torch.from_numpy(image)
        attr =  torch.from_numpy(attributes)
        return {'image': img.float(), 'attributes': attr.float()}


"""
transformed_dataset = MyDataSet(filelist ='celebATrain',
                                transform=transforms.Compose([
                                    ToTensorDict(),
                                    NormalizeImageDict(['image'])
                                ]))
dataloader = data.DataLoader(transformed_dataset, batch_size=4, shuffle=True, num_workers=1)
for i_batch, sample_batched in enumerate(dataloader):
    print(i_batch, sample_batched['image'].size(), sample_batched['Attractive'].size())
    print(sample_batched['Attractive'])
    print(sample_batched['EyeGlasses'])
    if i_batch == 1:
        break

testdataset = MyDataSet("celebATrain")
for i in range(1, len(testdataset)):
    fig = plt.figure()
    sample = agedataset[i]
    print(i, sample['image'].shape)
    ax = fig.add_subplot(1,1,1)
    ax.imshow(sample['image'])
    plt.show()
"""
