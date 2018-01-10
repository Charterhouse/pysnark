/**
 * Copyright (c) 2016-2018 Koninklijke Philips N.V. All rights reserved. A
 * copyright license for redistribution and use in source and binary forms,
 * with or without modification, is hereby granted for non-commercial,
 * experimental and research purposes, provided that the following conditions
 * are met:
 * - Redistributions of source code must retain the above copyright notice,
 *   this list of conditions and the following disclaimers.
 * - Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimers in the
 *   documentation and/or other materials provided with the distribution. If
 *   you wish to use this software commercially, kindly contact
 *   info.licensing@philips.com to obtain a commercial license.
 *
 * This license extends only to copyright and does not include or grant any
 * patent license or other license whatsoever.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdlib.h>
#include <stdio.h>
#include "../../pysnark/lib/gghkey.txt"

const char* key = GGH_KEY;
int curpos = 0;

#define HEXTOINT(val) ((val)>='A'?(val)-'A'+10:(val)-'0')

void hashreset() {
    curpos = 0;
}

int hashnextval() {
    int val1 = HEXTOINT(key[curpos]); curpos++;
    int val2 = HEXTOINT(key[curpos]); curpos++;
    int val3 = HEXTOINT(key[curpos]); curpos++;
    int val4 = HEXTOINT(key[curpos]); curpos++;
    int val5 = HEXTOINT(key[curpos]); curpos++;
    if (val1 < 0 || val1 > 15) printf("Error at %d[1]\n", curpos);
    if (val2 < 0 || val2 > 15) printf("Error at %d[2]\n", curpos);
    if (val3 < 0 || val3 > 15) printf("Error at %d[3]\n", curpos);
    if (val4 < 0 || val4 > 15) printf("Error at %d[4]\n", curpos);
    if (val5 < 0 || val5 > 15) printf("Error at %d[5]\n", curpos);
    return (val1<<16)+(val2<<12)+(val3<<8)+(val4<<4)+val5;
}

int main(int argc, char** argv) {
    
    int skipbytes = 0;
    
    // option to skip (to continue hashing from previous execution)
    if (argc==2) {
        int skip = atoi(argv[1]);
        int skipblocks = 1824*(skip/304);
        skipbytes = skip-(skip/304)*304;
        for (int i = 0; i < skipblocks; i++) getchar();
    }
    
    // hash data as it comes in
    int stop = 0;
    
    while (!stop) {
        // read next blob
        int plain[7296], i;
        for (i = 0; i < 1824; i++) {
            int ch;
_readnext:
            ch = getchar();
            if (ch == EOF) {
                stop = 1;
                for (int j = i*4; j<7296; j++) plain[j] = 0;
                break;
            }
            if (ch == '\n' || ch=='\r' || ch==' ') goto _readnext;
            int val = HEXTOINT(ch);
            plain[i*4]   = val&8?1:0;
            plain[i*4+1] = val&4?1:0;
            plain[i*4+2] = val&2?1:0;
            plain[i*4+3] = val&1?1:0;
        }
        if (i==0) break;
        
        // hash
        hashreset();
        int hashedbits[1216];
        for (int i = 0; i < 64; i++) {
            unsigned int val = 0;
            for (int j = 0; j < 7296; j++) {
                int hv = hashnextval();
                val += hv * plain[j];
            }
            for (int j = 0; j < 19; j++)
                hashedbits[i*19+j] = val&(1<<(18-j));
        }
        for (int i = 0; i < 304; i++) {
            int val = (hashedbits[i*4]?8:0)+(hashedbits[i*4+1]?4:0)+(hashedbits[i*4+2]?2:0)+(hashedbits[i*4+3]?1:0);
            if (skipbytes)
                skipbytes--;
            else
                putchar(val>=10?val-10+'A':val+'0');
        }
    }
    
    putchar('\n');
}