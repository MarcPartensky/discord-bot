from config.config import access, status, delete_after_time, wolfram, prefix
from utils.date import days, months
from utils import tools
from utils import html_parser
from libs.google import google

from discord.ext import commands, tasks
from translate import Translator
from bs4 import BeautifulSoup
import wikipedia; wikipedia.set_lang("fr")
import html2text
import argparse
import requests
import datetime
import discord
import random
import aiohttp
import urllib
import urllib.parse
import html
import json
import re


class Web(commands.Cog):
    def __init__(self, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.joke_color = discord.Color.magenta()
        # self.to_language = "fr"
        # self.from_language = "en"
        # self.translator = Translator(to_lang=to_language, from_lang=from_language)

    @commands.command(name='bot', aliases=[prefix])
    async def french_bot(self, ctx:commands.Context, *, msg:str):
        """Parle français avec un bot."""
        translator = Translator(from_lang='fr', to_lang='en')
        msg = translator.translate(msg)
        msg = html.unescape(msg)
        url = "https://acobot-brainshop-ai-v1.p.rapidapi.com/get"
        querystring = {
            "bid":"49023",
            "key":"2UeOjV0fHoFtn6i2",
            "uid":"Mazex",
            "msg":msg}
        headers = {
            'x-rapidapi-host': "acobot-brainshop-ai-v1.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        msg = response.json()['cnt']
        translator = Translator(from_lang='en', to_lang='fr')
        msg = translator.translate(msg)
        msg = html.unescape(msg)
        await ctx.send(msg)

    @commands.command(name="bot-en", aliases=[prefix*2])
    async def  english_bot(self, ctx:commands.Context, *, msg:str):
        """Parle anglais avec un bot."""
        url = "https://acobot-brainshop-ai-v1.p.rapidapi.com/get"
        querystring = {
            "bid":"49023",
            "key":"2UeOjV0fHoFtn6i2",
            "uid":"Mazex",
            "msg":msg}
        headers = {
            'x-rapidapi-host': "acobot-brainshop-ai-v1.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        await ctx.send(response.json()['cnt'])

    @commands.command(name='bot-dumb', aliases=['idiot'])
    async def french_dumb_bot(self, ctx:commands.Context, msg:str):
        """Parle français avec un bot idiot."""
        translator = Translator(from_lang='fr', to_lang='en')
        msg = translator.translate(msg)
        msg = html.unescape(msg)
        url = "https://robomatic-ai.p.rapidapi.com/api.php"
        payload = f"ChatSource=RapidAPI&SessionID=RapidAPI1&in={msg}&op=in&cbid=1&cbot=1&key=RHMN5hnQ4wTYZBGCF3dfxzypt68rVP"
        headers = {
            'x-rapidapi-host': "robomatic-ai.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7",
            'content-type': "application/x-www-form-urlencoded"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        translator = Translator(from_lang='en', to_lang='fr')
        msg = translator.translate(msg)
        msg = html.unescape(msg)
        await ctx.send(response.json()['out'])

    @commands.command(name='bot-dumb-en', aliases=['idiot-anglais'])
    async def english_dumb_bot(self, ctx:commands.Context, msg:str):
        """Parle anglais avec un bot idiot."""
        url = "https://robomatic-ai.p.rapidapi.com/api.php"
        payload = f"ChatSource=RapidAPI&SessionID=RapidAPI1&in={msg}&op=in&cbid=1&cbot=1&key=RHMN5hnQ4wTYZBGCF3dfxzypt68rVP"
        headers = {
            'x-rapidapi-host': "robomatic-ai.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7",
            'content-type': "application/x-www-form-urlencoded"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        await ctx.send(response.json()['out'])

    @commands.command(name="google-trad", aliases=['google-traduction'])
    async def google_translate(self, ctx:commands.Context, source:str, target:str, *, msg:str):
        """Traduit avec google traduction."""
        url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
        data = {
            'source': source,
            'q': msg,
            'target': target,
        }
        headers = {
            'x-rapidapi-host': "google-translate1.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7",
            'accept-encoding': "application/gzip",
            'content-type': "application/x-www-form-urlencoded"
            }
        response = requests.request("POST", url, data=data, headers=headers)
        text = '\n'.join([html.unescape(tr['translatedText']) for tr in response.json()['data']['translations']])
        await ctx.send(text)

    @commands.command(name="traduit", aliases=['t', 'trad'])
    async def translate(self, ctx:commands.Context, languages:str, *, message:str):
        """Traduit un message."""
        try:
            if '/'in languages:
                from_lang, to_lang = languages.split('/')
                if len(to_lang)!=2 or len(from_lang)!=2:
                    raise Exception("Ce n'est pas un langage du code ISO.")
                translator = Translator(to_lang=to_lang, from_lang=from_lang)
            else:
                to_lang = languages
                if len(to_lang)!=2:
                    raise Exception("Ce n'est pas un langage du code ISO.")
                translator = Translator(to_lang=to_lang)
            translation = translator.translate(message)
            translation = html.unescape(translation)
            await ctx.send(translation)
        except Exception as e:
            msg = str(e)
            msg += ("\nVous devez tapez: '.traduit [langue iso] [message]'. Il y a 2 options:"
                    "\n1) .traduit `fr` without the origin language => sans le langage d'origine."
                    "\n2) .traduit `en/fr` with the origin language => avec le langage d'origine."
                    "\n\nRegarder ce lien pour connaître le code iso en 2 lettres d'une langue."
                    "\nhttps://en.wikipedia.org/wiki/ISO_639-1")
            await ctx.send(msg)

    @commands.command(name="télécharger", aliases=['download', 'dl', 'tl'])
    async def download(self, ctx:commands.Context, *, url:str):
        """Télécharge une musique ytb avec un lien."""
        pattern = re.compile(r"https://www.youtu.?be.com/watch\?v=(\w{11})")
        results = pattern.findall(url)
        if len(results)==0:
            msg = "Ce n'est pas un url de vidéo youtube."
            return await ctx.send(msg)
        id = results[0]
        if not id:
            msg = "Ce n'est pas un url de vidéo youtube."
        else:
            msg = "https://youtube-downloader-of-marc.herokuapp.com/download?id="+id
        return await ctx.send(msg)

    @commands.command(name="chuck-norris", aliases=['chuck', 'norris'])
    async def chuck_norris(self, ctx:commands.Context):
        """API sur chuck norris."""
        params = dict(type='txt', nb=1, page=random.randint(0, 100))
        params = ";".join([f"{k}:{v}" for k,v in params.items()])
        url = "https://www.chucknorrisfacts.fr/api/get?data="
        res = requests.get(url=url+params)
        msg = html.unescape(res.json()[0]['fact'])
        await ctx.send(msg)

    @commands.command(name="chat")
    async def cat(self, ctx:commands.Context):
        """Affiche une image de chat."""
        res = requests.get('http://aws.random.cat/meow').json()
        embed = discord.Embed()
        embed.set_image(url=res['file'])
        await ctx.send(embed=embed)

    @commands.command(name="fausse-personne", aliases=['fake-person', 'dude', 'guy', 'someone', 'thispersondoesnotexist'])
    async def fake_person(self, ctx:commands.Context):
        """Affiche une fausse personne."""
        r = requests.get('https://thispersondoesnotexist.com/')
        print(r.text)
        raise NotImplementedError

    @commands.command(name="blague", aliases=['joke', 'j'])
    async def joke(self, ctx:commands.Context):
        """Fais un blague."""
        url = "https://joke3.p.rapidapi.com/v1/joke"
        headers = {
            'x-rapidapi-host': "joke3.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7"
            }
        r = requests.request("GET", url, headers=headers).json()
        translator = Translator(from_lang='en', to_lang='fr')
        content = html.unescape(translator.translate(r['content']))
        embed = (discord.Embed(title=content, color=self.joke_color)
        .add_field(name="original", value=r['content'])
        .add_field(name="likes", value=r['upvotes'])
        .add_field(name="dislikes", value=r['downvotes']))
        await ctx.send(embed=embed)

        # like and dislike support
        # await self.bot.add_reaction(emoji=emoji.like)
        # await self.bot.add_reaction(emoji=emoji.like)


        # await ctx.bot.
        # payload = ""
        # headers = {
        #     'x-rapidapi-host': "joke3.p.rapidapi.com",
        #     'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7",
        #     'content-type': "application/x-www-form-urlencoded"
        #     }

        # response = requests.request("POST", url, data=payload, headers=headers)

    @commands.command(name="math", aliases=['maths', 'mathématiques', 'm', 'wolfram', 'wolfram-alpha'])
    async def math(self, ctx:commands.Context, *, msg:str):
        """Calcule avec wolfram alpha."""
        res = wolfram.query(msg)
        for k,v in tools.keep(res, ['@src', 'plaintext']):
            if k == '@src':
                embed = discord.Embed(title=msg, color=discord.Color.orange())
                embed.set_image(url=v)
            elif k == 'plaintext':
                embed.title = v
                await ctx.send(embed=embed)

    @commands.command(name="wikipedia", aliases=['wiki'])
    async def wikipedia(self, ctx:commands.Context, *, search:str):
        """Fais une recherche sur wikipedia."""
        result = wikipedia.page(search)
        ctn = result.content.replace('\n', '')
        await ctx.send(ctn[:2000])

    @commands.command(name="langue-wiki", aliases=['lwiki'])
    async def set_wikipedia_language(self, ctx:commands.Context, *, lang:str):
        """Fais une recherche sur wikipedia."""
        wikipedia.set_lang(lang)
        msg = f"Wikipedia est en {lang} maintenant."
        await ctx.send(msg)

    @commands.command()
    async def google_search(self, ctx:commands.Context, *,msg:str, n=1):
        """Fais une recherche sur google."""
        parser = argparse.ArgumentParser()
        parser.add_argument('search', type=str, nargs='+', help='your google search')
        parser.add_argument('-n', type=int, help='number of search', default=n)
        try:
            parsed = parser.parse_args(msg.split(' '))
        except SystemExit as e:
            with tools.Capturing() as out:
                parser.print_help()
            msg = "**Erreur d'utilisation:**\n> "
            msg += '\n> '.join(out)
            return await ctx.send(msg)
        n = parsed.n or n
        search = ' '.join(parsed.search)
        results = google.search(search)[:n]
        for result in results:
            embed = self.embed_google_result(result)
            await ctx.send(embed=embed)

    @commands.command()
    async def google(self, ctx:commands.Context, *, search):
        """Fais une recherche sur google à ta place."""
        search = urllib.parse.quote(search)
        url = f"http://letmegooglethat.com/?q={search}"
        await ctx.send(url)

    def embed_google_result(self, result):
        """Crée une intégration pour le résultat de la recherche google."""
        embed = (discord.Embed(title=result.name, color=discord.Color.blue())
        .add_field(name='link', value=result.link)
        .add_field(name='name', value=result.name)
        .add_field(name='description', value=result.description))
        return embed

    @commands.command()
    async def web(self, ctx:commands.Context, url:str):
        """Consulte une page web avec l'url."""
        r = requests.get(url)
        h = html2text.HTML2Text()
        text = h.handle(r.text)
        await ctx.send(text[:2000])

    @commands.command()
    async def deepai(self, ctx:commands.Context, *, msg:str):
        """Envoie des requêtes à api.deepai.org."""
        r = requests.post(
            "https://api.deepai.org/api/text-generator",
            data={'text': msg},
            headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
        )
        resp = r.json()
        await ctx.send(str(resp['output'])[:2000])

    @commands.command()
    async def bitcoin(self, ctx:commands.Context):
        """Donne la valeur du bitcoin en dollar."""
        url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        async with aiohttp.ClientSession() as session:  # Async HTTP request
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            await ctx.send("Le prix du bitcoin est: $" + response['bpi']['USD']['rate'])

    @commands.command()
    async def meme(self, ctx):
        """Envoie un meme."""
        response = requests.get("https://meme-api.herokuapp.com/gimme").json()
        await ctx.send(response['title']+'\n'+response['url'])

    @commands.command(name="insulte")
    async def insult(self, ctx, *names:str):
        """Insulte des gens."""
        if len(names)==0: names=[""]
        url = "http://strategicalblog.com/liste-dinsultes-francaises-pas-trop-vulgaires/"
        for name in names:
            if name.startswith('*'):
                n = int(name[1:]) - 1
                name = oldname
            else:
                n = 1
            for i in range(n):
                await ctx.send(
                    html.unescape(
                        random.choice(
                            re.findall("\n•\t(.*)<br />", requests.get(url).text)
                        )
                    )+" "+name
                )
            oldname = name


    # @commands.command(name="wikipedia2", aliases=["wiki2"], hidden=True)
    # async def wikipedia2(self, ctx, *search_list, n=500, d=5):
    #     """Fais une recherche sur wikipédia."""
    #     languages = ["fr", "en"]
    #     for language in languages:
    #         if search_list[-1][:1] == "/":
    #             n = int(search_list[-1][1:])
    #             search_list = search_list[:-1]
    #         search_list = [search[0].upper()+search[1:] for search in search_list]
    #         search = "_".join(search_list)
    #         resp = requests.get(f"https://{language}.wikipedia.org/wiki/{search}")
    #         parser = html_parser.Parser('div', 'class', 'mw-parser-output', fetched_tags=["p", "li", "a"])
    #         parser.load(resp.text)
    #         lines = parser.result.split('\n')
    #         deleting = ["wiki", "wikti", "ne cite pas suffisamment ses sources", "quelles sources sont attendues ?", "testez votre navigateur"]
    #         new_lines = []
    #         for line in lines:
    #             found = False
    #             for s in deleting:
    #                 if s in line.lower():
    #                     found = True
    #                     break;
    #             if not found and line.strip()!="":
    #                 new_lines.append(line)
    #         parser.result = "\n".join(new_lines)
    #         if len(parser.result):
    #             await ctx.send(parser.result[:n]+"...")
    #             return
    #     await ctx.send(f"La page {search} n'existe pas sur Wikipedia.")
    #     # session = requests.Session()
        # url = "https://fr.wikipedia.org/w/api.php"
        # search = " ".join(search)
        # params = {"action":"query", "format":"json", "list":"search", "srsearch":search}
        # response = session.get(url=url, params=params)
        # data = response.json()
        # cmd = f"Les pages similaires sont:"
        # print(data['query']['search'])
        # cmd += "\n".join([e['title'] for e in data['query']['search'][:d]])
        # await ctx.send(cmd)

    @commands.command(name="uncyclopédie", aliases=["fwiki", "désencyclopédie"])
    async def uncyclopedia(self, ctx, search):
        """Fais une recherche sur désencyclopédie."""
        async with self.bot.channel.typing():
            url = "https://desencyclopedie.org/wiki/"
            html = BeautifulSoup(requests.get(url+search).text, 'html.parser')
            response = ""
            i = 0
            inp = ""
            while len(response)+len(inp)<1000:
                response += inp
                inp += html.body.find(class_='mw-parser-output').find_all('p')[i].text
                i+=1
            await ctx.send(response)


    @commands.command(name="cat-fact")
    async def cat_fact(self, ctx:commands.Context):
        """Donne un fait à propos des chats."""
        url = "https://brianiswu-cat-facts-v1.p.rapidapi.com/facts"
        headers = {
            'x-rapidapi-host': "brianiswu-cat-facts-v1.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7"
            }
        response = requests.request("GET", url, headers=headers)
        msg = random.choice(response.json()['all'])['text']
        await ctx.send(msg)

    @commands.command(name='ip')
    async def ip(self, ctx:commands.Context, ip:str):
        """Donne des informations avec un ip."""
        url = "https://ip-geolocation-ipwhois-io.p.rapidapi.com/json/"
        querystring = {"ip":ip}
        headers = {
            'x-rapidapi-host': "ip-geolocation-ipwhois-io.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7"
            }
        response = requests.request("GET", url, headers=headers, params=querystring)
        embed = discord.Embed(title=f"Informations sur {ip}", color=discord.Color.dark_grey())
        url = response.json()['country_flag']
        print(url)
        embed.set_thumbnail(url=url)
        for k,v in response.json().items():
            embed.add_field(name=str(k), value=str(v) or "aucun")
        await ctx.send(embed=embed)

    # @commands.command(name='who-is')
    # async def who_is(self, ctx:commands.Context, url:str):
    #     """Vérifie l'identité d'un site.
    #     La recherche est possible grâce à l'api:
    #     https://api.domaintools.com/v1/domaintools.com/whois/"
    #     """
    #     base = "https://api.domaintools.com/v1/domaintools.com/whois/"
    #     r = requests.get(base+url)
    #     d = r.json()['response']
    #     embed = discord.Embed(title=d['registrant'], color=discord.Color.dark_orange())
    #     for k,v in d['registration'].items():
    #         embed.add_field(name=str(k), value=str(v) or "aucun")
    #     embed.add_field(name='servers', value='\n'.join(d['name_servers']))
    #     for e in d['whois']['record'].split('\n'):
    #         try:
    #             k, v = e.split(': ')
    #             embed.add_field(name=str(k), value=str(v) or "aucun")
    #         except:
    #             pass
    #     embed.set_footer(text=d['whois']['date'])
    #     await ctx.send(embed=embed)

    @commands.command(name='who-is')
    async def who_is(self, ctx:commands.Context, domain:str):
        """Vérifie l'identité d'un site."""
        url = "https://zozor54-whois-lookup-v1.p.rapidapi.com/"
        querystring = {"format":"json","domain":domain}
        headers = {
            'x-rapidapi-host': "zozor54-whois-lookup-v1.p.rapidapi.com",
            'x-rapidapi-key': "564f5dcf9cmshfb697b99056338ap1ad2efjsn13ec11f2ef5b"
            }
        d = requests.request("GET", url, headers=headers, params=querystring).json()
        embed = discord.Embed(title=d['name'], color=discord.Color.dark_orange())
        for k,v in d.items():
            if k in ['status', 'registrar', 'contacts', 'rawdata', 'whoisserver', 'ask_whois', 'parsedContacts']:
                continue
            if not v:
                continue
            embed.add_field(name=k, value=v)
        if 'owner' in d['contacts']:
            for e in d['contacts']['owner']:
                for k,v in e.items():
                    if not v or k in ['email']:
                        continue            
                    embed.add_field(name=k, value=v)
        await ctx.send(embed=embed)

    @commands.command(name='captcha')
    async def captcha(self, ctx:commands.Context, img:str):
        """Resolveur de captcha."""
        url = "https://metropolis-api-captcha.p.rapidapi.com/solve"
        querystring = {"image":img}
        headers = {
            'x-rapidapi-host': "metropolis-api-captcha.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        msg = response.text
        if 'captcha' in msg:
            msg = response.json()['captcha']
        await ctx.send(msg)

    @commands.command(name='résume', aliases=['résumer', 'summarize', 'sum-up'])
    async def summarize(self, ctx:commands.Context, *, msg:str):
        """Summarize a text or an url."""
        url = "https://text-monkey-summarizer.p.rapidapi.com/nlp/summarize"
        headers = {
            'x-rapidapi-host': "text-monkey-summarizer.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7",
            'content-type': "application/json",
            'accept': "application/json"
            }
        pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        if msg.startswith("http"):
            payload = "{ \"url\": \"" + msg + "\"}"
        else:
            payload = "{ \"text\": \"" + msg + "\"}"
        response = requests.request("POST", url, data=payload, headers=headers)
        d = response.json()
        title = (d['title'] if 'title' in d else 'Résumé')
        footer = (re.search(pattern, d['datePublished']).group() if 'datePublished' in d else 'date inconnue')
        snippets = html.unescape('\n'.join(d['snippets']))
        embed = (discord.Embed(title=title, color=discord.Color.blurple())
        .add_field(name='résumé', value=snippets)
        .set_footer(text=footer)
        )
        await ctx.send(embed=embed)

    @commands.command(name='sentiment')
    async def sentiment(self, ctx:commands.Context, *, msg:str):
        """Analyse les sentiments d'un message."""
        url = "https://microsoft-text-analytics1.p.rapidapi.com/sentiment"
        payload = "{ \"documents\": [  {   \"id\": \"1\",   \"language\": \"fr\",   \"text\": \"" + msg + "\"  } ]}"
        headers = {
            'x-rapidapi-host': "microsoft-text-analytics1.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7",
            'content-type': "application/json",
            'accept': "application/json"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        if 'documents' in response.json():
            msg = response.json()['documents'][0]['sentiment']
        else:
            msg = response.text
        await ctx.send(msg)


    @commands.command(name='synonymes', aliases=['syn'])
    async def synonyms(self, ctx:commands.Context, word:str, lang:str='fr'):
        """Trouve des synonymes."""
        r = requests.get(f'https://wordsimilarity.com/{lang}/{word}')
        syn_pattern = re.compile(f'/{lang}/[^"]+\">([^"]+)</a>')
        synonyms = re.findall(syn_pattern, r.text)
        sim_pattern = re.compile(r"&nbsp;&nbsp;&nbsp;&nbsp;(\d\.\d+)")
        similarities = re.findall(sim_pattern, r.text)
        embed = discord.Embed(title=f"Synonymes de {word}:", color=discord.Color.greyple())
        for k,v in zip(synonyms, similarities):
            embed.add_field(name=k, value=v)
        await ctx.send(embed=embed)        

    @commands.command(name='dns', aliases=['dns-lookup'])
    async def dns(self, ctx:commands.Context, url:str):
        """Effectue une recherche dns par sécurité.
        La recherche est effectuée avec  https://dns.google.com."""
        if not url.startswith("http"):
            url = "http://"+url
        check = f"https://dns.google.com/resolve?name={url}&type=A"
        r = requests.get(check)
        embed = discord.Embed(title=f"Recherche DNS de {url}:", color=0x0000cc)
        embed.add_field(name='check', value=check)
        d = r.json()['Authority'][0]
        for k,v in d.items():
            embed.add_field(name=k, value=v)
        embed.set_footer(text="Recherche effectuée sur https://dns.google.com.")
        await ctx.send(embed=embed)

    @commands.group(name='bible')
    async def bible(self, ctx:commands.Context):
        """Cite la bible."""
    
    @commands.group(name="citation", aliases=['quote'])
    async def quote(self, ctx:commands.Context, language='fr'):
        """Affiche une citation."""
        url = "https://quotes15.p.rapidapi.com/quotes/random/"
        querystring = {"language_code":language}
        headers = {
            'x-rapidapi-host': "quotes15.p.rapidapi.com",
            'x-rapidapi-key': "9f89a4d69emsh51b4e1005159b42p14a115jsn521840e553e7"
        }
        d = requests.request("GET", url, headers=headers, params=querystring).json()


        embed = discord.Embed(title=d['content'],
                              color=discord.Color.orange())
        embed.add_field(name='id', value=d['id'])
        embed.add_field(name='tags', value=html.unescape(' '.join(d['tags'])))
        embed.set_footer(text=f"{d['originator']['name']}, {d['originator']['url']}")
        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(Web(bot))
