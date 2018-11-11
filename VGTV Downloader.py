from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import *
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import requests
import re
import json
import sys
import argparse

from tqdm import tqdm

chunk_size = 1024

API = "http://svp.vg.no/svp/api/v1/vgtv/assets/{0}?appName=vgtv-website"

class Window(Frame):
    def __init__ (self, master=None):
        Frame.__init__ (self,master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("VGTV Downloader")
        url_label=Label(root,text="Video URL:")
        global url_entry
        url_entry=Entry(root)
        download_button=Button(root,text="Download", command=main)
        url_label.grid(row=0, column=0)
        url_entry.grid(row=0, column=1)
        download_button.grid(row=0, column=2)
	
def validateURL(url):
	"""
	Validate the given url
	:param url: URL to the VGTV or VG page with the video
	:type url: str
	"""

	vgtv = "vgtv"
	vg = "vg"
	
	if vgtv in url:
		return "valid", vgtv

	elif vg in url:
		return "valid", vg

	else:
		return "not valid"

	
def download(fileURL, title, fname):

    try:
        #print("\033[92mDownloading:\033[0m", title)

        r = requests.get(fileURL, stream = True)
        total_size = int(r.headers['content-length'])
			
		# I found this progress bar thing on youtube. I like it :)
		# https://www.youtube.com/watch?v=Xhw2l-hzoKk
		
        saveFile = saveLocation + "/" + fname
		
        print(saveFile.encode("utf-8"))
		
        with open(saveFile, 'wb') as f:
            for data in tqdm(iterable = r.iter_content(chunk_size = chunk_size), total = total_size/chunk_size, unit = 'KB'):
                f.write(data)

            #print("\033[92mDownloaded:\033[0m", saveLocation)

    except Exception:
        messagebox.showinfo('Error','The url is invalid, or this video can not be downloaded')
		
def getdata(url, method):

	if method == "vgtv":
		videoID = re.findall('vgtv.no\/video\/(\d+)', url)[0]

		r = requests.get(API.format(videoID))
		
		data = json.loads(r.text)
		
		title = data["title"]
		fileURL = data["streamUrls"]["mp4"]
		fname = title.replace(" ", "_") + ".mp4"

		download(fileURL=fileURL, title=title, fname=fname)	
    
    # when method is vg
	else:
		r = requests.get(url)
		html = r.text

		fileURL = re.findall('pseudostreaming"(.*?)",', html)[0]
		fileURL = fileURL.replace(':["', '')
		fileURL = fileURL.replace("\\u002F", "/")

		title = re.findall('headline":"(.*?)",', html)[0]
		fname = title.replace(" ", "_") + ".mp4"
		
		download(fileURL=fileURL, title=title, fname=fname)
		
def main():
    # These are used for testing
    #url = "https://www.vgtv.no/video/164927/skal-lande-blir-tatt-av-stormen"
    #url = "https://www.vg.no/nyheter/innenriks/i/7lOwEV/nrk-politikere-bedt-om-aa-bytte-mobil-etter-spionmistanke"
	
    global saveLocation

    url = url_entry.get()
    
    is_valid = validateURL(url)

    if is_valid[0] == "valid":
    	if is_valid[1] == "vgtv":
    		saveLocation = filedialog.askdirectory()
    		getdata(url, method="vgtv")
    	
    	else:
    		saveLocation = filedialog.askdirectory()
    		getdata(url, method="vg")
    		
    else:
    	messagebox.showinfo('Error','Invalid URL')
    	sys.exit()
		

root= Tk()
root.geometry("253x27")
app = Window(root)
root.mainloop()