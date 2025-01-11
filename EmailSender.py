import discord
from datetime import *
import random
import numpy as np
import pandas as pd
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import AdminTools

class EmailSender:
     def __init__(self, smtp_server, port, sender_email, sender_password, dist_list_path):
          """
          Initializes the EmailSender instance.

          Parameters:
          - smtp_server (str): The SMTP server address (e.g., 'smtp.gmail.com').
          - port (int): The port to connect to (e.g., 587 for TLS).
          - sender_email (str): The sender's email address.
          - sender_password (str): The sender's email password or app-specific password.
          """
          self.smtp_server = smtp_server
          self.port = port
          self.email = sender_email
          self.password = sender_password
          self.distListPath = dist_list_path

     def __sendEmail(self, message: str, toAddress: str, user: str):
          with smtplib.SMTP(self.smtp_server, self.port) as server:
                    server.starttls()  # Upgrade the connection to secure TLS/SSL
                    server.login(self.email, self.password)
                    server.sendmail(from_addr=self.email, to_addrs=toAddress, msg= "From: %s\nTo: %s\nSubject: %s\n\n%s" % ( self.email, toAddress, "New Poke from " + user, message ))

     def getEmail(self, name: str, guildId):
          df = pd.read_csv(self.distListPath)
          exist = df[(df.Guild == guildId) & (df.Name == name)]

          if exist.index.empty:
               return 'False'
          
          #1234567890123456789
          #2025-01-08 20:25:04.625175
          strTime = df.at[exist.index[0],"Delay"]
          timer = datetime.strptime(strTime[0:19], "%Y-%m-%d %H:%M:%S")
          if timer > datetime.now():
               return 'False'
          
          df.at[exist.index[0],"Delay"] = datetime.now() + timedelta(minutes=20)
          df.to_csv(self.distListPath, index=False)

          return df.at[exist.index[0],"Email"]

     #-email name message 
     async def emailUser(self, message: discord.Message):
          if await AdminTools.checkRole(message.guild ,message.author, "Email User"):
               try:
                    ms = message.content.split('"')
                    name = ms[0].split(" ")[1]
                    text = ms[1]
                    guildId = message.guild.id
                    email = self.getEmail(name, guildId)
                    self.__sendEmail(text, email, message.author.name)
                    
                    await message.channel.send(":white_check_mark: Email to " + name + " was successfully sent!!" )
                    
               except:
                    embed = discord.Embed(
                              color=discord.Color.red())
                    embed.add_field(name="Error",value="Error using command `-email`: parameter should be as followed: `-email name \"message\"`")
                    await message.channel.send(embed=embed)
          else:
               embed = discord.Embed(
                         color=discord.Color.red())
               embed.add_field(name="Error",value=" 🚫 You are not Authorized to use this command. Ask you admin for access 🚫")
               await message.channel.send(embed=embed)
               
     #-showlist     
     async def showList(self, message: discord.Message):
          df: pd.DataFrame = pd.read_csv(self.distListPath)
          embed = discord.Embed(
                    color=discord.Color.blurple())
          embed.add_field(name="List",value="List of users below")
          count = 1
          for item in df:
               embed.add_field(name=count,value="Name: " + item.Name + " Email ")
               count += 1
          await message.channel.send(embed=embed)

     #-addtoemaillist Name email
     async def addToList(self, message: discord.Message):
          ms = message.content.split(" ")
          if len(ms) == 3 :
               name = ms[1]
               email = ms[2]
               email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

               if not re.match(email_regex, email):
                    embed = discord.Embed(
                              color=discord.Color.red())
                    embed.add_field(name="Error",value="Error using command `-addtoemaillist`: Email `" + email + "` is not vaild.")
                    await message.channel.send(embed=embed) 
               else:
                    df: pd.DataFrame = pd.read_csv(self.distListPath)
                    exist = df[(df.Guild == message.guild.id) & (df.Name == name)].index
                    if exist.empty:
                         temp = {"Guild": message.guild.id,"Name": name, "Email": email, "Delay": datetime.now() + timedelta(hours=-1)}
                         df = df.append(temp, ignore_index=True)
                    else: 
                         df.at[exist[0],"Email"] = email
                         df.at[exist[0],"Delay"] = datetime.now() + timedelta(hours=-1)     
                    df.to_csv(self.distListPath, index=False)

                    await message.channel.send(":white_check_mark: " + name + " with email " + email +  " was added!!" )
          else:
               embed = discord.Embed(
                         color=discord.Color.red())
               embed.add_field(name="Error",value="Error using command `-addtoemaillist`: parameter should be as followed: `-addtoemaillist Name email`")
               await message.channel.send(embed=embed)