anystr = 'asdfasdf/asdfasdf/asdfasdfasdfasdf/asdfasdf/asdfsadf.jpg'
splitlist = anystr.split('/')
print(splitlist)
print('/'.join(splitlist[:-1]))
print(splitlist[-1])