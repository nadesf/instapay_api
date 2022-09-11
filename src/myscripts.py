#============================================"
#           MY OWN FUNCTION
#============================================"

# Génération de code
import string
import random

# Envoie d'email
import smtplib
from email.message import EmailMessage

# Hasher le code pour la double authentification 
import hashlib

def CodeGenerator(size=6, numeric=1):

    code = ""
    all_chars = string.ascii_letters

    if int(numeric): 
        for i in range(int(size)):
            code = code + str(random.randint(0, 9))
    else:
        for i in range(int(size)):
            value = random.randint(0, len(string.ascii_letters))
            code = code + string.ascii_letters[value]

    return code
        
def SendMail(mail_receiver, mail_subject, mail_content):

    # Mes identifiants
    sender = "runbin83@gmail.com"
    password = "xluttkxrgcwwiozu"
    receiver = mail_receiver

    subject = mail_subject
    body = f"""
    
*******************************************************
        INSTAPAY - Solution de Paiement Digital
*******************************************************

{mail_content}


REJOIGNER NOUS MAINTENANT :)
"""

    em = EmailMessage()
    em['From'] = sender
    em['To'] = mail_receiver
    em['Subject'] = subject
    em.set_content(body)

    content = em.as_string()

    try:

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, receiver, content)
        server.close()

        return 1

    except:

        with open("fic.txt", "w") as fic:
            fic.write("Okay Bon !")


def HashSecondAuthenticationCode(code):

    code = code.encode()
    hash_code = hashlib.sha256(code).hexdigest()
    return hash_code