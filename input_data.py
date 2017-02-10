# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Functions for downloading and reading MNIST data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin

from tensorflow.contrib.learn.python.learn.datasets import base
from tensorflow.python.framework import dtypes

# SOURCE_URL = 'http://yann.lecun.com/exdb/mnist/'


def _read32(bytestream):
  dt = np.dtype(np.uint32).newbyteorder('>')
  return np.frombuffer(bytestream.read(4), dtype=dt)[0]


def extract_features(f):
  """Extract the images into a 4D uint8 numpy array [index, y, x, depth].
  Args:
    f: A file object that can be passed into a gzip reader.
  Returns:
    data: A 4D uint8 numpy array [index, y, x, depth].
  Raises:
    ValueError: If the bytestream does not start with 2051.
  """
  print('Extracting', f.name)
  data = np.load(f)
  return data


def dense_to_one_hot(labels_dense, num_classes):
  """Convert class labels from scalars to one-hot vectors."""
  num_labels = labels_dense.shape[0]
  index_offset = np.arange(num_labels) * num_classes
  labels_one_hot = np.zeros((num_labels, num_classes))
  labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
  return labels_one_hot


def extract_labels(f, one_hot=False, num_classes=10):
  """Extract the labels into a 1D uint8 np array [index].
  Args:
    f: A file object that can be passed into a gzip reader.
    one_hot: Does one hot encoding for the result.
    num_classes: Number of classes for the one hot encoding.
  Returns:
    labels: a 1D uint8 numpy array.
  Raises:
    ValueError: If the bystream doesn't start with 2049.
  """
  print('Extracting', f.name)
  labels = np.load(f)
  # with gzip.GzipFile(fileobj=f) as bytestream:
  #   magic = _read32(bytestream)
  #   if magic != 2049:
  #     raise ValueError('Invalid magic number %d in MNIST label file: %s' %
  #                      (magic, f.name))
  #   num_items = _read32(bytestream)
  #   buf = bytestream.read(num_items)
  #   labels = numpy.frombuffer(buf, dtype=numpy.uint8)
  if one_hot:
    return dense_to_one_hot(labels, num_classes)
  return labels


class DataSet(object):

  def __init__(self,
               features,
               labels,
               one_hot=False,
               dtype=dtypes.float32,
               reshape=True):
    """Construct a DataSet.
    `dtype` can be either
    `uint8` to leave the input as `[0, 255]`, or `float32` to rescale into
    `[0, 1]`.
    """
    dtype = dtypes.as_dtype(dtype).base_dtype
    if dtype not in (dtypes.uint8, dtypes.float32):
      raise TypeError('Invalid image dtype %r, expected uint8 or float32' %
                      dtype)

    assert features.shape[0] == labels.shape[0], (
        'images.shape: %s labels.shape: %s' % (features.shape, labels.shape))
    self._num_examples = features.shape[0]

    self._features = features
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0

  @property
  def features(self):
    return self._features

  @property
  def labels(self):
    return self._labels

  @property
  def num_examples(self):
    return self._num_examples

  @property
  def epochs_completed(self):
    return self._epochs_completed

  def next_batch(self, batch_size):
    """Return the next `batch_size` examples from this data set."""
    
    total = np.arange(self._num_examples)
    indices = np.random.choice(total, batch_size, replace = False)
    return self._features[indices], self._labels[indices]
    # return self._features[start:end], self._labels[start:end]


def read_data_sets(train_dir,
                   one_hot=False,
                   dtype=dtypes.float32,
                   reshape=True,
                   validation_size=10000,
                   runs = [1]):
  
  TRAIN_FEATURES = 'train'
  TRAIN_LABELS = 'train_labels'
  TEST_FEATURES = 'test'
  TEST_LABELS = 'test_labels'

  # Training
  train_features = None
  train_labels = None
  test_features = None
  test_labels = None
  for run in runs:
    run_prefix = 'run' + str(run) + '_' 
    local_file = os.path.join(train_dir, run_prefix + TRAIN_FEATURES)
    with open(local_file, 'rb') as f:
      if train_features is None:
        train_features = extract_features(f)
      else:
        print ('Train features shape', train_features.shape)
        train_features = np.concatenate((train_features, extract_features(f)))

    local_file = os.path.join(train_dir, run_prefix + TRAIN_LABELS)
    with open(local_file, 'rb') as f:
      if train_labels is None:
        train_labels = extract_labels(f, one_hot=one_hot)
      else:
        train_labels = np.concatenate((train_labels, extract_labels(f, one_hot=one_hot)))


    # Testing
    local_file = os.path.join(train_dir, run_prefix + TEST_FEATURES)
    with open(local_file, 'rb') as f:
      if test_features is None:
        test_features = extract_features(f)
      else:
        test_features = np.concatenate((test_features, extract_features(f)))

    
    local_file = os.path.join(train_dir, run_prefix + TEST_LABELS)
    with open(local_file, 'rb') as f:
      if test_labels is None:
        test_labels = extract_labels(f, one_hot=one_hot)
      else:
        test_labels = np.concatenate((test_labels, extract_labels(f, one_hot=one_hot)))

  # # We'll use the first 200k items to avoid using too much memory and train faster
  # train_features = train_features[:200000]
  # train_labels = train_labels[:200000]

  # test_features = test_features[:20000]
  # test_labels = test_labels[:20000]

  # Validation
  if not 0 <= validation_size <= len(train_features):
    raise ValueError(
        'Validation size should be between 0 and {}. Received: {}.'
        .format(len(train_images), validation_size))

  validation_features = train_features[:validation_size]
  validation_labels = train_labels[:validation_size]
  train_features = train_features[validation_size:]
  train_labels = train_labels[validation_size:]

  train = DataSet(train_features, train_labels, dtype=dtype, reshape=reshape)
  validation = DataSet(validation_features,
                       validation_labels,
                       dtype=dtype,
                       reshape=reshape)
  test = DataSet(test_features, test_labels, dtype=dtype, reshape=reshape)

  return base.Datasets(train=train, validation=validation, test=test)