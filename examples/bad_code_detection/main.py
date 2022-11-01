# pylint: disable=broad-except
"""Example of simple malicious code detection"""
import sys
import random
import time
from wmempy.wmem_process import WinProc

# Bad code:
# 0x83ec8b55,0x565340ec,0x0c758b57,0x8b087d8b,
# 0x348d104d,0xcf3c8dce,0x6f0fd9f7,0x6f0fce04,
# 0x0f08ce4c,0x10ce546f,0xce5c6f0f,0x646f0f18,
# 0x6f0f20ce,0x0f28ce6c,0x30ce746f,0xce7c6f0f,
# 0x04e70f38,0x4ce70fcf,0xe70f08cf,0x0f10cf54,
# 0x18cf5ce7,0xcf64e70f,0x6ce70f20,0xe70f28cf,
# 0x0f30cf74,0x38cf7ce7,0x7508c183,0xf8ae0fad,
# 0x5e5f770f,0x5de58b5b,0xccccccc3

# Application list that we will be scanning
potential_threats = ['WMemPy_test_app.exe', 'WMemPy_test_app_poly.exe',
                     'csrss.exe', 'dwm.exe', 'WMemPy_hello_app.exe']
# Memory patterns extracted from bad code
bad_code_patterns = ['55 8b ec 83 ec 40 53 56 57 8b 75 0c 8b 7d 08 8b',
                     '4d 10 8d 34 ce 8d 3c cf f7 d9 0f 6f 04 ce 0f 6f',
                     '4c ce 08 0f 6f 54 ce 10 0f 6f 5c ce 18 0f 6f 64',
                     'ce 20 0f 6f 6c ce 28 0f 6f 74 ce 30 0f 6f 7c ce',
                     '38 0f e7 04 cf 0f e7 4c cf 08 0f e7 54 cf 10 0f',
                     'e7 5c cf 18 0f e7 64 cf 20 0f e7 6c cf 28 0f e7',
                     '74 cf 30 0f e7 7c cf 38 83 c1 08 75 ad 0f ae f8']


# The checks are running constantly
while True:
    print('Starting check for bad code.')
    # Check every app
    for app in potential_threats:
        print(f'App: {app}')
        matches = []
        try:
            proc = WinProc(app)
        except Exception:
            continue
        # Normally the scan would be more extensive (for example also across all pages)
        # but Python is too slow for this
        main_entry = [module for module in proc.modules if module.get_name().lower() == app.lower()]
        # Check in different order each time to make scan time more consistent
        random.shuffle(bad_code_patterns)
        for code in bad_code_patterns:
            # Scan each code against the stack, if we find bad code, add it to results
            result = proc.scanner.AOB_scan_arr(main_entry, code)
            if not result[0] is None:
                matches.append([result, code])
        # 4/7 ths is enough to trigger detection
        if len(matches) >= 4:
            print(f'Detected application with bad code: {proc.proc_name} ('
                  f'{len(matches)}/{len(bad_code_patterns)} matches)')
            print('Matches:')
            print('-------------------')
            for match in matches:
                print(f'Address: {hex(match[0][1].base_address + match[0][0])}, code: {match[1]}')
            print('-------------------')
        # If there is at least 1 match, mark as suspicious
        elif len(matches) >= 1:
            print(f'Application {proc.proc_name} is suspicious, but only has a few '
                  f'matches ({len(matches)}/{len(bad_code_patterns)} matches)')
            print('Matches:')
            print('-------------------')
            for match in matches:
                print(f'Address: {hex(match[0][1].base_address + match[0][0])}, code: {match[1]}')
            print('-------------------')
    # Give up CPU for others, there is no reason to constantly check against the same thing
    print('')
    time.sleep(20)
