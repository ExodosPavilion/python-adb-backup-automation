from ppadb.client import Client as AdbClient
client = AdbClient(host="127.0.0.1", port=5037)
device = ( client.devices() )[0] 

phonePath = '/storage/8533-17ED/Neko/"MangaDex (EN)"/"Isekai Yakkyoku"/"Vol.3 Ch.13 - The Boy Without A Shadow and the Inquisition, Part 2 - 216965"/'

#print(device.shell( 'cd {} && ls'.format(phonePath) ) )

print(device.shell( 'ls' ) )
print(device.shell( 'cd storage && ls' ) )
print(device.shell( 'cd storage/8533-17ED && ls' ) )
print(device.shell( 'cd "storage/8533-17ED/Neko/MangaDex (EN)/Solo Login/Ch.40 - 1103950" && ls' ) )
#device.shell("screencap -p /sdcard/screen.png")
device.pull( ('/storage/8533-17ED/Neko/MangaDex (EN)/Even Though I_m a Former Noble and a Single Mother, My Daughters Are Too Cute and Working as an Adventurer Isn’t Too Much of a Hassle/Ch.6 - 913286/' + '001.jpg'), "screen.jpg")
