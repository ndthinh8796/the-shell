from string import ascii_uppercase

def find_vt(lst):
    for i in lst:
        if "-" in i:
            a = i.index("-")
            start = i[a - 1]
            end = i[a + 1]
            break
    return start, end

def handle(lst):
    a = []
    kq = []
    s, e = find_vt(lst)
    for x in ascii_uppercase:
        a.append(x.lower())
        a.append(x)
    for i in range(a.index(s), a.index(e)+1):
        kq.append(a[i])
    return kq


print(handle(['ls', '*[a-D].py']))
