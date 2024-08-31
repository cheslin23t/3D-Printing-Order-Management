from flask import render_template, Blueprint, session, redirect, request
from dotenv import load_dotenv
import os
load_dotenv()
import mysql.connector

mydb = mysql.connector.connect(
  host=os.getenv('database_host'),
  user=os.getenv('database_user'),
  password=os.getenv('database_password'),
  database=os.getenv('database_name'),
  port=os.getenv('database_port')
)
