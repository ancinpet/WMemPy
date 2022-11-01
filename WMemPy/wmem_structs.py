# pylint: disable=wildcard-import,too-few-public-methods,unused-wildcard-import,invalid-name
"""Structures defined by Microsoft (WinApi standart)"""
import ctypes
from ctypes.wintypes import *


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    """https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-memory_basic_information"""
    _fields_ = (('BaseAddress', LPVOID),
                ('AllocationBase', LPVOID),
                ('AllocationProtect', DWORD),
                ('RegionSize', ctypes.c_size_t),
                ('State', DWORD),
                ('Protect', DWORD),
                ('Type', DWORD))


class MODULEINFO(ctypes.Structure):
    """https://docs.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-moduleinfo"""
    _fields_ = (("lpBaseOfDll", LPVOID),
                ("SizeOfImage", DWORD),
                ("EntryPoint", LPVOID))
