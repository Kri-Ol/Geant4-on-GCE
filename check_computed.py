# -*- coding: utf-8 -*-

with open("cases.txt", "rt+") as cases:
    with open("TTT", "rt+") as computed:
        inlines = cases.readlines()
        bslines = computed.readlines()

        for case in inlines:
            case = case.rstrip()
            s = case.split(" ")
            s = [q for q in s if q] # remove empty strings

            c = s[1]
            n = s[2]
            seed1 = s[4]
            seed2 = s[5]

            str = f"C{c}_{n}_1_({seed1},{seed2})"
            #print(str)

            found = False
            for base in bslines:
                if str in base:
                    found = True
                    break

            if not found:
                print(case)
