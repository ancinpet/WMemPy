# pylint: disable=broad-except
"""Example of simple CSGO wallhack"""
import sys
import ctypes
from ctypes import wintypes
from wmempy.wmem_process import WinProc


def get_team_string(team_num):
    """
    Returns string from team number
    """
    if team_num == 1:
        return 'Spectator'
    if team_num == 2:
        return 'Terrorist'
    if team_num == 3:
        return 'Counter-Terrorist'
    return 'Unassigned'

def get_opposite_team(team_num):
    """
    Returns the opposite team number
    """
    if team_num == 2:
        return 3
    if team_num == 3:
        return 2
    return team_num

APP_NAME = 'csgo.exe'
csgo = WinProc(APP_NAME)
# Check what the app loads
csgo.print_modules()
# Get client.dll
client = [module for module in csgo.modules if module.get_name().lower() == 'client.dll'][0]
# Try scanning for local player pointer in CSGO memory
# (we know it is in client.dll so we can speed up the scan)
local_player_start = csgo.scanner.AOB_scan(client,
                     "8D 34 85 ? ? ? ? 89 15 ? ? ? ? 8B 41 08 8B 48 04 83 F9 FF") + 3
# We found the pointer in memory, read it so we can save it
local_player_offset_absolute = client.read_dtype(local_player_start, wintypes.DWORD()) + 4
# We want address relative to client.dll, not to whole csgo.exe process
local_player_offset = local_player_offset_absolute - client.base_address
print(f'The pointer to local player is located in {client.get_name()} at '
      f'address {hex(local_player_offset)}')
# We have address of pointer to local player, reading it lands us with pointer to local player aka
# address, where local_player really is at in csgo memory, this changes
# each time you reload map / die etc...
local_player_pointer = client.read_dtype(local_player_offset, wintypes.DWORD())
# If you reverse engineer the player structure of CSGO, we can find some
# cool values, such as team, health etc...
# Offsets can be found at https://github.com/frk1/hazedumper/blob/master/csgo.json
my_team = csgo.reader.dtype(local_player_pointer + 0xF4, ctypes.c_int())
my_health = csgo.reader.dtype(local_player_pointer + 0x100, ctypes.c_int())
print(f'My health is {my_health} and my team is {get_team_string(my_team)}')

print('Reversing the team number will make the game think we are on the enemy '
      'team and it will allow us to see enemies as if they were allies :)')
enemy_team_num = get_opposite_team(my_team)
# Due to how the Source engine works, we need to force our memory into the process
# That means keep writing it, until a call in the Source engine happens where the teams get updated
# After that, the new value will stay permanently until end of the game or next half
# The update happens during gametick, we just need to time into it (bruteforce)
for i in range(5000):
    csgo.writer.dtype(local_player_pointer + 0xF4, ctypes.c_int(enemy_team_num))

my_team = csgo.reader.dtype(local_player_pointer + 0xF4, ctypes.c_int())
my_health = csgo.reader.dtype(local_player_pointer + 0x100, ctypes.c_int())
print(f'My health is {my_health} and my team is {get_team_string(my_team)}')

# Result: https://imgur.com/a/vN1X3gL
