"""Return random movie quote string
 src: http://www.afi.com/100Years/quotes.aspx
"""
from random import randint

QUOTE_LIST = """
1|Frankly, my dear, I don't give a damn.|GONE WITH THE WIND|1939
2|I'm gonna make him an offer he can't refuse.|THE GODFATHER|1972
3|You don't understand! I coulda had class. I coulda been a contender. I could've been somebody, instead of a bum, which is what I am.|ON THE WATERFRONT|1954
4|Toto, I've a feeling we're not in Kansas anymore.|THE WIZARD OF OZ|1939
5|Here's looking at you, kid.|CASABLANCA|1942
6|Go ahead, make my day.|SUDDEN IMPACT|1983
7|All right, Mr. DeMille, I'm ready for my close-up.|SUNSET BLVD.|1950
8|May the Force be with you.|STAR WARS|1977
9|Fasten your seatbelts. It's going to be a bumpy night.|ALL ABOUT EVE|1950
10|You talking to me?|TAXI DRIVER|1976
11|What we've got here is failure to communicate.|COOL HAND LUKE|1967
12|I love the smell of napalm in the morning. |APOCALYPSE NOW|1979
13|Love means never having to say you're sorry.|LOVE STORY|1970
14|The stuff that dreams are made of.|THE MALTESE FALCON|1941
15|E.T. phone home.|E.T. THE EXTRA-TERRESTRIAL|1982
16|They call me Mister Tibbs!|IN THE HEAT OF THE NIGHT|1967
17|Rosebud.|CITIZEN KANE|1941
18|Made it, Ma! Top of the world!|WHITE HEAT|1949
19|I'm as mad as hell, and I'm not going to take this anymore!|NETWORK|1976
20|Louis, I think this is the beginning of a beautiful friendship.|CASABLANCA|1942
21|A census taker once tried to test me. I ate his liver with some fava beans and a nice Chianti.|THE SILENCE OF THE LAMBS|1991
22|Bond. James Bond.|DR. NO|1962
23|There's no place like home. |THE WIZARD OF OZ|1939
24|I am big! It's the pictures that got small.|SUNSET BLVD.|1950
25|Show me the money!|JERRY MAGUIRE|1996
26|Why don't you come up sometime and see me?|SHE DONE HIM WRONG|1933
27|I'm walking here! I'm walking here!|MIDNIGHT COWBOY|1969
28|Play it, Sam. Play 'As Time Goes By.'|CASABLANCA|1942
29|You can't handle the truth!|A FEW GOOD MEN|1992
30|I want to be alone.|GRAND HOTEL|1932
31|After all, tomorrow is another day!|GONE WITH THE WIND|1939
32|Round up the usual suspects.|CASABLANCA|1942
33|I'll have what she's having.|WHEN HARRY MET SALLY|1989
34|You know how to whistle, don't you, Steve? You just put your lips together and blow.|TO HAVE AND HAVE NOT|1944
35|You're gonna need a bigger boat.|JAWS|1975
36|Badges? We ain't got no badges! We don't need no badges! I don't have to show you any stinking badges!|THE TREASURE OF THE SIERRA MADRE|1948
37|I'll be back.|THE TERMINATOR|1984
38|Today, I consider myself the luckiest man on the face of the earth.|THE PRIDE OF THE YANKEES|1942
39|If you build it, he will come.|FIELD OF DREAMS|1989
40|My mama always said life was like a box of chocolates. You never know what you're gonna get.|FORREST GUMP|1994
41|We rob banks.|BONNIE AND CLYDE|1967
42|Plastics.|THE GRADUATE|1967
43|We'll always have Paris.|CASABLANCA|1942
44|I see dead people.|THE SIXTH SENSE|1999
45|Stella! Hey, Stella!|A STREETCAR NAMED DESIRE|1951
46|Oh, Jerry, don't let's ask for the moon. We have the stars.|NOW, VOYAGER|1942
47|Shane. Shane. Come back!|SHANE|1953
48|Well, nobody's perfect.|SOME LIKE IT HOT|1959
49|It's alive! It's alive!|FRANKENSTEIN|1931
50|Houston, we have a problem.|APOLLO 13|1995
51|You've got to ask yourself one question: 'Do I feel lucky?' Well, do ya, punk?|DIRTY HARRY|1971
52|You had me at "hello."|JERRY MAGUIRE|1996
53|One morning I shot an elephant in my pajamas. How he got in my pajamas, I don't know.|ANIMAL CRACKERS|1930
54|There's no crying in baseball!|A LEAGUE OF THEIR OWN|1992
55|La-dee-da, la-dee-da.|ANNIE HALL|1977
56|A boy's best friend is his mother.|PSYCHO|1960
57|Greed, for lack of a better word, is good.|WALL STREET|1987
58|Keep your friends close, but your enemies closer.|THE GODFATHER II|1974
59|As God is my witness, I'll never be hungry again.|GONE WITH THE WIND|1939
60|Well, here's another nice mess you've gotten me into!|SONS OF THE DESERT|1933
61|Say "hello" to my little friend!|SCARFACE|1983
62|What a dump.|BEYOND THE FOREST|1949
63|Mrs. Robinson, you're trying to seduce me. Aren't you?|THE GRADUATE|1967
64|Gentlemen, you can't fight in here! This is the War Room!|DR. STRANGELOVE|1964
65|Elementary, my dear Watson.|THE ADVENTURES OF SHERLOCK HOLMES|1939
66|Take your stinking paws off me, you damned dirty ape.|PLANET OF THE APES|1968
67|Of all the gin joints in all the towns in all the world, she walks into mine.|CASABLANCA|1942
68|Here's Johnny!|THE SHINING|1980
69|They're here!|POLTERGEIST|1982
70|Is it safe?|MARATHON MAN|1976
71|Wait a minute, wait a minute. You ain't heard nothin' yet!|THE JAZZ SINGER|1927
72|No wire hangers, ever!|MOMMIE DEAREST|1981
73|Mother of mercy, is this the end of Rico?|LITTLE CAESAR|1930
74|Forget it, Jake, it's Chinatown.|CHINATOWN|1974
75|I have always depended on the kindness of strangers.|A STREETCAR NAMED DESIRE|1951
76|Hasta la vista, baby.|TERMINATOR 2: JUDGMENT DAY|1991
77|Soylent Green is people!|SOYLENT GREEN|1973
78|Open the pod bay doors, please, HAL.|2001: A SPACE ODYSSEY|1968
79|Striker: Surely you can't be serious.|AIRPLANE!|1980
|Rumack: I am serious...and don't call me Shirley.||
80|Yo, Adrian!|ROCKY|1976
81|Hello, gorgeous.|FUNNY GIRL|1968
82|Toga! Toga!|LAMPOON'S ANIMAL HOUSE|1978
83|Listen to them. Children of the night. What music they make.|DRACULA|1931
84|Oh, no, it wasn't the airplanes. It was Beauty killed the Beast.|KING KONG|1933
85|My precious.|THE LORD OF THE RINGS: TWO TOWERS|2002
86|Attica! Attica!|DOG DAY AFTERNOON|1975
87|Sawyer, you're going out a youngster, but you've got to come back a star!|42ND STREET|1933
88|Listen to me, mister. You're my knight in shining armor. Don't you forget it. You're going to get back on that horse, and I'm going to be right behind you, holding on tight, and away we're gonna go, go, go!|ON GOLDEN POND|1981
89|Tell 'em to go out there with all they got and win just one for the Gipper.|KNUTE ROCKNE ALL AMERICAN|1940
90|A martini. Shaken, not stirred.|GOLDFINGER|1964
91|Who's on first.|THE NAUGHTY NINETIES|1945
92|Cinderella story. Outta nowhere. A former greenskeeper, now, about to become the Masters champion. It looks like a mirac...It's in the hole! It's in the hole! It's in the hole!|CADDYSHACK|1980
93|Life is a banquet, and most poor suckers are starving to death!|AUNTIE MAME|1958
94|I feel the need - the need for speed!|TOP GUN|1986
95|Carpe diem. Seize the day, boys. Make your lives extraordinary.|DEAD POETS SOCIETY|1989
96|Snap out of it!|MOONSTRUCK|1987
97|My mother thanks you. My father thanks you. My sister thanks you. And I thank you.|YANKEE DOODLE DANDY|1942
98|Nobody puts Baby in a corner.|DIRTY DANCING|1987
99|I'll get you, my pretty, and your little dog, too!|WIZARD OF OZ, THE|1939
100|I'm the king of the world!|TITANIC|1997"""

QUOTE_LIST = [x.strip() for x in QUOTE_LIST.split('\n') if len(x.strip()) > 0]

def get_random_quote():

    random_index = randint(0, len(QUOTE_LIST) - 1)

    qline = QUOTE_LIST[random_index]

    num, quote, movie, year = qline.split('|')

    return """<p>"{0}"</p><br />- from {1}, {2}""".format(\
                quote, movie, year)
