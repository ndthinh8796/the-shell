from string import ascii_uppercase

def chuoi(lst):
    for i in lst:
        if "-" in i:
            a = i.index("-")
            start = lst[a - 1]
            end = lst[a + 1]
            break
    print(start)
    print(end)
    # a = []
    # c = []
    # for x in ascii_uppercase:
    #     a.append(x.lower())
    #     a.append(x)
    # for i in a:
    #     if i != "D":
    #         c.append(i)
    #     else:
    #         c.append(i)
    #         break
    # print(c)

chuoi(['ls', '*[a-c].py'])
