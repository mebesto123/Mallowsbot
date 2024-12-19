import discord
from datetime import *
import random
import numpy as np
import pandas as pd
import smtplib
import re

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

    def __sendEmail(self, message: str):
        with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()  # Upgrade the connection to secure TLS/SSL
                server.login(self.email, self.password)
                server.send_message(message)
     #-email 
    async def emailUser(self, message: discord.Message):
          ms = message.content.split(" ")
          if len(ms) > 3:
               name = ms[1]
               
    #-showlist     
    async def showList(self, message: discord.Message):
          df: pd.DataFrame = pd.read_csv(self.distListPath)
          embed = discord.Embed(
                    #title="Command Error",
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
          if len(ms) > 3 :
               name = ms[1]
               email = ms[2]
               email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

               if re.match(email_regex, email):
                    embed = discord.Embed(
                              #title="Command Error",
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
                         #title="Command Error",
                         color=discord.Color.red())
               embed.add_field(name="Error",value="Error using command `-addtoemaillist`: parameter should be as followed: `-addtoemaillist Name email`")
               await message.channel.send(embed=embed)