import ctypes
from flexmock import flexmock
import numpy as np
import os
import pytest
import subprocess
from wmempy.wmem_scanner import ProcScanner
# Tests not covered here are covered by live memory tests


@pytest.mark.parametrize(
    ['pattern', 'base', 'separator'],
    [('A1 ? ? ? ? 33 D2 6A 00 6A 00 33 C9 89 B0', 16, ' '),
     ('A1,?,?,?,?,33,D2,6A,00,6A,00,33,C9,89,B0', 16, ','),
     ('A1:?:?:?:?:33:D2:6A:00:6A:00:33:C9:89:B0', 16, ':'),
     ('A1 * * * * 33 D2 6A 00 6A 00 33 C9 89 B0', 16, ' '),
     ('A1,*,*,*,*,33,D2,6A,00,6A,00,33,C9,89,B0', 16, ','),
     ('A1:*:*:*:*:33:D2:6A:00:6A:00:33:C9:89:B0', 16, ':'),
     ('161 ? ? ? ? 51 210 106 0 106 0 51 201 137 176', 10, ' '),
     ('161,?,?,?,?,51,210,106,0,106,0,51,201,137,176', 10, ','),
     ('161:?:?:?:?:51:210:106:0:106:0:51:201:137:176', 10, ':'),
     ('161 * * * * 51 210 106 0 106 0 51 201 137 176', 10, ' '),
     ('161,*,*,*,*,51,210,106,0,106,0,51,201,137,176', 10, ','),
     ('161:*:*:*:*:51:210:106:0:106:0:51:201:137:176', 10, ':')],
)
def test_winsys_proc_scanner_pattern_transform(pattern, base, separator):
    """Test that scanner can transform patterns"""
    scanner = ProcScanner(None)
    expected_result = np.array([161,-1,-1,-1,-1,51,210,106,0,106,0,51,201,137,176])
    arr = scanner.array_from_pattern(pattern, base, separator)
    assert (arr==expected_result).all()

def test_winsys_proc_scanner_ascii_transform():
    """Test that scanner can transform ascii"""
    scanner = ProcScanner(None)
    expected_result = np.array([97,98,99,100,69,70,71,72])
    arr = scanner.array_from_ascii('abcdEFGH')
    assert (arr==expected_result).all()

def test_winsys_proc_scanner_subsequence():
    """Test that scanner can look for subsequences"""
    scanner = ProcScanner(None)
    memory = np.array([161,22,25,29,90,51,210,106,0,106,0,51,201,137,176])
    pattern = np.array([161,-1,-1,-1,-1,51,210,106,0,106,0,51,201,137,176])
    result = scanner.is_subsequence(memory, pattern)
    assert result == 0
    # Check all sorts of different subsequences
    for i in range(1, 10):
        pattern = np.array([161,-1,-1,-1,-1,51,210,106,0,106,0,51,201,137,176])
        result = scanner.is_subsequence(memory, pattern[i:])
        assert result == i
    for i in range(2, 6):
        pattern = np.array([161,-1,-1,-1,-1,51,210,106,0,106,0,51,201,137,176])
        result = scanner.is_subsequence(memory, pattern[i:10])
        assert result == i
    for i in range(2, 6):
        pattern = np.array([161,-1,-1,-1,-1,51,210,106,0,106,0,51,201,137,176])
        result = scanner.is_subsequence(memory, pattern[5:i+5])
        assert result == 5
    # Subsequence is not in memory
    pattern = np.array([5,5,5,5,5])
    result = scanner.is_subsequence(memory, pattern)
    assert result is None
    pattern = np.array([210,106,0,106,0,5])
    result = scanner.is_subsequence(memory, pattern)
    assert result is None
    pattern = np.array([161,-1,88,-1,-1,51,210,106,0,106,0,51,201,137,176])
    result = scanner.is_subsequence(memory, pattern)
    assert result is None
