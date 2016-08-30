import cgi
import discord
from discord.ext import commands
import http.server
import threading
import multiprocessing

bot = None

serverPage = ""
with open('serverpage.html', 'r') as myfile:
    serverPage=myfile.read()
    
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        pathArr = self.path.split("/")
        if pathArr[1] == "Servers":
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            server = discord.utils.get(bot.servers, id=pathArr[2])
            onlineMembers = 0
            for member in server.members:
                if str(member.status)!="offline":
                    onlineMembers += 1
            self.wfile.write((serverPage.format(server.name,server.id,len(server.members),onlineMembers)).encode("utf-8"))
        return

def run(server_class=http.server.HTTPServer, handler_class=http.server.BaseHTTPRequestHandler):
    server_address = ('0.0.0.0', 8080)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
        
class ServerPage():
    
    def __init__(self, client):
        self.client = client
        
        thread = multiprocessing.Process(target = run, args = (http.server.HTTPServer, Handler))
        thread.start()
    
    @commands.command(pass_context = True)
    async def serverstats(self, ctx):
        await self.client.say("View this servers stats here: http://tessbot.octl.xyz:8080/Servers/{} ".format(ctx.message.server.id))
        
def setup(client):
    global bot
    bot = client
    client.add_cog(ServerPage(client))