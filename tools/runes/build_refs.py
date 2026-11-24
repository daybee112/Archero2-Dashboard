import json, os
from PIL import Image
from find_icon import find_icon
V1="/home/claude/runes/full/s_%03d.png"; V2="/home/claude/runes2/full/s_%03d.png"
refs=[
 (V1,2,"Sprite Multishot","enhancement"),(V1,4,"Sprite Link","enhancement"),(V1,6,"Sharp Arrow","enhancement"),(V1,8,"Flamenox Seal","enhancement"),
 (V1,10,"Melee Sprite","ability"),(V1,12,"Healing Sprite","ability"),(V1,14,"Arrow Rain","ability"),(V1,16,"Flamenox Touch","ability"),
 (V1,18,"Devil Pact","blessing"),(V1,20,"Lucky Shadow","blessing"),(V1,22,"Sprite Assist","etched"),(V1,24,"Sprite's Awe","etched"),
 (V1,26,"Elemental Crit","etched"),(V1,28,"Sawblade Circle","enhancement"),(V1,30,"Spin SPD Up","enhancement"),(V1,32,"Dragonflight Sword","enhancement"),
 (V1,34,"Ricochet Strike","enhancement"),(V1,36,"Giant Meteor","enhancement"),(V1,38,"Potion Magnet","enhancement"),(V1,40,"Frostshock Seal","enhancement"),
 (V1,42,"Rootguard","enhancement"),(V1,44,"Circle","ability"),(V1,46,"Ring of Agony","ability"),(V1,48,"Sword of Time","ability"),
 (V1,50,"Strike Potion","ability"),(V1,52,"Star of Time","ability"),(V1,54,"Star of Fury","ability"),(V1,56,"Frostshock Touch","ability"),
 (V1,58,"Vine Bind","enhancement"),(V1,60,"Circle","ability"),(V1,62,"Plant Summon","ability"),(V1,64,"Equinox Bloom","ability"),
 (V2,2,"Guardian","blessing"),(V2,4,"Rabbit's Foot","blessing"),(V2,6,"Resilience","blessing"),(V2,8,"Intelligence","blessing"),
 (V2,10,"Rabbit's Foot","blessing"),(V2,12,"Lucky Shadow","blessing"),(V2,14,"Revive","blessing"),(V2,16,"Arrow of Echoes","etched"),
 (V2,18,"Pulsing Orb","etched"),(V2,20,"Elemental Domain","etched"),(V2,22,"Life Surge","etched"),(V2,24,"Plant Crit","etched"),
 (V2,27,"Sword Strike Split","etched"),(V2,29,"Swordstrike Aerie","etched"),
]
os.makedirs("ref",exist_ok=True); out=[]
for k,(V,i,name,typ) in enumerate(refs):
    p=V%i; box=find_icon(p); top=box[1]; cx,cy=590,top+150
    im=Image.open(p).convert("RGB").crop((cx-115,cy-115,cx+115,cy+115))
    fn=f"ref/{k:02d}_{name.replace(' ','_').replace(chr(39),'')}.png"; im.save(fn)
    out.append({"file":fn,"name":name,"type":typ,"src":p})
json.dump(out,open("refs.json","w"),indent=1)
from PIL import ImageDraw
W=115; cols=10; rows=(len(out)+cols-1)//cols
sh=Image.new("RGB",(cols*W,rows*(W+14)),"white"); d=ImageDraw.Draw(sh)
for k,r in enumerate(out):
    sh.paste(Image.open(r["file"]).resize((W,W)),((k%cols)*W,(k//cols)*(W+14))); d.text(((k%cols)*W+2,(k//cols)*(W+14)+W),r["name"][:18],fill="black")
sh.save("refsheet.png"); print(len(out))
