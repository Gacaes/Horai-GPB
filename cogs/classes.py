from discord import User
from time import time
from pickle import load, dump




def wsgi():
    from wsgiref.simple_server import make_server, demo_app
    
    with make_server('', 8000, demo_app) as httpd:
        print("Serving HTTP on port 8000...")
    
        # Respond to requests until process is killed
        httpd.serve_forever()

class keep_alive_():
    def __init__(self):
        from multiprocessing import Process
        #proc = Process(target=your_proc_function, args=())
        #proc.start()
        # Terminate the process
        #proc.terminate()  # sends a SIGTERM
            
        #self.p = Process(target=wsgi)
        #self.p.start()

        from flask import Flask
            
        app = Flask('')
        @app.route('/')
        
        def home():
            return "Hello. I am a statue"
        
        def run():
            app.run(host='0.0.0.0',port=8080)
        
        self.p = Process(target=run)
        #self.p.start()

    def kill(self):
        self.p.terminate()
        #stops the webserver so we dont get any weird bugs like it restarts itself or turn itself back on again

class classNotice:
    def __init__(self, data: dict = {}) -> None:
        pass

class classUser:
    def __init__(self, user: User) -> None:
        self.discord: User = user
        self.bumps: int = 0
        self.id = self.discord.id
        self.notices: dict = {}
    
    def notice(self, reason: str = "", channel: int | None = None):
        pass
    def on_message(self):
        pass

class classBumps:
    def __init__(self) -> None:
        self.users: set[classUser] = set()
        self._id_to_user = {}

    def get_users_bumps(self, clear: bool = True) -> list[list[int,int]]:
        array = []
        for user in self.users:
            array.append([user.id,user.bumps])
        if clear:
            self.users.clear()
        return array

class epoch:
    def __init__(self, number: int | float | None = None) -> None:
        self.number = time()//900 if number == None else number
        self.start = self.number * 900
        self.end = (self.number + 1) * 900

class classGuild:
    def __init__(self) -> None:
        pass



if not __name__ == "__main__":
    bumps = classBumps()