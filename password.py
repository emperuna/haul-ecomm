from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin, logout_user
from werkzeug.utils import secure_filename
import os
from functools import wraps

hashed_password = generate_password_hash('admin123')
print(hashed_password)