from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/hello")
        self.client.get("/world")

class UserBehavior(TaskSet):
    statements = [
        'Hello', 
        'How are you?', 
        'This chat is nice',
    ]
    
    def on_start(self):
        uri = "wss://YOUR_WS_URL_HERE:443/chat/user" + str(uuid4().hex)
        self.ws = create_connection(uri)
        self.ws.send(str(uuid4().hex))
        
    def on_quit(self):
        self.ws.disconnect()