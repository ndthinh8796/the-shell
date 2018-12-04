a = ['ls', '|', 'grep', 'b']
if any("|" in i for i in a):
    print("heheh")
