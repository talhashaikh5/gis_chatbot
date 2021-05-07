import MySQLdb

serv = MySQLdb.connect(host = "52.66.82.69", user = "root", passwd = "Hotspot#0")

c = serv.cursor()

print(c.execute("SHOW DATABASES"))