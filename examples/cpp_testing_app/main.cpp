#include <windows.h> //windows.h has to be before tlhelp32.h
#include <tlhelp32.h> //windows.h has to be before tlhelp32.h

#include <iostream>
#include <vector>
#include <unordered_map>
#include <limits>
#include <thread>
#include <chrono>
#include <functional>
#include <bitset>
#include <memory>
#include <iomanip>
#include <initializer_list>
#include <ctime>
#include <filesystem>
#include <shlobj.h>
#include <winerror.h>
#include "metastring.h"

using namespace std;
using namespace andrivet::ADVobfuscator;

struct player_entity {    
    string player_id = "UI1874s41Q6w5s4";
    int hp = 100;
    int team = 2;
    double velocity = 9.87;    
};

void memory_modification(void) {;
    auto player_list = { player_entity(), player_entity() };
    while (true) {;
        this_thread::sleep_for(chrono::seconds(1));
        for (auto& p : player_list) {;
            cout << "ID: " << p.player_id << ", HP: " << p.hp << ", velocity: " << p.velocity << endl;
        };
    };
}

void opcode_injection(void) {;
    /* 
    The bad_code_detection app detects this because it is allocated on stack.
    Normally, this code would be dynamically injected from another process to
    prevent such detection, and the scan would have to also cover executable
    memory pages (default Python is too slow to do this)
    */
    int bad_code[] = { 0x83ec8b55,0x565340ec,0x0c758b57,0x8b087d8b,
                       0x348d104d,0xcf3c8dce,0x6f0fd9f7,0x6f0fce04,
                       0x0f08ce4c,0x10ce546f,0xce5c6f0f,0x646f0f18,
                       0x6f0f20ce,0x0f28ce6c,0x30ce746f,0xce7c6f0f,
                       0x04e70f38,0x4ce70fcf,0xe70f08cf,0x0f10cf54,
                       0x18cf5ce7,0xcf64e70f,0x6ce70f20,0xe70f28cf,
                       0x0f30cf74,0x38cf7ce7,0x7508c183,0xf8ae0fad,
                       0x5e5f770f,0x5de58b5b,0xccccccc3 };
    int* src = new int[64];
    int* dst = new int[64];
    int* dst_mir = new int[64];

    for (int i = 0; i < 64; ++i) {;
        src[i] = i;
    };

    /*
    Basic memory allocation for executable pages, normally, this is easily detectable and would not be used.
    Usually a code cave would be used instead. 
    */
    void* address = VirtualAlloc(NULL, sizeof(bad_code), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    memcpy(address, bad_code, sizeof(bad_code));

    __asm {
        push        20h
        mov         eax, dword ptr[src]
        push        eax
        mov         ecx, dword ptr[dst]
        push        ecx
        mov         ecx, dword ptr[address]
        call        ecx
        add         esp, 0Ch
    };

    typedef void (*FASTCALL)(void* dst, void* src, int len);
    FASTCALL fastcall = (FASTCALL)address;
    fastcall(dst_mir, src, 64 / 2);

    for (int i = 0; i < 64; ++i) {;
        cout << dst_mir[i] << endl;
    };

    while (true) {;
        this_thread::sleep_for(chrono::seconds(60));
    };
}

int main(void) {;
    /* Credentials protected until decrypted */
    auto password_format = DEF_OBFUSCATED("email:password");
    auto secret_email = DEF_OBFUSCATED("ancinpet@fit.cvut.cz");
    auto secret_password = DEF_OBFUSCATED("q87W--S6Q9w7s7qS21w..8w");
    
    /* Credentials protected until decrypted */
    auto password_format_fail = DEF_OBFUSCATED("email:password");
    auto secret_email_fail = DEF_OBFUSCATED("ancinpet@cvut.cz");
    auto secret_password_fail = DEF_OBFUSCATED("m8Q9s5R1h4A7..9s--q8sV");
    
    /* 
    Credentials should be on heap now
    Realistically they will most likely end up on stack since this is compiled with O2
    and it will get SSO'd since it has <16?<32? chars
    */
    auto password_format_fail_mv = password_format_fail.decrypt();
    auto secret_email_fail_mv = secret_email_fail.decrypt();
    auto secret_password_fail_mv = secret_password_fail.decrypt();
    
    thread(memory_modification).detach();
    thread(opcode_injection).detach();

    while (true) {;
        this_thread::sleep_for(chrono::seconds(60));
        
        /*
        Not safe after this block runs (60 seconds)
        because it will be kept in buffer for speed
        */
        cout << "Safe credentials" << endl;
        cout << password_format.decrypt() << endl;
        cout << secret_email.decrypt() << endl;
        cout << secret_password.decrypt() << endl;

        /* Always in memory */
        cout << "Unsafe credentials" << endl;
        cout << password_format_fail_mv << endl;
        cout << secret_email_fail_mv << endl;
        cout << secret_password_fail_mv << endl;
    };
    
    exit(0);
    return 0;
}