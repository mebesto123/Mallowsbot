import discord
from datetime import *
import random
import numpy as np
import pandas as pd
import smtplib

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
        self.distList: np.DataFrame = pd.read_csv(dist_list_path)

    def __sendEmail(self, message: str):
        with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()  # Upgrade the connection to secure TLS/SSL
                server.login(self.email, self.password)
                server.send_message(message)

    async def textUser(message: discord.Message):
         raise NotImplementedError
         
    async def showList(message: discord.Message):
         raise NotImplementedError

    async def addToList(message: discord.Message):
         raise NotImplementedError