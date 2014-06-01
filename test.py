import track_deploy
from track_deploy import TrackDeploySvc
import json
svc = TrackDeploySvc()

#data = { 'site' : 'ESAC', 'products' : {'IDT' : '16.0.0', 'FL': '15.0.0', 'MDB' : '1.2.3.4.5' } }
#f = open("deploy.json", 'w')
#json.dump(data, f, sort_keys=True, indent=4)

#f = open("deploy.json", 'r')
#data = json.load(f)
#print json.dumps(data, sort_keys=True, indent=4)

table = svc.on_product_table(None)
print table

print 'OK'
 #
