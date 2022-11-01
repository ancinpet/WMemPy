#include <windows.h>
#include <tlhelp32.h>

#include <string>
#include <cstdlib>
#include <iostream>

using namespace std;

int main() {
	int good_code[] = { 0x83ec8b55, 0x565340ec, 0x0c758b57, 0x8b087d8b };
	while (true) {
		Sleep(1000);
		cout << "Hello world :)" << endl;
		for (auto x: good_code) {
			cout << x << endl;
		}
	}
}