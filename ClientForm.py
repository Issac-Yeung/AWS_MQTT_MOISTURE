# -*- coding:utf-8 -*-
import matplotlib.figure as mplfig
import matplotlib.backends.backend_wxagg as mplwx
import random, wx
import time
import threading
import ssl
import paho.mqtt.client as mqtt
import json
# Client windows application

CA_CERTS = "AmazonRootCA1.pem"
CERT_FILE = "AWS-IY-certificate.pem.crt"
KEY_FILE = "AWS-IY-private.pem.key"
HOST = "a30rplcugc3t7k-ats.iot.us-east-1.amazonaws.com"
PORT = 8883
AWS_GET = "$aws/things/Firebeetle/shadow/get"
AWS_ACCEPT = "$aws/things/Firebeetle/shadow/update/accepted"
X_SIZE = 60
class MoistureClient(wx.Frame):
    #Constructor
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Moisture Monitor", size=(1024,768))
        panel = wx.Panel(self)
        self.text = wx.StaticText(parent=panel, label="Disconnect", pos=(480,10))
        self.text.SetForegroundColour(wx.Colour(255,0,0))

        #Raw
        wx.StaticText(parent=panel, label="Raw:", pos=(30,40))
        self.raw = wx.TextCtrl(parent=panel, pos=(100,40), style = wx.TE_READONLY, size=(180,26))

        #Volts
        wx.StaticText(parent=panel, label="Volts:", pos=(330,40))
        self.volts = wx.TextCtrl(parent=panel, pos=(400,40), style = wx.TE_READONLY, size=(180,26))

        #Percent
        wx.StaticText(parent=panel, label="Percent:", pos=(630,40))
        self.percent = wx.TextCtrl(parent=panel, pos=(700,40), style = wx.TE_READONLY, size=(180,26))

        self.btn = wx.Button(parent=panel, label="Close", pos=(900,10))
        self.Bind(wx.EVT_BUTTON, self.BtnClick, self.btn)

        self.figure = mplfig.Figure(figsize=(9.8, 6))
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.31)
        self.canvas = mplwx.FigureCanvasWxAgg(panel, -1, self.figure)
        self.canvas.SetPosition(wx.Point(10, 80)) 

        #self.update_chart([0, 0])
        self.data_queue = []  # Initialize the data queue
        self.max_queue_size = X_SIZE 

        self.thread = threading.Thread(target=self.ReadMoisture)
        self.thread.daemon = True  
        self.thread.start()
    
    def doPublish(self, client):
        while True:
            try:
                payload = json.dumps({}) 
                client.publish(AWS_GET, payload)
                print("Sent empty message")
                time.sleep(10)                
            except Exception as e:
                print("start_period_public Error", e)
                break
    
    # ReadMoisture() - Connect MQTT and read Moisture
    def ReadMoisture(self):
        try:
            client = mqtt.Client()
            def on_connect_closure(client, userdata, flags, rc):
                self.on_connect(client, userdata, flags, rc)
        
            def on_message_closure(client, userdata, msg):
                self.on_message(client, userdata, msg)

            client.on_connect = on_connect_closure
            client.on_message = on_message_closure
            client.tls_set(ca_certs=CA_CERTS,
                            certfile=CERT_FILE,
                            keyfile=KEY_FILE,
                            cert_reqs=ssl.CERT_REQUIRED,
                            tls_version=ssl.PROTOCOL_TLS,
                            ciphers=None)
            client.connect(HOST, PORT, 60)
            print("Connect to AWS MQTT")
            payload = json.dumps({})  #Initialize chart
            pub_thread = threading.Thread(target=self.doPublish, args=(client,))
            pub_thread.daemon = True
            pub_thread.start()
            client.loop_forever()
        except Exception as e:
            wx.MessageBox('Exception',  e, 'Dialog', wx.OK | wx.ICON_ERROR)

    # BtnClick() - Close form
    def BtnClick(self, event):
         self.Close()

    # OnClose() - Destroy form
    def OnClose(self, event):
        self.Destroy()
    
    # on_connect() - Connect MQTT
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code:", rc)
        try:
            if (rc == 0):
                self.text.SetLabel("Connected")
                self.text.SetForegroundColour(wx.Colour(0,255,0))
                client.subscribe(AWS_ACCEPT)
            else:
                self.text.SetLabel("Disconnected")
                self.text.SetForegroundColour(wx.Colour(255,0,0))
        except Exception as e:
            print("on_connect Error: ", e)
    
    # on_message() - Handle Message
    def on_message(self, client, userdata, msg):
        try:
            d = json.loads(msg.payload)
            #print(d)
            #self.datetime.SetValue(d["DateTime"])
            date_str = d["state"]["reported"]["DateTime"]
            value = d["state"]["reported"]["Percent"]
            self.raw.SetValue(str(round(d["state"]["reported"]["Raw"])) + " @ " + date_str)
            self.volts.SetValue(str(round(d["state"]["reported"]["Volts"],3)) + "V @ " + date_str)
            self.percent.SetValue(str(round(d["state"]["reported"]["Percent"],1)) + "% @ " + date_str)
            
            # Update the queue with new data
            if len(self.data_queue) >= self.max_queue_size:
                self.data_queue.pop(0)  # Remove the oldest data point
            self.data_queue.append((date_str, value))
            # Update the chart
            self.update_chart(self.data_queue)
            #print("DateTime: ",d["DateTime"], ",Analog: ",d["Analog"], ",Voltage: ",d["Voltage"])
        except Exception as e:
            print("on_message Error: ", e)
    
    def update_chart(self, data):
        print("Data:" ,data)
        self.axes.clear()  
        self.axes.set_title("Moisture Monitor")

        if data:
            date_strings, values = zip(*data)
        else:
            date_strings, values = [], []

        # Set the x-axis labels and rotate x-axis labels
        self.axes.set_xticks(range(len(date_strings)))
        self.axes.set_xticklabels(date_strings, rotation=90)

        # Plot new data
        if date_strings and values:
            self.axes.plot(range(len(date_strings)), values)  

        # Set axis labels and limits
        self.axes.set_xlabel("Date Time")
        print("Date_strings:", date_strings)
        if date_strings and len(date_strings) > 1:
            self.axes.set_xlim(0, len(date_strings) - 1)
        else:
            self.axes.set_xlim(0, 1)

        # Set y-axis ticks and limits
        self.axes.set_yticks(range(0, 101, 5))
        self.axes.set_ylabel("Percent")
        self.axes.set_ylim(0, 100)

        # Add grid lines
        self.axes.grid(which='major', axis='y', linestyle='-', color='gray', linewidth=0.5)
        self.axes.grid(which='major', axis='x', linestyle='-', color='gray', linewidth=0.5)

        self.canvas.draw()

# Main Entry point
if __name__ == '__main__':
    num = random.randint(1, 100)

    app = wx.App(False)
    frame = MoistureClient()
    frame.Show()
    app.MainLoop()
