import urllib.request, json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

script = """**[Hook — curious, energetic]**

Socho, tumne WhatsApp par apne dost ko message bheja…  
"Kal milte hain!"

Lekin kya tumne kabhi socha hai, ye message uske phone tak pahunchta kaise hai?

**[Story begins]**

Sabse pehle, tumhara message tumhare phone se WhatsApp ke system tak jaata hai.

Lekin ek interesting baat hai…

Tumhara message end-to-end encrypted hota hai. Matlab, message ka content sirf sender aur receiver ke devices hi padh sakte hain.

Ab WhatsApp ka server message ko sahi destination tak pahunchane mein help karta hai.

Agar dost online hai, message uske device tak deliver ho jaata hai.

Aur agar offline hai? Toh encrypted message temporarily server par wait kar sakta hai, jab tak uska device available na ho.

**[Reveal — slightly dramatic]**

Aur bas, isi process mein networking, servers, encryption aur databases jaise concepts ka role samajh aata hai.

**[Ending]**

Agli baar WhatsApp par message bhejo, toh yaad rakhna… ek simple text ke peeche poora software system kaam kar raha hota hai!

Aise tech concepts simple stories mein samajhne ke liye follow karo **Code Ki Class!**"""

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/tts/generate',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'text': script,
        'speaker_id': 'aarav',
        'speed': 1.0
    }).encode('utf-8')
)
res = json.loads(urllib.request.urlopen(req).read())
print('Live Multi-Scene WhatsApp Reel Generation:')
print('Success:', res['success'])
print('Duration:', res['duration_seconds'], 'seconds')
print('Speaker:', res['speaker_name'])
print('Prompt Condition:', res['conditioning_prompt'])
print('MP3 URL:', res['mp3_url'])
