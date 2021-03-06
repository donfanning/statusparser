#!/usr/bin/env python3

import requests
import sys
import concurrent.futures
import socket
import csv
import os
from colorama import Fore, Style

from statusparser_core.configurations import options
# Suppress errors if verify is turned off
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class StatusParserColorMode():
	GREEN = Fore.GREEN # Success
	BLUE = Fore.BLUE # Success but redirected
	CYAN = Fore.CYAN # IP
	RED = Fore.RED # Error
	YELLOW = Fore.YELLOW # Status codes
	MAG = Fore.MAGENTA # Port numbers
	WHITE = Fore.WHITE # Information
	RESET = Style.RESET_ALL # Reset term colors


	def __init__(self):
		self.threads = 20
		self.timeout = 3

	# Simple text report
	def success_txt(self, url, rurl, port, IP, statuscode):
		with open(options().textfile, "a") as f:
			f.write(f"URL: {url}\nRedirect: {rurl}\nPort: {port}\nIP: {IP}\nStatus Code: {statuscode}\n\n")

	# CSV report
	def success_csv(self, url, rurl, port, IP, statuscode):
		if options().csvfile:
			if not options().csvfile.endswith(".csv"):
				csvfile = f"{options().csvfile}.csv"
			else:
				csvfile = options().csvfile

			if os.path.isfile(csvfile):
				pass
			else:
				with open(csvfile, "w") as csvf:
					writer = csv.writer(csvf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
					writer.writerow(["URL", "REDIRECT", "PORT", "IP", "STATUS CODE"])

		with open(csvfile, "a") as csvf:
			writer = csv.writer(csvf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerow([url, rurl, port, IP, statuscode])

	def errors(self, url, rurl, status):
		with open(options().errorfile, "a") as ef:
			ef.write(f"URL: {url}\nRedirect: {rurl}\nStatus: {status}\n\n")

	def parser(self):
		with open(options().file, "r") as f:
			# If URL has invalid characterrs in it, replace
			urls = [url.strip("\n").replace("__", "://").replace("_", ".").replace("*.", "http://") for url in f] # took out + /
			urls = [url for url in urls if not url.startswith("#")]
			# If url does not start with http://
			#urls = [f"http://{url}" for url in urls if not url.startswith("http")]

			# Let user choose threads, else use default of 20
			if options().threads:
				threads = options().threads

			else:
				threads = self.threads

			# Start thread pool
			with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
				for _ in executor.map(self.url_responses, urls):
					pass

	def url_responses(self, url):

		# If user specifies a different timeout option, else use default of 3
		if options().timeout:
			timeout = options().timeout
		else:
			timeout = self.timeout

		try:
			# Use a default header
			headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
			# Make request
			response = requests.head(url, allow_redirects=True, verify=False, timeout=timeout, stream=True, headers=headers)
			# Grab URL. This will also grab the redirected URL
			rurl = response.url
			# Grab IP number of URL
			IP = str(response.raw._connection.sock.getpeername()[0])
			# Grab port number requests made connection on
			port = str(response.raw._connection.sock.getpeername()[1])
			# Grab status code information
			status_code = response.status_code

			# if url was redirected
			if url != rurl:
				if options().statuscode:
					if status_code in options().statuscode:
						print(f"URL:{self.BLUE} {url}\n{self.WHITE}Redirect:{self.GREEN} {rurl}\n{self.WHITE}Port:{self.MAG} {port}\n{self.WHITE}IP:{self.CYAN} {IP}\n{self.WHITE}Status Code:{self.YELLOW} {status_code}{self.RESET}\n")
					else:
						pass

				elif not options().statuscode:
					print(f"URL:{self.BLUE} {url}\n{self.WHITE}Redirect:{self.GREEN} {rurl}\n{self.WHITE}Port:{self.MAG} {port}\n{self.WHITE}IP:{self.CYAN} {IP}\n{self.WHITE}Status Code:{self.YELLOW} {status_code}{self.RESET}\n")


				if options().textfile:
					if options().statuscode:
						if status_code in options().statuscode:
							self.success_txt(url=url, rurl=rurl, port=port, IP=IP, statuscode=status_code)
						else:
							pass
					elif not options().statuscode:
						self.success_txt(url=url, rurl=rurl, port=port, IP=IP, statuscode=status_code)

				if options().csvfile:
					if options().statuscode:
						if status_code in options().statuscode:
							self.success_csv(url=url, rurl=rurl, port=port, IP=IP, statuscode=status_code)
						else:
							pass
					elif not options().statuscode:
						self.success_csv(url=url, rurl=rurl, port=port, IP=IP, statuscode=status_code)

			# If url never redirected
			elif url == url:
				if options().statuscode:
					if status_code in options().statuscode:
						print(f"{self.white}URL:{self.GREEN} {url}\n{self.white}Port: {self.MAG} {port}\n{self.WHITE}IP:{self.CYAN} {IP}\n{self.white}Status Code:{self.YELLOW} {status_code}{self.RESET}\n")
					else:
						pass

				elif not options().statuscode:
					print(f"{self.white}URL:{self.GREEN} {url}\n{self.white}Port:{self.MAG} {port}\n{self.WHITE}IP:{self.CYAN} {IP}\n{self.white}Status Code:{self.YELLOW} {status_code}{self.RESET}\n")

				if options().textfile:
					if options().statuscode:
						if status_code in options().statuscode:
							self.success_txt(url=url, rurl=rurl, port=port, IP=IP, statuscode=status_code)
						else:
							pass
					elif not options().statuscode:
						self.success_txt(url=url, rurl=rurl, port=port, IP=IP, statuscode=status_code)

				if options().csvfile:
					if options().statuscode:
						if status_code in options().statuscode:
							self.success_csv(url=url, rurl=rurl, port=port, IP=IP, statuscode=status_code)
						else:
							pass
					elif not options().statuscode:
						self.success_csv(url=url, rurl=rurl, port=port, IP=IP, statuscode=status_code)

		# Connection Errors
		except requests.ConnectionError:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}Connection Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="Connection Error")

		# Invalid URL Errors
		except socket.gaierror:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}GAI Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="GAI Error")

		except requests.exceptions.InvalidURL:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}Invalid URL Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="Invalid URL Error")

		except requests.exceptions.MissingSchema:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}Invalid URL Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="Invalid URL Error")

		# Timeout Errors
		except socket.timeout:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}Timeout Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="Timeout Error")

		except requests.exceptions.ReadTimeout:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}Read Timeout Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="Read Timeout Error")

		# Redirect Errors
		except requests.exceptions.TooManyRedirects:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}Too Many Redirects Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="Too Many Redirects Error")

		# MISC Errors
		except TypeError:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}Type Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="Type Error")

		except UnicodeError:
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.RED} {url}\n{self.WHITE}Status:{self.RED}Unicode Error{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=None, status="Unicode Error")

		except AttributeError:
			# Although status code probability is most likely 200. The status code is still an undetermined error. For that, if noerror mode is enabled, pass.
			if options().noerrors:
				pass

			elif not options().noerrors:
				print(f"{self.WHITE}URL:{self.GREEN} {url}\n{self.WHITE}Redirect:{self.BLUE} {rurl}\n{self.WHITE}Status Code:{self.RED} Undetermined\n{self.WHITE}Status Code Probability:{self.YELLOW} 200{self.RESET}\n")
				pass

			if options().errorfile:
				self.errors(url=url, rurl=rurl, status="Undetermined\nStaus Code Probability: 200")

		# If user cancels program
		except KeyboardInterrupt:
			sys.exit(0)
